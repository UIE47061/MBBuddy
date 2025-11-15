from dotenv import load_dotenv, find_dotenv
import os

# 自動尋找專案根目錄的 .env
load_dotenv(find_dotenv(), override=False)

# 統一管理環境變數和 API Keys
class Env:
    # 應用配置
    RELOAD: bool = os.getenv("RELOAD", "").lower() == "true"
    
    # AnythingLLM API 配置
    ANYTHINGLLM_BASE_URL: str = os.getenv("ANYTHINGLLM_BASE_URL", "http://localhost:3001")
    ANYTHINGLLM_API_KEY: str = os.getenv("ANYTHINGLLM_API_KEY", "ANYTHINGLLM_API_KEY_NOT_SET")
    ANYTHINGLLM_WORKSPACE_SLUG: str = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG", "MBBuddy")
    ANYTHINGLLM_DEBUG_THINKING: bool = os.getenv("ANYTHINGLLM_DEBUG_THINKING", "false").lower() == "true"
    
    # Snapdragon Elite X 平台配置
    SNAPDRAGON_ELITE_X: bool = os.getenv("SNAPDRAGON_ELITE_X", "false").lower() == "true"

env = Env()