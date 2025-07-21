#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React模式章节智能体实现
为每个具体章节实现专门的React智能体
"""

import json
from typing import Dict, Any
from .react_agent import ReactAgent
from ..services.llm_service import LLMService

class ProjectBackgroundAgent(ReactAgent):
    """项目背景智能体 (1.1)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("项目背景智能体", config, llm_service, "项目背景")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化项目背景智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_business": self._tool_analyze_business,
            "generate_background": self._tool_generate_background,
            "validate_content": self._tool_validate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载项目背景智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是项目背景智能体，需要生成项目背景章节。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 项目的业务背景和价值
            2. 项目目标和预期收益
            3. 项目在整体业务中的定位
            
            让我开始分析项目背景信息。
            """,
            'thinking_step': """
            当前进行到第{step}步，之前的分析：
            {context_info}
            
            当前上下文：{context}
            
            我需要继续分析项目背景的哪个方面？
            """,
            'content_generation': """
            请根据以下信息生成项目背景章节内容：
            
            分析结果：{requirements}
            上下文信息：{context}
            
            请包含以下内容：
            1. 项目概述
            2. 业务背景
            3. 项目目标
            4. 预期收益
            
            请用专业的技术文档语言撰写，内容要具体、准确。
            """
        }
    
    async def _tool_analyze_business(self, business_info: str) -> str:
        """业务分析工具"""
        prompt = f"""
        请分析以下业务信息，提取关键的业务背景要素：
        
        业务信息：{business_info}
        
        请从以下角度分析：
        1. 核心业务价值
        2. 业务痛点和挑战
        3. 解决方案的必要性
        4. 业务影响范围
        
        请提供结构化的分析结果。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_generate_background(self, analysis_result: str) -> str:
        """项目背景生成工具"""
        template = self.prompt_templates.get('content_generation')
        prompt = template.format(
            requirements=analysis_result,
            context=json.dumps(self.context, ensure_ascii=False, indent=2)
        )
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_validate_content(self, content: str) -> str:
        """内容验证工具"""
        prompt = f"""
        请验证以下项目背景内容的质量：
        
        内容：{content}
        
        验证标准：
        1. 是否包含完整的项目概述
        2. 业务背景是否清晰
        3. 项目目标是否明确
        4. 预期收益是否具体
        
        请给出验证结果和改进建议。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成项目背景章节内容：
        
        系统描述：{context}
        需求信息：{requirements}
        
        请包含以下内容：
        1. 项目概述
        2. 业务背景
        3. 项目目标
        4. 预期收益
        
        请用专业的技术文档语言撰写，内容要具体、准确。
        """

