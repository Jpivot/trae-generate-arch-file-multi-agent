import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class APIResponse:
    """API响应类"""
    data: Any
    status_code: int
    headers: Dict[str, str]
    response_time: float
    
class ExternalAPIService:
    """外部API服务类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('external_api_service')
        self.session = None
        self.cache = {}  # 简单的内存缓存
        self.cache_ttl = 300  # 缓存5分钟
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'ArchitectureDocGenerator/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            
    async def get_upstream_systems(self, system_id: str) -> List[Dict[str, Any]]:
        """获取上游系统信息"""
        cache_key = f"upstream_{system_id}"
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            url = self.config.get('upstream_service_api', '')
            if not url:
                self.logger.warning("Upstream service API URL not configured")
                return self._get_mock_upstream_data(system_id)
                
            params = {'system_id': system_id}
            response = await self._make_request('GET', url, params=params)
            
            if response.status_code == 200:
                upstream_systems = response.data.get('upstream_systems', [])
                self._set_cache(cache_key, upstream_systems)
                return upstream_systems
            else:
                self.logger.error(f"Failed to get upstream systems: {response.status_code}")
                return self._get_mock_upstream_data(system_id)
                
        except Exception as e:
            self.logger.error(f"Error getting upstream systems: {e}")
            return self._get_mock_upstream_data(system_id)
            
    async def get_downstream_systems(self, system_id: str) -> List[Dict[str, Any]]:
        """获取下游系统信息"""
        cache_key = f"downstream_{system_id}"
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            url = self.config.get('downstream_service_api', '')
            if not url:
                self.logger.warning("Downstream service API URL not configured")
                return self._get_mock_downstream_data(system_id)
                
            params = {'system_id': system_id}
            response = await self._make_request('GET', url, params=params)
            
            if response.status_code == 200:
                downstream_systems = response.data.get('downstream_systems', [])
                self._set_cache(cache_key, downstream_systems)
                return downstream_systems
            else:
                self.logger.error(f"Failed to get downstream systems: {response.status_code}")
                return self._get_mock_downstream_data(system_id)
                
        except Exception as e:
            self.logger.error(f"Error getting downstream systems: {e}")
            return self._get_mock_downstream_data(system_id)
            
    async def get_api_specifications(self, system_id: str) -> Dict[str, Any]:
        """获取API规范信息"""
        cache_key = f"api_specs_{system_id}"
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # 模拟API规范获取
            api_specs = {
                "openapi": "3.0.0",
                "info": {
                    "title": f"{system_id} API",
                    "version": "1.0.0",
                    "description": f"API specifications for {system_id}"
                },
                "paths": {
                    "/api/v1/health": {
                        "get": {
                            "summary": "Health check",
                            "responses": {
                                "200": {
                                    "description": "Service is healthy"
                                }
                            }
                        }
                    }
                }
            }
            
            self._set_cache(cache_key, api_specs)
            return api_specs
            
        except Exception as e:
            self.logger.error(f"Error getting API specifications: {e}")
            return {}
            
    async def _make_request(self, method: str, url: str, 
                           params: Optional[Dict[str, Any]] = None,
                           data: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """发起HTTP请求"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers
            ) as response:
                response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                response_time = asyncio.get_event_loop().time() - start_time
                
                return APIResponse(
                    data=response_data,
                    status_code=response.status,
                    headers=dict(response.headers),
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Request failed: {method} {url} - {e}")
            raise
            
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return data
            else:
                del self.cache[key]
        return None
        
    def _set_cache(self, key: str, data: Any):
        """设置缓存数据"""
        self.cache[key] = (data, datetime.now())
        
    def _get_mock_upstream_data(self, system_id: str) -> List[Dict[str, Any]]:
        """获取模拟上游系统数据"""
        return [
            {
                "name": "统一认证中心",
                "type": "authentication",
                "protocol": "OAuth 2.0",
                "endpoint": "https://auth.example.com",
                "description": "提供用户认证和授权服务",
                "sla": {
                    "availability": "99.9%",
                    "response_time": "< 200ms"
                }
            },
            {
                "name": "支付网关",
                "type": "payment",
                "protocol": "HTTPS REST",
                "endpoint": "https://payment.example.com",
                "description": "处理支付相关业务",
                "sla": {
                    "availability": "99.99%",
                    "response_time": "< 500ms"
                }
            }
        ]
        
    def _get_mock_downstream_data(self, system_id: str) -> List[Dict[str, Any]]:
        """获取模拟下游系统数据"""
        return [
            {
                "name": "消息推送系统",
                "type": "notification",
                "protocol": "HTTPS + WebSocket",
                "endpoint": "https://notification.example.com",
                "description": "发送各类通知消息",
                "features": ["短信", "邮件", "App推送", "站内消息"]
            },
            {
                "name": "数据分析平台",
                "type": "analytics",
                "protocol": "Kafka",
                "endpoint": "kafka://analytics.example.com:9092",
                "description": "收集和分析业务数据",
                "features": ["实时分析", "报表生成", "数据可视化"]
            }
        ]
        
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        results = {}
        
        # 检查上游服务API
        upstream_url = self.config.get('upstream_service_api')
        if upstream_url:
            try:
                response = await self._make_request('GET', f"{upstream_url}/health")
                results['upstream_api'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.response_time
                }
            except Exception as e:
                results['upstream_api'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        # 检查下游服务API
        downstream_url = self.config.get('downstream_service_api')
        if downstream_url:
            try:
                response = await self._make_request('GET', f"{downstream_url}/health")
                results['downstream_api'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.response_time
                }
            except Exception as e:
                results['downstream_api'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                
        return results