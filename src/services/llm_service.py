import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """LLM响应类"""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str
    
class LLMService:
    """大语言模型服务类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('dashscope_api_key')  # 通义千问使用DashScope API Key
        self.base_url = config.get('base_url', 'https://dashscope.aliyuncs.com/api/v1')
        self.model = config.get('model', 'qwen-turbo')  # 通义千问默认模型
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.logger = logging.getLogger('llm_service')
        
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, 
                           temperature: Optional[float] = None, 
                           max_tokens: Optional[int] = None) -> LLMResponse:
        """生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 通义千问API请求格式
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                "result_format": "message"
            }
        }
        
        # 通义千问使用Authorization头部认证
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "disable"  # 禁用SSE流式输出
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 通义千问响应格式解析
                        if data.get('code') and data['code'] != '200':
                            self.logger.error(f"DashScope API error: {data.get('code')} - {data.get('message')}")
                            raise Exception(f"DashScope API error: {data.get('code')} - {data.get('message')}")
                        
                        output = data.get('output', {})
                        choice = output.get('choices', [{}])[0]
                        message = choice.get('message', {})
                        
                        return LLMResponse(
                            content=message.get('content', ''),
                            usage=data.get('usage', {}),
                            model=self.model,
                            finish_reason=choice.get('finish_reason', 'stop')
                        )
                    else:
                        error_text = await response.text()
                        self.logger.error(f"DashScope API error: {response.status} - {error_text}")
                        raise Exception(f"DashScope API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error calling DashScope API: {e}")
            raise
            
    async def generate_with_retry(self, prompt: str, system_prompt: Optional[str] = None,
                                 max_retries: int = 3, retry_delay: float = 1.0) -> LLMResponse:
        """带重试的文本生成"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await self.generate_text(prompt, system_prompt)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    self.logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                else:
                    self.logger.error(f"All LLM generation attempts failed")
                    
        raise last_exception
        
    async def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None,
                           concurrency: int = 3) -> List[LLMResponse]:
        """批量生成文本"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def generate_single(prompt: str) -> LLMResponse:
            async with semaphore:
                return await self.generate_with_retry(prompt, system_prompt)
                
        tasks = [generate_single(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
        
    def format_prompt_with_template(self, template: str, variables: Dict[str, Any]) -> str:
        """使用模板格式化提示词"""
        try:
            return template.format(**variables)
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error formatting prompt template: {e}")
            raise
            
    def estimate_tokens(self, text: str) -> int:
        """估算token数量（简单实现）"""
        # 简单估算：1个token约等于4个字符（英文）或1.5个字符（中文）
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)
        
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.api_key:
            self.logger.error("DashScope API key is required")
            return False
            
        if not self.base_url:
            self.logger.error("Base URL is required")
            return False
            
        return True