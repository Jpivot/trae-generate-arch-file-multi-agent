#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React模式智能体基类
实现思考-行动-观察的循环机制
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .base_agent import BaseAgent, AgentMessage
from ..services.llm_service import LLMService

class ActionType(Enum):
    """行动类型枚举"""
    THINK = "think"
    SEARCH = "search"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    FINISH = "finish"

@dataclass
class ReactStep:
    """React步骤数据类"""
    step_type: ActionType
    thought: str
    action: str
    observation: str
    result: Optional[Any] = None

class ReactAgent(BaseAgent):
    """React模式智能体基类"""
    
    def __init__(self, name: str, config: Dict[str, Any], llm_service: LLMService, 
                 section_type: str, max_steps: int = 10):
        super().__init__(name, config)
        self.llm_service = llm_service
        self.section_type = section_type
        self.dependencies = config.get('dependencies', [])
        self.max_steps = max_steps
        self.react_steps: List[ReactStep] = []
        self.tools = self._initialize_tools()
        self.context = {}
        self.final_result = None
        self.prompt_templates = self._load_prompt_templates()
        
    @abstractmethod
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化可用工具（子类实现）"""
        pass
    
    @abstractmethod
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板（子类实现）"""
        pass
    
    # 基础工具方法，供子类使用
    async def _base_tool_think(self, thought: str) -> str:
        """基础思考工具"""
        self.logger.info(f"[{self.name}] 执行思考工具，思考内容: {thought[:50]}...")
        result = f"思考结果: {thought}"
        return result
    
    async def _base_tool_search_context(self, query: str) -> str:
        """基础上下文搜索工具"""
        self.logger.info(f"[{self.name}] 执行上下文搜索，查询: {query}")
        # 在共享上下文中搜索相关信息
        relevant_info = []
        for key, value in self.context.items():
            if query.lower() in str(value).lower():
                relevant_info.append(f"{key}: {value}")
        
        if relevant_info:
            result = "\n".join(relevant_info)
            self.logger.info(f"[{self.name}] 找到{len(relevant_info)}条相关信息")
        else:
            result = f"未找到与'{query}'相关的上下文信息"
            self.logger.info(f"[{self.name}] 未找到相关上下文信息")
        return result
    
    async def _base_tool_generate_content(self, requirements: str) -> str:
        """基础内容生成工具"""
        self.logger.info(f"[{self.name}] 执行内容生成工具，需求: {requirements[:50]}...")
        
        template = self.prompt_templates.get('content_generation',
            """根据以下要求生成{section_type}章节内容：
            
            要求：{requirements}
            
            上下文信息：{context}
            
            请生成详细的内容。""")
        
        prompt = template.format(
            section_type=self.section_type,
            requirements=requirements,
            context=json.dumps(self.context, ensure_ascii=False, indent=2)
        )
        
        self.logger.info(f"[{self.name}] 发送内容生成提示给LLM，提示长度: {len(prompt)}")
        response = await self.llm_service.generate_text(prompt)
        self.logger.info(f"[{self.name}] LLM内容生成响应长度: {len(response.content)}")
        return response.content
    
    # 原有的工具方法已移除，由子类实现具体工具
    
    @abstractmethod
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        """构建生成提示词（子类实现）"""
        pass
    
    async def react_process(self, input_data: Dict[str, Any]) -> str:
        """React处理流程"""
        self.context.update(input_data)
        self.react_steps.clear()
        
        self.logger.info(f"[{self.name}] 开始React处理流程，输入数据: {json.dumps(input_data, ensure_ascii=False)[:200]}...")
        
        # 初始思考
        initial_thought = await self._initial_thinking(input_data)
        self.logger.info(f"[{self.name}] 初始思考完成: {initial_thought[:100]}...")
        
        for step in range(self.max_steps):
            try:
                self.logger.info(f"[{self.name}] 开始第{step}步React循环")
                
                # 思考阶段
                thought = await self._think_step(step, initial_thought if step == 0 else None)
                self.logger.info(f"[{self.name}] 思考阶段完成: {thought[:100]}...")
                
                # 行动阶段
                action, action_input = await self._action_step(thought)
                self.logger.info(f"[{self.name}] 行动阶段完成: action={action}, input={action_input[:50]}...")
                
                # 观察阶段
                observation = await self._observation_step(action, action_input)
                self.logger.info(f"[{self.name}] 观察阶段完成: {observation[:100]}...")
                
                # 记录步骤 - 处理自定义工具名称
                try:
                    step_type = ActionType(action)
                except ValueError:
                    # 如果不是标准ActionType，使用GENERATE作为默认类型
                    step_type = ActionType.GENERATE
                
                react_step = ReactStep(
                    step_type=step_type,
                    thought=thought,
                    action=f"{action}({action_input})",
                    observation=observation
                )
                self.react_steps.append(react_step)
                
                # 检查是否完成 - 多种退出条件
                if (action == ActionType.FINISH.value or 
                    action == "finish" or 
                    action == "generate_content" and len(observation) > 100 or
                    "完成" in observation or "生成完毕" in observation):
                    self.final_result = observation
                    self.logger.info(f"[{self.name}] React流程完成，退出条件: action={action}")
                    break
                    
            except Exception as e:
                self.logger.error(f"[{self.name}] React step {step} failed: {e}")
                break
        
        # 如果没有明确的结果，尝试从最后一步获取
        if not self.final_result and self.react_steps:
            last_step = self.react_steps[-1]
            if "generate_content" in last_step.action:
                self.final_result = last_step.observation
                self.logger.info(f"[{self.name}] 使用最后一步的生成内容作为结果")
        
        result = self.final_result or "生成失败"
        self.logger.info(f"[{self.name}] React处理流程结束，结果长度: {len(result)}")
        return result
    
    async def _initial_thinking(self, input_data: Dict[str, Any]) -> str:
        """初始思考"""
        # 使用专门的初始思考提示词模板
        template = self.prompt_templates.get('initial_thinking', 
            """我需要为{section_type}章节生成内容。
            
            输入信息：
            {input_data}
            
            我需要思考：
            1. 这个章节的主要目标是什么？
            2. 需要哪些信息来完成这个章节？
            3. 应该采用什么样的生成策略？
            
            请给出初始思考结果。""")
        
        thinking_prompt = template.format(
            section_type=self.section_type,
            input_data=json.dumps(input_data, ensure_ascii=False, indent=2)
        )
        
        self.logger.info(f"[{self.name}] 发送初始思考提示给LLM，提示长度: {len(thinking_prompt)}")
        response = await self.llm_service.generate_text(thinking_prompt)
        self.logger.info(f"[{self.name}] LLM初始思考响应长度: {len(response.content)}")
        return response.content
    
    async def _think_step(self, step: int, initial_thought: Optional[str] = None) -> str:
        """思考步骤"""
        if initial_thought:
            self.logger.info(f"[{self.name}] 使用初始思考结果")
            return initial_thought
            
        # 基于当前状态和历史步骤进行思考
        context_info = "\n".join([f"步骤{i}: {s.thought} -> {s.action} -> {s.observation}" 
                                 for i, s in enumerate(self.react_steps)])
        
        template = self.prompt_templates.get('thinking_step',
            """当前进行到第{step}步，之前的步骤：
            {context_info}
            
            当前上下文：
            {context}
            
            我需要思考下一步应该做什么来完成{section_type}章节的生成。""")
        
        thinking_prompt = template.format(
            step=step,
            context_info=context_info,
            context=json.dumps(self.context, ensure_ascii=False, indent=2),
            section_type=self.section_type
        )
        
        self.logger.info(f"[{self.name}] 发送第{step}步思考提示给LLM，提示长度: {len(thinking_prompt)}")
        response = await self.llm_service.generate_text(thinking_prompt)
        self.logger.info(f"[{self.name}] LLM第{step}步思考响应长度: {len(response.content)}")
        return response.content
    
    async def _action_step(self, thought: str) -> Tuple[str, str]:
        """行动步骤"""
        action_prompt = f"""
        基于以下思考：
        {thought}
        
        可用的工具：
        {list(self.tools.keys())}
        
        请选择一个工具并提供输入参数。如果已经有足够信息生成内容，请选择generate_content工具。
        
        格式：工具名称|参数
        例如：think|我需要分析技术栈
        例如：generate_content|根据已有信息生成章节内容
        例如：finish|内容生成完成
        
        请严格按照"工具名称|参数"的格式回答，不要添加其他内容。
        """
        
        self.logger.info(f"[{self.name}] 发送动作选择提示给LLM")
        response = await self.llm_service.generate_text(action_prompt)
        action_line = response.content.strip()
        self.logger.info(f"[{self.name}] LLM返回动作: {action_line}")
        
        # 尝试多种解析方式
        if '|' in action_line:
            action, action_input = action_line.split('|', 1)
            action = action.strip()
            action_input = action_input.strip()
        else:
            # 如果没有|分隔符，尝试其他格式
            lines = action_line.split('\n')
            first_line = lines[0].strip()
            
            if ':' in first_line:
                parts = first_line.split(':', 1)
                action = parts[0].strip()
                action_input = parts[1].strip() if len(parts) > 1 else ""
            elif any(tool in first_line for tool in self.tools.keys()):
                # 如果包含工具名称，提取工具名称
                for tool_name in self.tools.keys():
                    if tool_name in first_line:
                        action = tool_name
                        action_input = first_line.replace(tool_name, "").strip()
                        break
                else:
                    action = "think"
                    action_input = action_line
            else:
                action = "think"
                action_input = action_line
        
        # 确保动作名称有效
        if action not in self.tools:
            self.logger.warning(f"[{self.name}] 无效动作'{action}'，使用默认动作'think'")
            action = "think"
        
        self.logger.info(f"[{self.name}] 解析后的动作: action={action}, input={action_input[:50]}...")
        return action, action_input
    
    async def _observation_step(self, action: str, action_input: str) -> str:
        """观察步骤"""
        self.logger.info(f"[{self.name}] 执行工具: {action}，参数: {action_input[:50]}...")
        
        if action in self.tools:
            try:
                result = await self.tools[action](action_input)
                result_str = str(result)
                self.logger.info(f"[{self.name}] 工具'{action}'执行成功，结果长度: {len(result_str)}")
                self.logger.debug(f"[{self.name}] 工具'{action}'执行结果: {result_str[:200]}...")
                return result_str
            except Exception as e:
                error_msg = f"工具执行失败: {e}"
                self.logger.error(f"[{self.name}] 工具'{action}'执行失败: {e}")
                return error_msg
        else:
            error_msg = f"未知工具: {action}"
            self.logger.warning(f"[{self.name}] {error_msg}")
            return error_msg
    
    async def generate_content(self, input_data: Dict[str, Any]) -> str:
        """生成内容（实现基类方法）"""
        return await self.react_process(input_data)
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理消息（实现基类方法）"""
        if message.message_type == "generate_request":
            try:
                # 解析消息内容
                if hasattr(message, 'data') and message.data:
                    input_data = message.data
                elif message.content:
                    try:
                        input_data = json.loads(message.content)
                    except json.JSONDecodeError:
                        input_data = {"requirements": message.content}
                else:
                    input_data = {}
                
                content = await self.generate_content(input_data)
                return AgentMessage(
                    sender=self.name,
                    receiver=message.sender,
                    message_type="generation_completed",
                    content=json.dumps({"content": content, "section_type": self.section_type}),
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id
                )
            except Exception as e:
                self.logger.error(f"Content generation failed: {e}")
                return AgentMessage(
                    sender=self.name,
                    receiver=message.sender,
                    message_type="generation_error",
                    content=json.dumps({"error": str(e), "section_type": self.section_type}),
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id
                )
        
        elif message.message_type == "context_update":
            if hasattr(message, 'data') and message.data:
                self.context.update(message.data)
            elif message.content:
                try:
                    context_data = json.loads(message.content)
                    self.context.update(context_data)
                except json.JSONDecodeError:
                    pass
            return None
            
        return None
    
    def get_react_history(self) -> List[Dict[str, Any]]:
        """获取React历史记录"""
        return [
            {
                "step_type": step.step_type.value,
                "thought": step.thought,
                "action": step.action,
                "observation": step.observation
            }
            for step in self.react_steps
        ]
    
    def reset_react_state(self):
        """重置React状态"""
        self.react_steps.clear()
        self.context.clear()
        self.final_result = None