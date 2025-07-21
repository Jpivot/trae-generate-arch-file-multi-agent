#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构设计文档生成系统
多智能体协作生成架构设计文档
"""

import asyncio
import json
import logging
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.factory.agent_factory import AgentFactory
from src.agents.master_agent import MasterAgent

def setup_logging(log_level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('architecture_generator.log', encoding='utf-8')
        ]
    )

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        raise

def load_input_data(input_path: str) -> Dict[str, Any]:
    """加载输入数据"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            if input_path.endswith('.json'):
                return json.load(f)
            elif input_path.endswith('.yaml') or input_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                raise ValueError("Unsupported input file format")
    except Exception as e:
        logging.error(f"Error loading input data: {e}")
        raise

def save_document(document: str, output_path: str):
    """保存生成的文档"""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(document)
            
        logging.info(f"Document saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error saving document: {e}")
        raise

class ArchitectureDocumentGenerator:
    """架构设计文档生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('document_generator')
        self.agent_factory = AgentFactory(config)
        self.master_agent: MasterAgent = None
        
    async def initialize(self):
        """初始化系统"""
        try:
            # 验证配置
            if not self.agent_factory.validate_configuration():
                raise ValueError("Configuration validation failed")
                
            # 创建智能体系统
            self.master_agent = self.agent_factory.create_complete_system()
            
            # 启动智能体系统
            await self.master_agent.start()
            
            self.logger.info("System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing system: {e}")
            raise
            
    async def generate_document(self, input_data: Dict[str, Any]) -> str:
        """生成架构设计文档"""
        try:
            if not self.master_agent:
                raise RuntimeError("System not initialized")
                
            self.logger.info("Starting document generation")
            start_time = datetime.now()
            
            # 生成文档（使用React模式）
            document = await self.master_agent.generate_document(input_data)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Document generation completed in {duration:.2f} seconds")
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating document: {e}")
            raise
            
    async def get_generation_status(self) -> Dict[str, Any]:
        """获取生成状态"""
        if not self.master_agent:
            return {"status": "not_initialized"}
            
        return {
            "status": "initialized",
            "section_status": self.master_agent.get_generation_status(),
            "agent_info": self.agent_factory.get_agent_info()
        }
        
    async def cleanup(self):
        """清理资源"""
        try:
            if self.master_agent:
                await self.master_agent.stop()
            self.logger.info("System cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

async def main():
    """主函数"""
    try:
        # 设置日志
        setup_logging("INFO")
        logger = logging.getLogger('main')
        
        logger.info("Starting Architecture Document Generator")
        
        # 加载配置
        config = load_config("config.yaml")
        
        # 创建生成器
        generator = ArchitectureDocumentGenerator(config)
        
        # 初始化系统
        await generator.initialize()
        
        # 准备输入数据（示例）
        input_data = {
            "project_name": "电商平台系统",
            "system_id": "ecommerce_platform",
            "system_description": "一个支持高并发的电商平台系统，包含用户管理、商品管理、订单处理、支付系统等核心功能",
            "tech_stack": {
                "前端": ["React", "TypeScript", "Ant Design"],
                "后端": ["Spring Boot", "Spring Cloud", "Java 17"],
                "数据库": ["MySQL 8.0", "Redis 6.0", "MongoDB"],
                "消息队列": ["Apache Kafka", "RabbitMQ"],
                "容器化": ["Docker", "Kubernetes"],
                "监控": ["Prometheus", "Grafana", "ELK Stack"]
            },
            "database_info": {
                "primary_db": "MySQL 8.0",
                "cache_db": "Redis 6.0",
                "document_db": "MongoDB",
                "search_engine": "Elasticsearch"
            },
            "business_requirements": [
                "支持10万+并发用户",
                "99.9%系统可用性",
                "秒级响应时间",
                "支持水平扩展",
                "数据安全和隐私保护"
            ],
            "business_modules": [
                "用户管理",
                "商品管理",
                "订单处理",
                "支付系统",
                "库存管理",
                "推荐系统",
                "客服系统"
            ],
            "business_entities": [
                "用户",
                "商品",
                "订单",
                "支付记录",
                "库存",
                "购物车",
                "评价"
            ],
            "dev_standards": {
                "代码规范": "阿里巴巴Java开发手册",
                "API设计": "RESTful API设计规范",
                "数据库设计": "数据库设计三范式",
                "安全规范": "OWASP安全开发指南"
            }
        }
        
        # 如果存在输入文件，则加载
        input_file = "input_data.json"
        if Path(input_file).exists():
            input_data = load_input_data(input_file)
            logger.info(f"Loaded input data from {input_file}")
        
        # 生成文档
        document = await generator.generate_document(input_data)
        
        # 保存文档
        output_path = f"output/architecture_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        save_document(document, output_path)
        
        # 获取生成状态
        status = await generator.get_generation_status()
        logger.info(f"Generation status: {json.dumps(status, ensure_ascii=False, indent=2)}")
        
        logger.info("Architecture document generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        # 清理资源
        if 'generator' in locals():
            await generator.cleanup()

def create_sample_input_file():
    """创建示例输入文件"""
    sample_data = {
        "project_name": "智能客服系统",
        "system_id": "smart_customer_service",
        "system_description": "基于AI的智能客服系统，支持多渠道接入、自然语言处理、知识库管理等功能",
        "tech_stack": {
            "前端": ["Vue.js 3", "TypeScript", "Element Plus"],
            "后端": ["Spring Boot", "Spring Cloud Gateway", "Java 17"],
            "AI/ML": ["Python", "TensorFlow", "BERT", "FastAPI"],
            "数据库": ["PostgreSQL", "Redis", "Elasticsearch"],
            "消息队列": ["Apache Kafka"],
            "容器化": ["Docker", "Kubernetes"]
        },
        "database_info": {
            "primary_db": "PostgreSQL 14",
            "cache_db": "Redis 7.0",
            "search_engine": "Elasticsearch 8.0",
            "vector_db": "Milvus"
        },
        "business_requirements": [
            "支持多渠道接入（网页、微信、APP）",
            "智能意图识别准确率>90%",
            "平均响应时间<2秒",
            "支持7x24小时服务",
            "支持多语言"
        ]
    }
    
    with open("input_data.json", 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("Sample input file created: input_data.json")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_input_file()
    else:
        asyncio.run(main())