class UnifiedTerminologyAgent(ReactAgent):
    """统一术语智能体 (1.2)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("统一术语智能体", config, llm_service, "统一术语")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化统一术语智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "extract_terms": self._tool_extract_terms,
            "define_terminology": self._tool_define_terminology,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载统一术语智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是统一术语智能体，需要生成项目的统一术语定义。
            
            输入信息：{input_data}
            
            我需要识别和定义：
            1. 技术术语和概念
            2. 业务领域术语
            3. 架构相关术语
            4. 常用缩写和简称
            
            让我开始术语提取和定义工作。
            """,
            'content_generation': """
            请根据以下信息生成统一术语章节：
            
            术语分析：{requirements}
            上下文信息：{context}
            
            请定义以下类型的术语：
            1. 技术术语
            2. 业务术语
            3. 架构术语
            4. 缩写说明
            
            格式：术语 - 定义说明
            """
        }
    
    async def _tool_extract_terms(self, content: str) -> str:
        """术语提取工具"""
        prompt = f"""
        请从以下内容中提取需要定义的关键术语：
        
        内容：{content}
        
        请识别：
        1. 技术专业术语
        2. 业务领域术语
        3. 架构设计术语
        4. 缩写和简称
        
        请列出术语清单。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_define_terminology(self, terms: str) -> str:
        """术语定义工具"""
        prompt = f"""
        请为以下术语提供准确的定义：
        
        术语清单：{terms}
        
        定义要求：
        1. 准确性和专业性
        2. 简洁明了
        3. 上下文相关
        4. 避免循环定义
        
        请提供术语定义。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下技术栈和系统信息生成统一术语章节：
        
        技术栈：{context}
        系统信息：{requirements}
        
        请定义以下类型的术语：
        1. 技术术语
        2. 业务术语
        3. 架构术语
        4. 缩写说明
        
        格式：术语 - 定义说明
        """

class TechStackSelectionAgent(ReactAgent):
    """技术栈选型智能体 (2.1)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("技术栈选型智能体", config, llm_service, "技术栈选型")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化技术栈选型智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_tech_requirements": self._tool_analyze_tech_requirements,
            "evaluate_technologies": self._tool_evaluate_technologies,
            "generate_selection_rationale": self._tool_generate_selection_rationale,
            "assess_risks": self._tool_assess_risks
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载技术栈选型智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是技术栈选型智能体，需要分析和生成技术栈选型方案。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 业务需求对技术的要求
            2. 各技术选项的优劣势
            3. 技术栈的整体协调性
            4. 实施风险和成本
            
            让我开始技术栈选型分析。
            """,
            'thinking_step': """
            技术栈选型第{step}步分析，之前的评估：
            {context_info}
            
            当前技术信息：{context}
            
            我需要继续评估哪个技术层面？
            """,
            'content_generation': """
            请根据技术评估结果生成技术栈选型章节：
            
            评估结果：{requirements}
            技术信息：{context}
            
            请包含：
            1. 技术栈总览
            2. 各层技术选型理由
            3. 技术栈优势分析
            4. 风险评估
            
            要详细说明选型依据和技术适配性。
            """
        }
    
    async def _tool_analyze_tech_requirements(self, requirements: str) -> str:
        """技术需求分析工具"""
        prompt = f"""
        请分析以下业务需求对技术栈的要求：
        
        业务需求：{requirements}
        
        请从以下维度分析：
        1. 性能要求
        2. 扩展性要求
        3. 安全性要求
        4. 开发效率要求
        5. 运维要求
        
        请提供技术需求清单。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_evaluate_technologies(self, tech_options: str) -> str:
        """技术评估工具"""
        prompt = f"""
        请评估以下技术选项：
        
        技术选项：{tech_options}
        
        评估维度：
        1. 技术成熟度
        2. 社区支持
        3. 学习成本
        4. 性能表现
        5. 生态完整性
        
        请给出详细的技术评估报告。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_generate_selection_rationale(self, evaluation: str) -> str:
        """选型理由生成工具"""
        template = self.prompt_templates.get('content_generation')
        prompt = template.format(
            requirements=evaluation,
            context=json.dumps(self.context, ensure_ascii=False, indent=2)
        )
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_assess_risks(self, tech_stack: str) -> str:
        """风险评估工具"""
        prompt = f"""
        请评估以下技术栈的风险：
        
        技术栈：{tech_stack}
        
        风险评估维度：
        1. 技术风险
        2. 人员风险
        3. 时间风险
        4. 成本风险
        5. 维护风险
        
        请提供风险评估和缓解措施。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成技术栈选型章节：
        
        已选技术栈：{context}
        业务需求：{requirements}
        
        请包含：
        1. 技术栈总览
        2. 各层技术选型理由
        3. 技术栈优势分析
        4. 风险评估
        
        要说明为什么选择这些技术，以及它们如何满足业务需求。
        """

class AppArchitectureOverviewAgent(ReactAgent):
    """应用架构总体设计思路智能体 (2.2)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("应用架构设计思路智能体", config, llm_service, "应用架构总体设计思路")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化应用架构智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_architecture_principles": self._tool_analyze_architecture_principles,
            "design_layers": self._tool_design_layers,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载应用架构智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是应用架构设计思路智能体，需要设计应用层面的架构方案。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 应用架构设计原则
            2. 分层架构方案
            3. 模块化设计策略
            4. 扩展性和可维护性考虑
            
            让我开始应用架构设计。
            """,
            'content_generation': """
            请根据以下信息生成应用架构总体设计思路：
            
            设计分析：{requirements}
            系统信息：{context}
            
            请包含：
            1. 架构设计原则
            2. 分层架构设计
            3. 模块化设计思路
            4. 扩展性考虑
            
            重点说明架构设计的核心思想和设计理念。
            """
        }
    
    async def _tool_analyze_architecture_principles(self, requirements: str) -> str:
        """架构原则分析工具"""
        prompt = f"""
        请分析以下需求，提出应用架构设计原则：
        
        需求信息：{requirements}
        
        请考虑：
        1. 可扩展性原则
        2. 可维护性原则
        3. 性能优化原则
        4. 安全性原则
        
        请提供架构设计原则。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_design_layers(self, principles: str) -> str:
        """分层设计工具"""
        prompt = f"""
        基于以下架构原则，设计应用分层架构：
        
        架构原则：{principles}
        
        请设计：
        1. 表现层设计
        2. 业务逻辑层设计
        3. 数据访问层设计
        4. 层间交互机制
        
        请提供分层架构设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成应用架构总体设计思路：
        
        系统信息：{context}
        技术栈：{requirements}
        
        请包含：
        1. 架构设计原则
        2. 分层架构设计
        3. 模块化设计思路
        4. 扩展性考虑
        
        重点说明架构设计的核心思想和设计理念。
        """

