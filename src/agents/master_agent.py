import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Template

from .base_agent import BaseAgent, AgentMessage
from .react_section_agents import create_react_agents
from ..services.llm_service import LLMService
from ..services.external_api_service import ExternalAPIService

class MasterAgent(BaseAgent):
    """主智能体，负责协调各个React模式章节智能体，生成完整的架构设计文档"""
    
    def __init__(self, name: str, config: Dict[str, Any], llm_service: LLMService):
        super().__init__(name, config)
        self.llm_service = llm_service
        self.section_agents = {}
        self.external_api_service = None
        self.generation_tasks: Dict[str, asyncio.Task] = {}
        self.section_results: Dict[str, str] = {}
        self.input_data: Dict[str, Any] = {}
        self.document_template = self._load_document_template()
        self.generation_status = {}
        self._initialize_react_agents()
        
    def _load_document_template(self) -> str:
        """加载文档模板"""
        try:
            template_path = Path("templates/document_template.md")
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.logger.warning("Document template not found, using default")
                return self._get_default_template()
        except Exception as e:
            self.logger.error(f"Error loading document template: {e}")
            return self._get_default_template()
            
    def _initialize_react_agents(self):
        """初始化React模式章节智能体"""
        self.section_agents = create_react_agents(self.llm_service, self.config)
        for section_type in self.section_agents.keys():
            self.generation_status[section_type] = 'pending'
            
    def _get_default_template(self) -> str:
        """获取默认文档模板"""
        return """
# {{ project_name }} 架构设计文档

# 1. 简介
## 1.1. 项目背景
{{ project_background }}

## 1.2. 统一术语
{{ unified_terminology }}

# 2. 总体设计思路概述
## 2.1. 技术栈选型
{{ tech_stack_selection }}

## 2.2. 应用架构总体设计思路
{{ app_architecture_overview }}

## 2.3. 系统架构总体设计思路
{{ system_architecture_overview }}

# 3. 应用架构总体设计
## 3.1. 模块划分
{{ module_division }}

## 3.2. 微服务划分
{{ microservice_division }}

### 3.2.1. 微服务代码结构
{{ microservice_code_structure }}

## 3.3. 对下游系统的影响
{{ downstream_impact }}

# 4. 系统架构总体设计
## 4.1. 微服务部署策略设计
{{ microservice_deployment }}

## 4.2. 数据库部署策略设计
{{ database_deployment }}

## 4.3. 云服务选型及架构设计
{{ cloud_service_design }}

## 4.4. 外部系统依赖
{{ external_dependencies }}

---
*文档生成时间: {{ generation_time }}*
*技术栈: {{ tech_stack }}*
"""

    def add_section_agent(self, section_type: str, agent):
        """添加章节智能体"""
        self.section_agents[section_type] = agent
        self.generation_status[section_type] = 'pending'
        self.logger.info(f"Added section agent: {section_type}")
        
    async def start(self):
        """启动主智能体"""
        await super().start()
        
        # 启动所有章节智能体
        for agent in self.section_agents.values():
            await agent.start()
            
        # 初始化外部API服务
        api_config = self.config.get('external_apis', {})
        self.external_api_service = ExternalAPIService(api_config)
        
        self.logger.info("Master agent and all section agents started")
        
    async def stop(self):
        """停止主智能体"""
        # 停止所有章节智能体
        for agent in self.section_agents.values():
            await agent.stop()
            
        # 取消所有生成任务
        for task in self.generation_tasks.values():
            if not task.done():
                task.cancel()
                
        await super().stop()
        self.logger.info("Master agent and all section agents stopped")
        
    async def handle_message(self, message: AgentMessage):
        """处理消息"""
        try:
            if message.message_type == "generation_completed":
                await self._handle_generation_completed(message)
            elif message.message_type == "generation_error":
                await self._handle_generation_error(message)
            else:
                self.logger.warning(f"Unknown message type: {message.message_type}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            
    async def _handle_generation_completed(self, message: AgentMessage):
        """处理生成完成消息"""
        try:
            result = json.loads(message.content)
            section_type = result['section_type']
            content = result['content']
            
            self.section_results[section_type] = content
            self.generation_status[section_type] = 'completed'
            
            self.logger.info(f"Section {section_type} generation completed")
            
            # 通知依赖此章节的其他智能体
            await self._notify_dependent_agents(section_type, content)
            
        except Exception as e:
            self.logger.error(f"Error handling generation completed: {e}")
            
    async def _handle_generation_error(self, message: AgentMessage):
        """处理生成错误消息"""
        try:
            result = json.loads(message.content)
            section_type = result['section_type']
            error = result['error']
            
            self.generation_status[section_type] = 'error'
            self.logger.error(f"Section {section_type} generation failed: {error}")
            
        except Exception as e:
            self.logger.error(f"Error handling generation error: {e}")
            
    async def _notify_dependent_agents(self, section_type: str, content: str):
        """通知依赖此章节的智能体"""
        for agent in self.section_agents.values():
            if section_type in agent.dependencies:
                dependency_message = {
                    "dependency_name": section_type,
                    "content": content
                }
                
                await agent.receive_message(AgentMessage(
                    sender=self.name,
                    receiver=agent.name,
                    content=json.dumps(dependency_message),
                    message_type="dependency_ready",
                    timestamp=datetime.now()
                ))
                
    async def generate_architecture_document(self, input_data: Dict[str, Any]) -> str:
        """生成架构设计文档"""
        try:
            self.input_data = input_data
            self.logger.info("Starting architecture document generation")
            
            # 1. 预处理输入数据
            processed_data = await self._preprocess_input_data(input_data)
            
            # 2. 获取外部系统信息（用于上下游章节）
            external_systems = await self._fetch_external_systems_info()
            processed_data.update(external_systems)
            
            # 3. 设置共享上下文
            await self._set_shared_context(processed_data)
            
            # 4. 并行生成各章节内容
            await self._generate_sections_parallel(processed_data)
            
            # 5. 等待所有章节完成
            await self._wait_for_all_sections()
            
            # 6. 整合最终文档
            final_document = await self._integrate_final_document()
            
            self.logger.info("Architecture document generation completed")
            return final_document
            
        except Exception as e:
            self.logger.error(f"Error generating architecture document: {e}")
            raise
            
    async def generate_document(self, input_data: Dict[str, Any]) -> str:
        """生成完整的架构设计文档（兼容旧接口）"""
        return await self.generate_architecture_document(input_data)
        
    async def _generate_section_with_retry(self, agent, input_data: Dict[str, Any], section_type: str, max_retries: int = 3) -> str:
        """带重试机制的章节生成"""
        for attempt in range(max_retries):
            try:
                # 发送生成请求给React智能体
                request_id = str(uuid.uuid4())
                message = AgentMessage(
                    sender=self.name,
                    receiver=agent.name,
                    content=json.dumps(input_data),
                    message_type="generate_request",
                    timestamp=datetime.now(),
                    correlation_id=request_id
                )
                
                await agent.receive_message(message)
                
                # 等待生成完成
                timeout = 60.0  # 60秒超时
                start_time = asyncio.get_event_loop().time()
                
                while section_type not in self.section_results:
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        raise asyncio.TimeoutError(f"Section {section_type} generation timeout")
                    await asyncio.sleep(0.5)
                
                return self.section_results[section_type]
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for section {section_type}: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
                
        raise Exception(f"Failed to generate section {section_type} after {max_retries} attempts")
            
    async def _preprocess_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理输入数据"""
        processed_data = input_data.copy()
        
        # 处理技术栈信息（主智能体直接处理，不需要子智能体生成）
        tech_stack = input_data.get('tech_stack', {})
        if isinstance(tech_stack, dict):
            tech_stack_str = self._format_tech_stack(tech_stack)
            processed_data['tech_stack_formatted'] = tech_stack_str
            
        # 添加项目名称（如果没有提供）
        if 'project_name' not in processed_data:
            processed_data['project_name'] = input_data.get('system_description', '未命名项目')[:20]
            
        return processed_data
        
    def _format_tech_stack(self, tech_stack: Dict[str, Any]) -> str:
        """格式化技术栈信息"""
        formatted = []
        for category, technologies in tech_stack.items():
            if isinstance(technologies, list):
                tech_list = ', '.join(technologies)
            else:
                tech_list = str(technologies)
            formatted.append(f"**{category}**: {tech_list}")
        return '\n'.join(formatted)
        
    async def _fetch_external_systems_info(self) -> Dict[str, Any]:
        """获取外部系统信息"""
        external_info = {'external_systems': 'pay'}
        
        # try:
        #     async with self.external_api_service as api_service:
        #         # 获取上游系统信息
        #         system_id = self.input_data.get('system_id', 'default')
        #         upstream_systems = await api_service.get_upstream_systems(system_id)
        #         downstream_systems = await api_service.get_downstream_systems(system_id)
        #         api_specs = await api_service.get_api_specifications(system_id)
        #
        #         external_info.update({
        #             'upstream_systems': upstream_systems,
        #             'downstream_systems': downstream_systems,
        #             'api_specifications': api_specs
        #         })
        #
        # except Exception as e:
        #     self.logger.error(f"Error fetching external systems info: {e}")
        #     # 使用默认值
        #     external_info = {
        #         'upstream_systems': [],
        #         'downstream_systems': [],
        #         'api_specifications': {}
        #     }
            
        return external_info
        
    async def _set_shared_context(self, processed_data: Dict[str, Any]):
        """设置共享上下文"""
        for agent in self.section_agents.values():
            agent.set_shared_context(processed_data)
            
    async def _generate_sections_parallel(self, processed_data: Dict[str, Any]):
        """并行生成章节内容"""
        # 确定生成顺序（考虑依赖关系）
        generation_order = self._determine_generation_order()
        
        # 分批并行生成
        for batch in generation_order:
            tasks = []
            for section_type in batch:
                if section_type in self.section_agents:
                    task = self._generate_section(section_type, processed_data)
                    tasks.append(task)
                    self.generation_tasks[section_type] = task
                    
            # 等待当前批次完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
    def _determine_generation_order(self) -> List[List[str]]:
        """确定生成顺序（考虑依赖关系）"""
        # 简化实现：按依赖关系分批
        # 第一批：无依赖的章节
        # 第二批：依赖第一批的章节
        # 以此类推
        
        all_sections = set(self.section_agents.keys())
        ordered_batches = []
        remaining_sections = all_sections.copy()
        
        while remaining_sections:
            current_batch = []
            
            for section in list(remaining_sections):
                agent = self.section_agents[section]
                dependencies = set(agent.dependencies)
                
                # 检查依赖是否已在之前的批次中
                completed_sections = all_sections - remaining_sections
                if dependencies.issubset(completed_sections):
                    current_batch.append(section)
                    remaining_sections.remove(section)
                    
            if not current_batch:
                # 避免死循环，将剩余的都加入当前批次
                current_batch = list(remaining_sections)
                remaining_sections.clear()
                
            ordered_batches.append(current_batch)
            
        return ordered_batches
        
    async def _generate_section(self, section_type: str, input_data: Dict[str, Any]):
        """生成单个章节"""
        try:
            agent = self.section_agents[section_type]
            self.generation_status[section_type] = 'generating'
            
            # 发送生成请求
            request_id = str(uuid.uuid4())
            message = AgentMessage(
                sender=self.name,
                receiver=agent.name,
                content=json.dumps(input_data),
                message_type="generate_request",
                timestamp=datetime.now(),
                correlation_id=request_id
            )
            
            # 直接调用React智能体的handle_message方法并处理响应
            response_message = await agent.handle_message(message)
            
            if response_message:
                # 处理响应消息
                await self.handle_message(response_message)
            else:
                # 如果没有响应消息，标记为错误
                self.generation_status[section_type] = 'error'
                self.logger.error(f"No response from agent {section_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating section {section_type}: {e}")
            self.generation_status[section_type] = 'error'
            
    async def _wait_for_all_sections(self, timeout: float = 300.0):
        """等待所有章节完成"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 检查是否所有章节都已完成
            pending_sections = [
                section for section, status in self.generation_status.items()
                if status in ['pending', 'generating']
            ]
            
            if not pending_sections:
                break
                
            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                self.logger.error(f"Timeout waiting for sections: {pending_sections}")
                break
                
            await asyncio.sleep(1.0)
            
        # 记录最终状态
        completed = [s for s, status in self.generation_status.items() if status == 'completed']
        failed = [s for s, status in self.generation_status.items() if status == 'error']
        
        self.logger.info(f"Generation completed: {len(completed)} sections")
        if failed:
            self.logger.warning(f"Generation failed: {failed}")
            
    async def _integrate_final_document(self) -> str:
        """整合最终文档"""
        try:
            # 准备模板变量
            template_vars = {
                'project_name': self.input_data.get('project_name', '架构设计'),
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tech_stack': self.input_data.get('tech_stack_formatted', ''),
                **self.section_results
            }
            
            # 使用Jinja2渲染模板
            template = Template(self.document_template)
            final_document = template.render(**template_vars)
            
            # 后处理：确保文档连贯性
            final_document = await self._post_process_document(final_document)
            
            return final_document
            
        except Exception as e:
            self.logger.error(f"Error integrating final document: {e}")
            raise
            
    async def _post_process_document(self, document: str, input_data: Dict[str, Any] = None) -> str:
        """后处理文档，确保连贯性"""
        try:
            # 使用LLM进行文档连贯性检查和优化
            post_process_prompt = f"""
请检查以下架构设计文档的连贯性，并进行必要的优化：

1. 检查各章节之间的逻辑一致性
2. 确保技术选型在各章节中保持一致
3. 优化语言表达，使文档更加专业和流畅
4. 修正可能的矛盾或不一致之处

文档内容：
{document}

请返回优化后的完整文档。
"""
            
            response = await self.llm_service.generate_with_retry(
                prompt=post_process_prompt,
                system_prompt="你是一个专业的技术文档编辑，负责优化架构设计文档的质量和连贯性。"
            )
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error in post-processing: {e}")
            # 如果后处理失败，返回原文档
            return document
            
    def _render_new_document_structure(self, input_data: Dict[str, Any], section_contents: Dict[str, str]) -> str:
        """使用新的文档结构渲染文档"""
        try:
            # 准备模板变量
            template_vars = {
                'project_name': input_data.get('project_name', '架构设计'),
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tech_stack': input_data.get('tech_stack_formatted', ''),
                **section_contents
            }
            
            # 使用Jinja2渲染模板
            template = Template(self.document_template)
            final_document = template.render(**template_vars)
            
            return final_document
            
        except Exception as e:
            self.logger.error(f"Error rendering document: {e}")
            # 如果渲染失败，返回简单拼接的文档
            return self._fallback_document_render(input_data, section_contents)
            
    def _fallback_document_render(self, input_data: Dict[str, Any], section_contents: Dict[str, str]) -> str:
        """备用文档渲染方法"""
        document_parts = [
            f"# {input_data.get('project_name', '架构设计')} 架构设计文档\n",
            f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        ]
        
        for section_type, content in section_contents.items():
            document_parts.append(f"## {section_type}\n{content}\n\n")
            
        return ''.join(document_parts)
            
    async def generate_content(self, input_data: Dict[str, Any]) -> str:
        """实现基类的抽象方法"""
        return await self.generate_architecture_document(input_data)
        
    async def get_react_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有React智能体的状态"""
        status = {}
        for section_type, agent in self.section_agents.items():
            try:
                agent_status = {
                    'name': agent.name,
                    'is_running': agent.is_running,
                    'generation_status': self.generation_status.get(section_type, 'unknown'),
                    'dependencies': getattr(agent, 'dependencies', []),
                    'current_step': getattr(agent, 'current_step', 'idle')
                }
                status[section_type] = agent_status
            except Exception as e:
                status[section_type] = {'error': str(e)}
        return status
        
    async def reset_generation_state(self):
        """重置生成状态"""
        self.section_results.clear()
        self.generation_status = {section_type: 'pending' for section_type in self.section_agents.keys()}
        
        # 取消所有正在进行的任务
        for task in self.generation_tasks.values():
            if not task.done():
                task.cancel()
        self.generation_tasks.clear()
        
        self.logger.info("Generation state reset")
        
    def get_generation_status(self) -> Dict[str, str]:
        """获取生成状态"""
        return self.generation_status.copy()
        
    def get_section_results(self) -> Dict[str, str]:
        """获取章节结果"""
        return self.section_results.copy()