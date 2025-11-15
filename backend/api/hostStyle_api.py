from fastapi import APIRouter, HTTPException
import json
import os
from pathlib import Path

router = APIRouter()

# 獲取正確的文件路徑
BASE_DIR = Path(__file__).parent.parent.parent  # 回到 MBBuddy 根目錄
JSON_FILE_PATH = BASE_DIR / "frontend" / "src" / "utils" / "hostStyle.json"

@router.post("/api/update-host-style")
async def update_host_style(style_data: dict):
    try:
        # 確保目錄存在
        JSON_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入 JSON 檔案
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(style_data, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": "Host style updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/host-style")
async def get_host_style():
    try:
        if JSON_FILE_PATH.exists():
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            # 如果文件不存在，創建預設值
            default_data = {
                "version": "1.0",
                "created": "2024-08-30T00:00:00.000Z",
                "totalMeetings": 0,
                "lastUpdated": None,
                "styles": {
                    "democratic": 0, 
                    "efficient": 0, 
                    "engaging": 0, 
                    "structured": 0
                },
                "patterns": {
                    "avgParticipants": 0, 
                    "avgComments": 0, 
                    "avgInteraction": 0, 
                    "avgBalance": 0
                },
                "recentMeetings": [],
                "currentPrompt": None,
                "metadata": {
                    "hostId": "host_default", 
                    "userAgent": "MBBuddy_Host",
                    "iterationCount": 0
                }
            }
            
            # 創建文件
            JSON_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            
            return default_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))