class SystemArchitectureOverviewAgent(ReactAgent):
    """系统架构总体设计思路智能体 (2.3)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("系统架构设计思路智能体", config, llm_service, "系统架构总体设计思路")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化系统架构智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "design_deployment": self._tool_design_deployment,
            "analyze_performance": self._tool_analyze_performance,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载系统架构智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是系统架构设计思路智能体，需要设计系统级架构方案。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 系统架构原则和策略
            2. 部署架构和基础设施
            3. 高可用和容灾方案
            4. 性能优化和监控策略
            
            让我开始系统架构设计。
            """,
            'content_generation': """
            请根据以下信息生成系统架构总体设计思路：
            
            设计分析：{requirements}
            应用架构信息：{context}
            
            请包含：
            1. 系统架构原则
            2. 部署架构设计
            3. 高可用设计
            4. 性能优化策略
            
            重点说明系统级别的架构设计考虑。
            """
        }
    
    async def _tool_design_deployment(self, requirements: str) -> str:
        """部署架构设计工具"""
        prompt = f"""
        请设计部署架构方案：
        
        系统需求：{requirements}
        
        请考虑：
        1. 服务器架构
        2. 网络拓扑
        3. 负载均衡
        4. 容器化部署
        
        请提供部署架构设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_analyze_performance(self, architecture: str) -> str:
        """性能分析工具"""
        prompt = f"""
        请分析以下架构的性能优化策略：
        
        架构设计：{architecture}
        
        请分析：
        1. 性能瓶颈点
        2. 优化策略
        3. 监控指标
        4. 扩展方案
        
        请提供性能优化建议。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成系统架构总体设计思路：
        
        应用架构信息：{context}
        系统需求：{requirements}
        
        请包含：
        1. 系统架构原则
        2. 部署架构设计
        3. 高可用设计
        4. 性能优化策略
        
        重点说明系统级别的架构设计考虑。
        """

class ModuleDivisionAgent(ReactAgent):
    """模块划分智能体 (3.1)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("模块划分智能体", config, llm_service, "模块划分")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化模块划分智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_domain": self._tool_analyze_domain,
            "identify_modules": self._tool_identify_modules,
            "define_boundaries": self._tool_define_boundaries,
            "validate_division": self._tool_validate_division,
            "generate_module_design": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载模块划分智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是模块划分智能体，需要进行系统模块划分设计。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 业务领域和功能边界
            2. 模块职责和依赖关系
            3. 模块划分的合理性
            4. 模块间的协作方式
            
            让我开始领域分析和模块识别。
            """,
            'thinking_step': """
            模块划分第{step}步，之前的分析：
            {context_info}
            
            当前模块信息：{context}
            
            我需要继续分析哪个模块或关系？
            """,
            'content_generation': """
            请根据模块分析结果生成模块划分设计：
            
            分析结果：{requirements}
            架构信息：{context}
            
            请包含：
            1. 模块划分原则
            2. 核心业务模块
            3. 支撑模块
            4. 模块间关系
            
            要清晰地说明每个模块的职责和边界。
            """
        }
    
    async def _tool_analyze_domain(self, business_requirements: str) -> str:
        """领域分析工具"""
        prompt = f"""
        请分析以下业务需求，识别核心业务领域：
        
        业务需求：{business_requirements}
        
        请从以下角度分析：
        1. 核心业务流程
        2. 业务实体和概念
        3. 业务规则和约束
        4. 业务边界和接口
        
        请提供领域分析结果。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_identify_modules(self, domain_analysis: str) -> str:
        """模块识别工具"""
        prompt = f"""
        基于以下领域分析，识别系统模块：
        
        领域分析：{domain_analysis}
        
        模块识别原则：
        1. 高内聚低耦合
        2. 单一职责原则
        3. 业务完整性
        4. 技术可行性
        
        请列出建议的模块清单和职责。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_define_boundaries(self, modules: str) -> str:
        """边界定义工具"""
        prompt = f"""
        请为以下模块定义清晰的边界：
        
        模块清单：{modules}
        
        边界定义要素：
        1. 模块输入输出
        2. 模块依赖关系
        3. 数据流向
        4. 接口规范
        
        请提供详细的边界定义。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_validate_division(self, module_design: str) -> str:
        """模块划分验证工具"""
        prompt = f"""
        请验证以下模块划分设计的合理性：
        
        模块设计：{module_design}
        
        验证维度：
        1. 职责清晰度
        2. 耦合度评估
        3. 可维护性
        4. 可扩展性
        
        请给出验证结果和优化建议。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成模块划分设计：
        
        业务需求：{context}
        架构思路：{requirements}
        
        请包含：
        1. 模块划分原则
        2. 核心业务模块
        3. 支撑模块
        4. 模块间关系
        
        要清晰地说明每个模块的职责和边界。
        """

