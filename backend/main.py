# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api import ai_api
from fastapi.middleware.cors import CORSMiddleware
from api import participants_api
from api import network_api
from api import mindmap_api
from api import hostStyle_api

# 設置日誌
from utility.logger import setup_logger
logger = setup_logger("mbbuddy")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # Startup
    logger.info("🚀 MBBuddy 後端服務啟動中...")
    
    # 預載入 CPU LLM 模型
    try:
        from api.local_llm_client import local_llm_client
        logger.info("📥 開始預載入 CPU LLM 模型...")
        
        # 檢查模型文件是否存在
        model_dir = local_llm_client.models_dir / "qwen2-1.5b"
        if model_dir.exists():
            model_files = list(model_dir.glob("*.gguf"))
            if model_files:
                model_path = str(model_files[0])
                logger.info(f"📁 找到模型文件: {model_path}")
                
                # 預載入模型
                success = await local_llm_client.load_model(model_path, "qwen2-1.5b")
                if success:
                    logger.info("✅ CPU LLM 模型預載入成功")
                else:
                    logger.warning("⚠️ CPU LLM 模型預載入失敗")
            else:
                logger.warning("⚠️ 找不到 .gguf 模型文件")
        else:
            logger.warning("⚠️ 模型目錄不存在，將在首次調用時下載")
            
    except Exception as e:
        logger.error(f"❌ 預載入 CPU LLM 模型時發生錯誤: {e}")
    
    # 測試 AnythingLLM 連接
    try:
        from api.ai_client import ai_client
        from api.ai_config import ai_config
        
        logger.info("🔗 測試 AnythingLLM 連接...")
        logger.info(f"   目標: {ai_config.base_url}")
        logger.info(f"   工作區: {ai_config.workspace_slug}")
        
        # 簡單的連接測試
        test_result = await ai_client.test_connection()
        
        # 正確檢查連接狀態
        if test_result.get("status") == "success":
            workspace_count = len(test_result.get("workspaces", []))
            logger.info(f"✅ AnythingLLM 連接正常 (找到 {workspace_count} 個工作區)")
        else:
            logger.error("❌ AnythingLLM 連接失敗")
            logger.error(f"   錯誤訊息: {test_result.get('message', '未知錯誤')}")
            if "response" in test_result:
                logger.error(f"   回應內容: {test_result['response']}")
            logger.error("   請檢查:")
            logger.error("   1. AnythingLLM 服務是否正在運行")
            logger.error("   2. ANYTHINGLLM_API_KEY 是否有效")
            
    except Exception as e:
        logger.error(f"❌ AnythingLLM 連接測試時發生異常: {e}")
        import traceback
        logger.error(f"   詳細堆疊:\n{traceback.format_exc()}")
    
    logger.info("🎉 MBBuddy 後端服務啟動完成！")
    
    yield
    
    # Shutdown
    logger.info("🛑 MBBuddy 後端服務正在關閉...")
    
    try:
        from api.local_llm_client import local_llm_client
        if local_llm_client.is_model_loaded():
            local_llm_client.unload_model()
            logger.info("✅ CPU LLM 模型已卸載")
    except Exception as e:
        logger.error(f"❌ 卸載模型時發生錯誤: {e}")
    
    logger.info("👋 MBBuddy 後端服務已關閉")

app = FastAPI(title="MBBuddy API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(participants_api.router)
app.include_router(ai_api.router)
app.include_router(network_api.router)
app.include_router(mindmap_api.router)
app.include_router(hostStyle_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
