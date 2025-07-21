import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentMessage:
    """智能体消息类"""
    sender: str
    receiver: str
    content: str
    message_type: str
    timestamp: datetime
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"agent.{name}")
        self.message_queue = asyncio.Queue()
        self.is_running = False
        self.context = {}
        
    async def start(self):
        """启动智能体"""
        self.is_running = True
        self.logger.info(f"Agent {self.name} started")
        
    async def stop(self):
        """停止智能体"""
        self.is_running = False
        self.logger.info(f"Agent {self.name} stopped")
        
    async def send_message(self, receiver: str, content: str, message_type: str = "request", 
                          correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """发送消息"""
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        # 这里应该通过消息总线发送，简化实现直接返回消息
        self.logger.info(f"Sending message to {receiver}: {message_type}")
        return message
        
    async def receive_message(self, message: AgentMessage):
        """接收消息"""
        await self.message_queue.put(message)
        
    async def process_messages(self):
        """处理消息队列"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                
    @abstractmethod
    async def handle_message(self, message: AgentMessage):
        """处理具体消息，子类需要实现"""
        pass
        
    @abstractmethod
    async def generate_content(self, input_data: Dict[str, Any]) -> str:
        """生成内容，子类需要实现"""
        pass
        
    def update_context(self, key: str, value: Any):
        """更新上下文"""
        self.context[key] = value
        
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self.context.get(key, default)
        
    def set_shared_context(self, shared_context: Dict[str, Any]):
        """设置共享上下文"""
        self.context.update(shared_context)