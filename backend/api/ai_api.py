from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, random, time
from typing import List, Optional
from .participants_api import ROOMS, topics, votes
from .ai_config import ai_config
from .ai_client import ai_client
from .ai_prompts import prompt_builder, topic_parser
from .transparent_fusion import transparent_fusion
from .local_llm_client import local_llm_client

router = APIRouter(prefix="/ai", tags=["AI"])

class AskRequest(BaseModel):
    prompt: str

@router.get("/test_connection")
async def test_anythingllm_connection():
    """測試AnythingLLM連接的端點"""
    return await ai_client.test_connection()

class TestWorkspaceRequest(BaseModel):
    room_code: str
    room_title: str

@router.post("/test_create_workspace")
async def test_create_workspace(req: TestWorkspaceRequest):
    """測試創建工作區的端點"""
    try:
        workspace_slug = await ai_client.ensure_workspace_exists(req.room_code, req.room_title)
        return {
            "status": "success",
            "message": f"工作區操作成功",
            "workspace_slug": workspace_slug,
            "room_code": req.room_code,
            "room_title": req.room_title
        }
    except Exception as e:
        return {"status": "error", "message": f"創建工作區失敗: {str(e)}"}

@router.post("/ask")
async def ask_ai(req: AskRequest):
    """AI問答 - 透明融合系統（NPU+CPU並行->NPU融合）"""
    try:
        # 使用透明融合引擎，背景並行NPU+CPU，最終NPU融合推理
        answer = await transparent_fusion.process_request(req.prompt, task_type="chat")
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 處理失敗: {str(e)}")

# 定義用於 AI 總結的請求模型
class SummaryRequest(BaseModel):
    room: str  # 討論室代碼
    topic: str # 要總結的主題

@router.post("/summary")
async def summary_ai(req: SummaryRequest):
    """
    對指定討論室的特定主題進行 AI 總結

    [POST] /ai/summary

    參數：
    - room (str): 討論室代碼
    - topic (str): 要進行總結的主題名稱

    回傳：
    - summary (str): AI 生成的總結文字
    """
    # 檢查討論室是否存在
    if req.room not in ROOMS:
        return {"summary": "錯誤：找不到指定的討論室。"}

    # 組合主題 ID 並檢查主題是否存在
    topic_id = f"{req.room}_{req.topic}"
    if topic_id not in topics:
        return {"summary": "錯誤：在該討論室中找不到指定的主題。"}

    # 使用prompt_builder的方法來建立 prompt
    prompt = prompt_builder.build_summary_prompt(req.room, req.topic)
    
    if prompt.startswith("錯誤"):
        return {"summary": prompt}

    # 使用透明融合系統生成摘要
    try:
        # 獲取討論室資訊
        room_data = ROOMS[req.room]
        room_title = room_data.get('title', f'討論室-{req.room}')
        
        # 優先使用討論創建時保存的workspace，如果不存在則創建
        workspace_slug = room_data.get('workspace_slug')
        if not workspace_slug:
            print(f"⚠️ 討論 {req.room} 沒有預設workspace，正在創建...")
            workspace_slug = await ai_client.ensure_workspace_exists(req.room, room_title)
            # 更新討論數據
            ROOMS[req.room]['workspace_slug'] = workspace_slug
            workspace_info = await ai_client.get_workspace_info(workspace_slug)
            if workspace_info and "id" in workspace_info:
                ROOMS[req.room]['workspace_id'] = workspace_info["id"]
        else:
            print(f"✅ 使用討論專屬workspace: {workspace_slug}")
        
        # 使用透明融合系統：NPU+CPU並行->NPU融合，提升摘要質量
        summary_text = await transparent_fusion.process_request(
            prompt, workspace_slug, task_type="summary"
        )
        return {"summary": summary_text}
    except HTTPException:
        raise
    except Exception as e:
        return {"summary": f"AI 總結生成失敗: {str(e)}"}

