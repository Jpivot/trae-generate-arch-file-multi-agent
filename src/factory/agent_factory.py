import logging
from typing import Dict, Any, List
from pathlib import Path

from ..agents.master_agent import MasterAgent
from ..agents.react_section_agents import create_react_agents
from ..services.llm_service import LLMService

class AgentFactory:
    """智能体工厂类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('agent_factory')
        self.llm_service = self._create_llm_service()
        
    def _create_llm_service(self) -> LLMService:
        """创建LLM服务"""
        api_config = self.config.get('api', {})
        return LLMService(api_config)
        
    def create_master_agent(self, config: Dict[str, Any]) -> MasterAgent:
        """创建主智能体"""
        try:
            master_agent = MasterAgent(
                name="MasterAgent",
                config=config,
                llm_service=self.llm_service
            )
            
            self.logger.info(f"Created master agent with React mode section agents")
            return master_agent
            
        except Exception as e:
            self.logger.error(f"Failed to create master agent: {e}")
            raise
            
    # React模式下不再需要单独创建section agents，由master_agent内部管理
        
    # React模式下不再需要_create_section_agent方法
        
    def _get_section_dependencies(self, section_type: str) -> List[str]:
        """获取章节依赖关系"""
        # 定义章节间的依赖关系
        dependencies_map = {
            'background_agent': [],  # 背景章节无依赖
            'app_architecture_agent': ['background_agent'],  # 应用架构依赖背景
            'microservice_agent': ['app_architecture_agent'],  # 微服务架构依赖应用架构
            'code_structure_agent': ['microservice_agent'],  # 代码结构依赖微服务架构
            'database_agent': ['microservice_agent'],  # 数据库设计依赖微服务架构
            'upstream_downstream_agent': ['app_architecture_agent']  # 上下游系统依赖应用架构
        }
        
        return dependencies_map.get(section_type, [])
        
    def create_complete_system(self) -> MasterAgent:
        """创建完整的智能体系统"""
        try:
            # 创建主智能体（React模式下内部自动管理section agents）
            master_agent = self.create_master_agent(self.config)
                
            self.logger.info(f"Created complete system with React mode section agents")
            return master_agent
            
        except Exception as e:
            self.logger.error(f"Error creating complete system: {e}")
            raise
            
    def validate_configuration(self) -> bool:
        """验证配置"""
        try:
            # 验证API配置
            api_config = self.config.get('api', {})
            if not api_config.get('dashscope_api_key'):
                self.logger.error("OpenAI API key is required")
                return False
                
            # 验证智能体配置
            agents_config = self.config.get('agents', {})
            if not agents_config:
                self.logger.error("No agents configured")
                return False
                
            # 验证模板文件
            for section_type, agent_config in agents_config.items():
                prompt_template = agent_config.get('prompt_template', '')
                template_path = Path(f"templates/prompts/{prompt_template}")
                if not template_path.exists():
                    self.logger.warning(f"Prompt template not found: {template_path}")
                    
            # 验证LLM服务
            if not self.llm_service.validate_config():
                return False
                
            self.logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return False
            
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        agents_config = self.config.get('agents', {})
        agent_info = {}
        
        for section_type, agent_config in agents_config.items():
            dependencies = self._get_section_dependencies(section_type)
            agent_info[section_type] = {
                'name': agent_config.get('name', f"{section_type}_agent"),
                'prompt_template': agent_config.get('prompt_template', ''),
                'dependencies': dependencies,
                'description': f"负责生成{section_type}章节内容"
            }
            
        return agent_info
        
    # React模式下不再需要create_custom_agent方法，所有agents由React框架管理