class MicroserviceDivisionAgent(ReactAgent):
    """微服务划分智能体 (3.2)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("微服务划分智能体", config, llm_service, "微服务划分")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化微服务划分智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_services": self._tool_analyze_services,
            "define_boundaries": self._tool_define_service_boundaries,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载微服务划分智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是微服务划分智能体，需要进行微服务架构设计。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 业务模块到微服务的映射
            2. 微服务边界和职责
            3. 服务间通信机制
            4. 数据一致性策略
            
            让我开始微服务划分设计。
            """,
            'content_generation': """
            请根据以下信息生成微服务划分设计：
            
            分析结果：{requirements}
            模块信息：{context}
            
            请包含：
            1. 微服务划分原则
            2. 微服务清单
            3. 服务边界定义
            4. 服务间通信
            
            要详细说明每个微服务的职责和接口。
            """
        }
    
    async def _tool_analyze_services(self, modules: str) -> str:
        """微服务分析工具"""
        prompt = f"""
        请分析以下模块，设计微服务划分：
        
        模块信息：{modules}
        
        请考虑：
        1. 业务边界清晰度
        2. 数据独立性
        3. 团队组织结构
        4. 技术栈一致性
        
        请提供微服务划分建议。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_define_service_boundaries(self, services: str) -> str:
        """服务边界定义工具"""
        prompt = f"""
        请为以下微服务定义清晰的边界：
        
        微服务清单：{services}
        
        边界定义包括：
        1. 服务职责范围
        2. API接口设计
        3. 数据所有权
        4. 依赖关系
        
        请提供详细的边界定义。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成微服务划分设计：
        
        模块信息：{context}
        业务需求：{requirements}
        
        请包含：
        1. 微服务划分原则
        2. 微服务清单
        3. 服务边界定义
        4. 服务间通信
        
        要详细说明每个微服务的职责和接口。
        """

class MicroserviceCodeStructureAgent(ReactAgent):
    """微服务代码结构智能体 (3.2.1)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("微服务代码结构智能体", config, llm_service, "微服务代码结构")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化微服务代码结构智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "design_layers": self._tool_design_code_layers,
            "define_components": self._tool_define_key_components,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载微服务代码结构智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是微服务代码结构智能体，需要设计微服务的代码组织结构。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 代码分层架构
            2. 目录结构组织
            3. 关键组件设计
            4. 配置和依赖管理
            
            让我开始代码结构设计。
            """,
            'content_generation': """
            请根据以下信息生成微服务代码结构设计：
            
            分析结果：{requirements}
            微服务信息：{context}
            
            请包含：
            1. 代码组织结构
            2. 分层架构设计
            3. 关键组件设计
            4. 配置管理
            
            要详细说明每个层次的职责和实现方式。
            """
        }
    
    async def _tool_design_code_layers(self, microservices: str) -> str:
        """代码分层设计工具"""
        prompt = f"""
        请为以下微服务设计代码分层架构：
        
        微服务信息：{microservices}
        
        分层设计包括：
        1. 表现层(Controller)
        2. 业务逻辑层(Service)
        3. 数据访问层(Repository)
        4. 基础设施层(Infrastructure)
        
        请提供详细的分层设计方案。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_define_key_components(self, layers: str) -> str:
        """关键组件定义工具"""
        prompt = f"""
        请为以下分层架构定义关键组件：
        
        分层信息：{layers}
        
        组件设计包括：
        1. 核心业务组件
        2. 通用基础组件
        3. 配置管理组件
        4. 监控和日志组件
        
        请提供详细的组件设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成微服务代码结构设计：
        
        微服务信息：{context}
        技术栈：{requirements}
        
        请包含：
        1. 代码组织结构
        2. 分层架构实现
        3. 关键代码模块
        4. 编码规范
        
        要提供具体的目录结构和代码组织方式。
        """