async def _generate_topics_from_title(meeting_title: str, topic_count: int, workspace_slug: str = None) -> List[str]:
    """
    根據討論標題生成主題的核心邏輯。
    這是一個內部函式，旨在被其他 API 端點調用。
    """
    topic_count = max(1, min(10, topic_count))
    meeting_title = meeting_title.strip()

    if not meeting_title:
        return ["錯誤：討論名稱不可為空。"]

    prompt = prompt_builder.build_topics_generation_prompt(meeting_title, topic_count)
    
    if prompt.startswith("錯誤"):
        return [prompt]

    try:
        # 使用透明融合系統生成主題：NPU+CPU並行->NPU融合
        raw_text = await transparent_fusion.process_request(prompt, workspace_slug, task_type="topic_generation")
        return topic_parser.parse_topics_from_response(raw_text, topic_count)

    except Exception as e:
        print(f"Error calling LLM for topic generation: {e}")
        return [f"AI服務暫時無法連線，請稍後再試。"]


class GenerateTopicsRequest(BaseModel):
    """用於 AI 生成主題請求的模型"""
    meeting_title: str
    topic_count: int
    room_code: Optional[str] = None  # 可選的討論代碼，如果提供則使用討論專屬workspace

@router.post("/generate_topics")
async def generate_ai_topics(req: GenerateTopicsRequest):
    """
    根據討論名稱和指定數量，使用 AI 生成議程主題。

    [POST] /ai/generate_topics

    參數：
    - meeting_title (str): 討論的標題或主要目的。
    - topic_count (int): 希望生成的主題數量。

    回傳：
    - topics (list[str]): 一個包含 AI 生成的主題字串的列表。
    """
    # --- 1. 基本驗證 ---
    # 確保主題數量在一個合理的範圍內
    topic_count = max(1, min(10, req.topic_count)) 
    meeting_title = req.meeting_title.strip()

    if not meeting_title:
        return {"topics": ["錯誤：討論名稱不可為空。"]}

    # 呼叫 AnythingLLM API
    try:
        # 優先使用討論專屬workspace，如果沒有提供room_code則創建臨時workspace
        if req.room_code and req.room_code in ROOMS:
            # 使用真實討論的專屬workspace
            room_data = ROOMS[req.room_code]
            workspace_slug = room_data.get('workspace_slug')
            if not workspace_slug:
                print(f"⚠️ 討論 {req.room_code} 沒有預設workspace，正在創建...")
                workspace_slug = await ai_client.ensure_workspace_exists(req.room_code, meeting_title)
                # 更新討論數據
                ROOMS[req.room_code]['workspace_slug'] = workspace_slug
                workspace_info = await ai_client.get_workspace_info(workspace_slug)
                if workspace_info and "id" in workspace_info:
                    ROOMS[req.room_code]['workspace_id'] = workspace_info["id"]
            else:
                print(f"✅ 使用討論專屬workspace: {workspace_slug}")
        else:
            # 備選方案：為獨立的主題生成創建臨時workspace
            print(f"📝 為獨立主題生成創建臨時workspace...")
            temp_room_code = f"topics-{hash(meeting_title) % 10000}"
            workspace_slug = await ai_client.ensure_workspace_exists(temp_room_code, meeting_title)
        
        generated_topics = await _generate_topics_from_title(meeting_title, topic_count, workspace_slug)
        return {"topics": generated_topics}

    except Exception as e:
        # 處理呼叫 AI 時可能發生的任何錯誤
        print(f"Error calling LLM for topic generation: {e}")
        return {"topics": [f"AI 服務暫時無法連線，請稍後再試。"]}

# 新增的請求模型，用於 generate_single_topic 端點
class GenerateSingleTopicRequest(BaseModel):
    room: str
    custom_prompt: str

