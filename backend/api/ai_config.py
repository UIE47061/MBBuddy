"""
AI 配置和初始化模块
負責處理 AnythingLLM 的配置、環境變數和 HTTP 客戶端初始化
"""

import httpx
from typing import Optional
from utility.config import env

class AIConfig:
    """AI配置管理類"""
    
    def __init__(self):
        # AnythingLLM API 配置 - 從統一配置讀取
        self.base_url = env.ANYTHINGLLM_BASE_URL
        self.api_key = env.ANYTHINGLLM_API_KEY
        self.workspace_slug = env.ANYTHINGLLM_WORKSPACE_SLUG
        
        # 調試配置
        self.debug_thinking = env.ANYTHINGLLM_DEBUG_THINKING
        
        # HTTP 客戶端配置
        self._httpx_client: Optional[httpx.AsyncClient] = None
        
        # 驗證配置
        self._validate_config()
    
    def _validate_config(self):
        """驗證配置的有效性"""
        if not self.api_key:
            print("警告：未設置 ANYTHINGLLM_API_KEY 環境變數")
    
    @property
    def httpx_client(self) -> httpx.AsyncClient:
        """獲取HTTP客戶端實例（懶加載）"""
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._httpx_client
    
    @property
    def headers(self) -> dict:
        """獲取標準請求頭"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_workspace_url(self, workspace_slug: str = None) -> str:
        """獲取工作區API的完整URL"""
        slug = workspace_slug or self.workspace_slug
        return f"{self.base_url}/api/v1/workspace/{slug}/chat"
    
    def get_workspaces_url(self) -> str:
        """獲取工作區列表API的完整URL"""
        return f"{self.base_url}/api/v1/workspaces"
    
    def get_create_workspace_url(self) -> str:
        """獲取創建工作區API的完整URL"""
        return f"{self.base_url}/api/v1/workspace/new"
    
    async def close(self):
        """關閉HTTP客戶端連接"""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None

# 全局配置實例
ai_config = AIConfig()