class DownstreamImpactAgent(ReactAgent):
    """对下游系统影响智能体 (3.3)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("下游系统影响智能体", config, llm_service, "对下游系统的影响")
    
    def _initialize_tools(self) -> Dict[str, callable]:
        """初始化下游系统影响智能体专用工具"""
        return {
            "think": self._base_tool_think,
            "search_context": self._base_tool_search_context,
            "analyze_dependencies": self._tool_analyze_dependencies,
            "assess_impact": self._tool_assess_impact,
            "get_external_info": self._tool_get_external_info,
            "generate_content": self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载下游系统影响智能体专用提示词模板"""
        return {
            'initial_thinking': """
            我是下游系统影响智能体，需要分析系统变更对下游系统的影响。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 下游系统依赖关系
            2. 接口变更影响
            3. 数据流变化
            4. 兼容性和迁移策略
            
            让我开始下游影响分析。
            """,
            'content_generation': """
            请根据以下信息生成下游系统影响分析：
            
            分析结果：{requirements}
            系统信息：{context}
            
            请包含：
            1. 影响分析
            2. 接口变更
            3. 数据流变化
            4. 兼容性考虑
            
            要详细分析系统变更对下游的具体影响。
            """
        }
    
    async def _tool_analyze_dependencies(self, system_info: str) -> str:
        """依赖关系分析工具"""
        prompt = f"""
        请分析以下系统的下游依赖关系：
        
        系统信息：{system_info}
        
        请分析：
        1. 直接依赖的下游系统
        2. 间接依赖关系
        3. 关键依赖路径
        4. 依赖强度评估
        
        请提供详细的依赖关系分析。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_assess_impact(self, dependencies: str) -> str:
        """影响评估工具"""
        prompt = f"""
        请评估以下依赖关系的变更影响：
        
        依赖信息：{dependencies}
        
        影响评估包括：
        1. 功能影响范围
        2. 性能影响
        3. 数据一致性影响
        4. 业务流程影响
        
        请提供详细的影响评估报告。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_get_external_info(self, info_type: str) -> str:
        """重写获取外部信息工具，专门获取下游系统信息"""
        # 这里可以调用外部API获取下游系统信息
        return f"下游系统{info_type}信息：[通过API获取的实际数据]"
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息分析对下游系统的影响：
        
        当前系统设计：{context}
        下游系统信息：{requirements}
        
        请包含：
        1. 影响分析
        2. 接口变更
        3. 数据流变化
        4. 兼容性考虑
        
        要详细分析系统变更对下游的具体影响。
        """

class MicroserviceDeploymentAgent(ReactAgent):
    """微服务部署策略智能体 (4.1)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("微服务部署策略智能体", config, llm_service, "微服务部署策略设计")
    
    def _initialize_tools(self):
        """初始化微服务部署策略智能体的专属工具"""
        return {
            'think': self._base_tool_think,
            'search_context': self._base_tool_search_context,
            'design_deployment': self._tool_design_deployment_architecture,
            'plan_containerization': self._tool_plan_containerization,
            'generate_content': self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载微服务部署策略智能体的专属提示词模板"""
        return {
            'initial_thinking': """
            我是微服务部署策略智能体，专门负责设计微服务的部署策略。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 部署架构设计
            2. 容器化策略
            3. 编排方案
            4. 监控告警
            
            让我开始微服务部署策略设计。
            """,
            'content_generation': """
            请根据以下信息生成微服务部署策略：
            
            部署设计：{requirements}
            系统信息：{context}
            
            请包含：
            1. 部署架构设计
            2. 容器化策略
            3. 编排方案
            4. 监控告警
            
            要提供具体的部署方案和配置。
            """
        }
    
    async def _tool_design_deployment_architecture(self, microservice_info: str) -> str:
        """部署架构设计工具"""
        prompt = f"""
        请设计以下微服务的部署架构：
        
        微服务信息：{microservice_info}
        
        请设计：
        1. 部署拓扑结构
        2. 负载均衡策略
        3. 服务发现机制
        4. 网络配置
        
        请提供详细的部署架构设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_plan_containerization(self, deployment_arch: str) -> str:
        """容器化策略规划工具"""
        prompt = f"""
        请规划以下部署架构的容器化策略：
        
        部署架构：{deployment_arch}
        
        容器化策略包括：
        1. 容器镜像设计
        2. 资源配置
        3. 编排配置
        4. 扩缩容策略
        
        请提供详细的容器化策略规划。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成微服务部署策略：
        
        微服务架构：{context}
        部署需求：{requirements}
        
        请包含：
        1. 部署架构设计
        2. 容器化策略
        3. 编排方案
        4. 监控告警
        
        要提供具体的部署方案和配置。
        """

class DatabaseDeploymentAgent(ReactAgent):
    """数据库部署策略智能体 (4.2)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("数据库部署策略智能体", config, llm_service, "数据库部署策略设计")
    
    def _initialize_tools(self):
        """初始化数据库部署策略智能体的专属工具"""
        return {
            'think': self._base_tool_think,
            'search_context': self._base_tool_search_context,
            'design_database': self._tool_design_database_architecture,
            'plan_optimization': self._tool_plan_optimization,
            'generate_content': self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载数据库部署策略智能体的专属提示词模板"""
        return {
            'initial_thinking': """
            我是数据库部署策略智能体，专门负责设计数据库的部署策略。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 数据库架构
            2. 分库分表策略
            3. 读写分离
            4. 备份恢复
            
            让我开始数据库部署策略设计。
            """,
            'content_generation': """
            请根据以下信息生成数据库部署策略：
            
            数据库设计：{requirements}
            系统信息：{context}
            
            请包含：
            1. 数据库架构
            2. 分库分表策略
            3. 读写分离
            4. 备份恢复
            
            要提供详细的数据库部署和优化方案。
            """
        }
    
    async def _tool_design_database_architecture(self, database_info: str) -> str:
        """数据库架构设计工具"""
        prompt = f"""
        请设计以下数据库的部署架构：
        
        数据库信息：{database_info}
        
        请设计：
        1. 数据库拓扑结构
        2. 主从配置
        3. 集群方案
        4. 存储策略
        
        请提供详细的数据库架构设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_plan_optimization(self, db_arch: str) -> str:
        """数据库优化策略规划工具"""
        prompt = f"""
        请规划以下数据库架构的优化策略：
        
        数据库架构：{db_arch}
        
        优化策略包括：
        1. 性能优化
        2. 分库分表
        3. 索引策略
        4. 缓存策略
        
        请提供详细的数据库优化策略。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成数据库部署策略：
        
        数据库设计：{context}
        性能需求：{requirements}
        
        请包含：
        1. 数据库架构
        2. 分库分表策略
        3. 读写分离
        4. 备份恢复
        
        要提供详细的数据库部署和优化方案。
        """

class CloudServiceDesignAgent(ReactAgent):
    """云服务选型及架构设计智能体 (4.3)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("云服务设计智能体", config, llm_service, "云服务选型及架构设计")
    
    def _initialize_tools(self):
        """初始化云服务设计智能体的专属工具"""
        return {
            'think': self._base_tool_think,
            'search_context': self._base_tool_search_context,
            'select_services': self._tool_select_cloud_services,
            'design_architecture': self._tool_design_cloud_architecture,
            'generate_content': self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载云服务设计智能体的专属提示词模板"""
        return {
            'initial_thinking': """
            我是云服务设计智能体，专门负责云服务选型及架构设计。
            
            输入信息：{input_data}
            
            我需要设计：
            1. 云服务选型
            2. 云架构设计
            3. 成本优化
            4. 安全考虑
            
            让我开始云服务选型及架构设计。
            """,
            'content_generation': """
            请根据以下信息生成云服务选型及架构设计：
            
            云服务设计：{requirements}
            系统信息：{context}
            
            请包含：
            1. 云服务选型
            2. 云架构设计
            3. 成本优化
            4. 安全考虑
            
            要提供具体的云服务使用方案。
            """
        }
    
    async def _tool_select_cloud_services(self, system_info: str) -> str:
        """云服务选型工具"""
        prompt = f"""
        请为以下系统选择合适的云服务：
        
        系统信息：{system_info}
        
        请选择：
        1. 计算服务
        2. 存储服务
        3. 网络服务
        4. 安全服务
        
        请提供详细的云服务选型建议。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_design_cloud_architecture(self, cloud_services: str) -> str:
        """云架构设计工具"""
        prompt = f"""
        请设计基于以下云服务的架构：
        
        云服务选型：{cloud_services}
        
        架构设计包括：
        1. 整体架构图
        2. 服务间通信
        3. 数据流设计
        4. 安全架构
        
        请提供详细的云架构设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成云服务选型及架构设计：
        
        系统架构：{context}
        云服务需求：{requirements}
        
        请包含：
        1. 云服务选型
        2. 云架构设计
        3. 成本优化
        4. 安全考虑
        
        要提供具体的云服务使用方案。
        """

class ExternalDependenciesAgent(ReactAgent):
    """外部系统依赖智能体 (4.4)"""
    
    def __init__(self, config: Dict[str, Any], llm_service: LLMService):
        super().__init__("外部系统依赖智能体", config, llm_service, "外部系统依赖")
    
    def _initialize_tools(self):
        """初始化外部系统依赖智能体的专属工具"""
        return {
            'think': self._base_tool_think,
            'search_context': self._base_tool_search_context,
            'analyze_dependencies': self._tool_analyze_external_dependencies,
            'design_integration': self._tool_design_integration,
            'get_external_info': self._tool_get_external_info,
            'generate_content': self._base_tool_generate_content
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载外部系统依赖智能体的专属提示词模板"""
        return {
            'initial_thinking': """
            我是外部系统依赖智能体，专门负责分析和设计外部系统依赖。
            
            输入信息：{input_data}
            
            我需要分析：
            1. 依赖系统清单
            2. 接口设计
            3. 容错处理
            4. 监控告警
            
            让我开始外部系统依赖分析。
            """,
            'content_generation': """
            请根据以下信息生成外部系统依赖设计：
            
            依赖分析：{requirements}
            系统信息：{context}
            
            请包含：
            1. 依赖系统清单
            2. 接口设计
            3. 容错处理
            4. 监控告警
            
            要详细说明与外部系统的集成方案。
            """
        }
    
    async def _tool_analyze_external_dependencies(self, system_info: str) -> str:
        """外部依赖分析工具"""
        prompt = f"""
        请分析以下系统的外部依赖关系：
        
        系统信息：{system_info}
        
        请分析：
        1. 外部系统清单
        2. 依赖类型
        3. 依赖强度
        4. 风险评估
        
        请提供详细的外部依赖分析。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_design_integration(self, dependencies: str) -> str:
        """集成方案设计工具"""
        prompt = f"""
        请设计以下外部依赖的集成方案：
        
        外部依赖：{dependencies}
        
        集成方案包括：
        1. 接口设计
        2. 通信协议
        3. 数据格式
        4. 错误处理
        
        请提供详细的集成方案设计。
        """
        response = await self.llm_service.generate_text(prompt)
        return response.content
    
    async def _tool_get_external_info(self, info_type: str) -> str:
        """重写获取外部信息工具，专门获取外部依赖信息"""
        # 这里可以调用外部API获取上游系统信息
        return f"外部系统{info_type}依赖信息：[通过API获取的实际数据]"
    
    def _build_generation_prompt(self, context: str, requirements: str) -> str:
        return f"""
        请根据以下信息生成外部系统依赖设计：
        
        系统架构：{context}
        外部系统信息：{requirements}
        
        请包含：
        1. 依赖系统清单
        2. 接口设计
        3. 容错处理
        4. 监控告警
        
        要详细说明与外部系统的集成方案。
        """

# Agent工厂函数
def create_react_agents(llm_service: LLMService, config: Dict[str, Any]) -> Dict[str, ReactAgent]:
    """创建所有React模式智能体"""
    agents = {
        "project_background": ProjectBackgroundAgent(config, llm_service),
        "unified_terminology": UnifiedTerminologyAgent(config, llm_service),
        "tech_stack_selection": TechStackSelectionAgent(config, llm_service),
        "app_architecture_overview": AppArchitectureOverviewAgent(config, llm_service),
        "system_architecture_overview": SystemArchitectureOverviewAgent(config, llm_service),
        "module_division": ModuleDivisionAgent(config, llm_service),
        "microservice_division": MicroserviceDivisionAgent(config, llm_service),
        "microservice_code_structure": MicroserviceCodeStructureAgent(config, llm_service),
        "downstream_impact": DownstreamImpactAgent(config, llm_service),
        "microservice_deployment": MicroserviceDeploymentAgent(config, llm_service),
        # 缺少 microservice_deployment_details
        "database_deployment": DatabaseDeploymentAgent(config, llm_service),
        # 缺少 database_deployment_details
        "cloud_service_design": CloudServiceDesignAgent(config, llm_service),
        # 缺少 cloud_service_details
        "external_dependencies": ExternalDependenciesAgent(config, llm_service)
    }
    
    return agents