@router.post("/generate_single_topic")
async def generate_single_topic(req: GenerateSingleTopicRequest):
    """
    根據討論室和自訂提示，使用 AI 生成單一議程主題。

    [POST] /ai/generate_single_topic

    參數：
    - room (str): 討論室代碼
    - custom_prompt (str): 自訂的提示語句，用於引導 AI 生成主題

    回傳：
    - topic (str): AI 生成的主題字串
    """
    # 檢查討論室是否存在
    if req.room not in ROOMS:
        return {"topic": "錯誤：找不到指定的討論室。"}

    room_data = ROOMS[req.room]

    # 使用prompt_builder的方法來建立 prompt
    prompt = prompt_builder.build_single_topic_generation_prompt(req.room, req.custom_prompt)
    
    if prompt.startswith("錯誤"):
        return {"topic": prompt}

    # 使用透明融合系統生成單一主題
    try:
        # 獲取討論室資訊
        room_data = ROOMS[req.room]
        room_title = room_data.get('title', f'討論室-{req.room}')
        
        # 優先使用討論創建時保存的workspace，如果不存在則創建
        workspace_slug = room_data.get('workspace_slug')
        if not workspace_slug:
            print(f"⚠️ 討論 {req.room} 沒有預設workspace，正在創建...")
            workspace_slug = await ai_client.ensure_workspace_exists(req.room, room_title)
            # 更新討論數據
            ROOMS[req.room]['workspace_slug'] = workspace_slug
            workspace_info = await ai_client.get_workspace_info(workspace_slug)
            if workspace_info and "id" in workspace_info:
                ROOMS[req.room]['workspace_id'] = workspace_info["id"]
        else:
            print(f"✅ 使用討論專屬workspace: {workspace_slug}")
        
        # 使用透明融合系統：NPU+CPU並行->NPU融合
        topic = await transparent_fusion.process_request(
            prompt, workspace_slug, task_type="single_topic"
        )
        return {"topic": topic.strip()}
    except HTTPException:
        raise
    except Exception as e:
        return {"topic": f"AI 主題生成失敗: {str(e)}"}

# 透明融合系統管理端點
@router.get("/fusion/status")
async def get_fusion_status():
    """獲取透明融合系統狀態"""
    stats = transparent_fusion.get_stats()
    health = transparent_fusion.get_health_status()
    return {
        "fusion_enabled": transparent_fusion.is_fusion_enabled(),
        "status": "運行中" if transparent_fusion.is_fusion_enabled() else "已禁用",
        "statistics": stats,
        "health": health,
        "message": "Snapdragon Elite X透明融合：NPU+CPU並行->NPU融合，用戶無感知質量提升"
    }

@router.post("/fusion/toggle")
async def toggle_fusion(enable: bool = True):
    """切換融合系統狀態（管理員功能）"""
    if enable:
        transparent_fusion.enable_fusion()
        message = "透明融合系統已啟用 - Snapdragon Elite X: NPU+CPU並行->NPU融合推理"
    else:
        transparent_fusion.disable_fusion()
        message = "融合系統已禁用 - 回退到單一NPU模式"
    
    return {
        "status": "success",
        "fusion_enabled": transparent_fusion.is_fusion_enabled(),
        "message": message,
        "note": "API格式保持完全不變，用戶感知不到任何差異",
        "platform": "Snapdragon Elite X優化"
    }

# CPU模型管理端點
@router.post("/cpu_model/load")
async def load_cpu_model(model_name: str = "phi3-mini"):
    """加載CPU模型（Snapdragon Elite X優化）"""
    try:
        success = await local_llm_client.load_model(model_name=model_name)
        if success:
            model_info = local_llm_client.get_model_info()
            return {
                "status": "success",
                "message": f"CPU模型 {model_name} 加載成功",
                "model_info": model_info,
                "platform_optimization": "Snapdragon Elite X - 8核心CPU優化"
            }
        else:
            return {
                "status": "error",
                "message": f"CPU模型 {model_name} 加載失敗"
            }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"CPU模型加載錯誤: {str(e)}"
        }

@router.post("/cpu_model/download")
async def download_cpu_model(model_name: str = "phi3-mini"):
    """從Hugging Face下載CPU模型"""
    try:
        model_path = await local_llm_client.download_model(model_name)
        return {
            "status": "success",
            "message": f"模型 {model_name} 下載完成",
            "model_path": model_path,
            "supported_models": list(local_llm_client.supported_models.keys())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"模型下載失敗: {str(e)}"
        }

@router.get("/cpu_model/info")
async def get_cpu_model_info():
    """獲取CPU模型信息"""
    return {
        "model_info": local_llm_client.get_model_info(),
        "supported_models": local_llm_client.supported_models,
        "platform": "Snapdragon Elite X"
    }

@router.post("/cpu_model/test")
async def test_cpu_model():
    """測試CPU模型推理功能"""
    try:
        result = await local_llm_client.test_generation()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 融合系統高級管理端點
@router.post("/fusion/cache/clear")
async def clear_fusion_cache():
    """清空融合系統緩存"""
    transparent_fusion.clear_cache()
    return {
        "status": "success",
        "message": "融合系統緩存已清空"
    }

@router.post("/fusion/stats/reset")
async def reset_fusion_stats():
    """重置融合系統統計"""
    transparent_fusion.reset_stats()
    return {
        "status": "success",
        "message": "融合系統統計已重置"
    }

@router.get("/fusion/health")
async def get_fusion_health():
    """獲取融合系統健康狀況"""
    health = transparent_fusion.get_health_status()
    return {
        "system": "透明融合引擎",
        "platform": "Snapdragon Elite X",
        "architecture": "NPU+CPU並行 -> NPU融合推理",
        "health": health,
        "timestamp": time.time()
    }

class CleanTempTopicsRequest(BaseModel):
    """清理臨時主題的請求模型"""
    room: str

@router.post("/clean_temp_topics")
async def clean_temp_topics(req: CleanTempTopicsRequest):
    """
    清理討論室中的臨時主題（如 "AI 主題生成中..." 等）

    [POST] /ai/clean_temp_topics

    參數：
    - room (str): 討論室代碼

    回傳：
    - success (bool): 是否成功清理
    - cleaned_topics (list[str]): 被清理的主題列表
    - message (str): 操作結果訊息
    """
    # 檢查討論室是否存在
    if req.room not in ROOMS:
        raise HTTPException(status_code=404, detail="找不到指定的討論室")

    # 定義需要清理的臨時主題關鍵字
    temp_topic_keywords = [
        "AI 主題生成中...",
        "AI 主題生成中",
        "AI 產生中...",
        "AI 產生中",
        "載入中...",
        "載入中"
    ]

    cleaned_topics = []
    
    try:
        # 獲取該討論室的所有主題
        room_topics = [
            topic_id for topic_id in topics.keys() 
            if topic_id.startswith(f"{req.room}_")
        ]
        
        # 檢查並清理臨時主題
        for topic_id in room_topics:
            topic_name = topic_id.replace(f"{req.room}_", "")
            
            # 檢查是否為臨時主題
            if any(keyword in topic_name for keyword in temp_topic_keywords):
                # 清理該主題的留言
                if topic_id in topics:
                    del topics[topic_id]
                
                # 清理該主題的投票記錄
                votes_to_delete = [
                    vote_id for vote_id in votes.keys()
                    if vote_id.startswith(f"{topic_id}_")
                ]
                for vote_id in votes_to_delete:
                    del votes[vote_id]
                
                cleaned_topics.append(topic_name)
                print(f"✅ 已清理臨時主題: {topic_name}")
        
        if cleaned_topics:
            return {
                "success": True,
                "cleaned_topics": cleaned_topics,
                "message": f"成功清理 {len(cleaned_topics)} 個臨時主題"
            }
        else:
            return {
                "success": True,
                "cleaned_topics": [],
                "message": "沒有找到需要清理的臨時主題"
            }
    
    except Exception as e:
        print(f"❌ 清理臨時主題時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"清理臨時主題失敗: {str(e)}"
        )