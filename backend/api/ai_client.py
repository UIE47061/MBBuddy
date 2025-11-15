"""
AI 客戶端模組
負責與 AnythingLLM API 的實際交互，包括工作區管理和聊天調用
"""

import httpx
import re
from fastapi import HTTPException
from typing import Optional, Dict, Any
from .ai_config import ai_config

class AIClient:
    """AnythingLLM API 客戶端"""
    
    def __init__(self):
        self.config = ai_config
    
    def filter_thinking_tags(self, text: str, debug_mode: bool = False) -> str:
        """
        過濾思考型模型回覆中的 <think> 標籤和思考內容
        
        Args:
            text: 包含可能的 <think> 標籤的原始回覆
            debug_mode: 如果為 True，保留思考內容用於調試
        
        Returns:
            過濾後的純回覆內容
        """
        if not text:
            return text
        
        # 調試模式下保留思考內容
        if debug_mode or self.config.debug_thinking:
            print(f"調試模式：保留思考內容，原始回覆長度: {len(text)}")
            return text
        
        # 使用正則表達式移除 <think>...</think> 標籤及其內容
        pattern = r'<think>.*?</think>'
        filtered_text = re.sub(pattern, '', text, flags=re.DOTALL)
        
        # 清理多餘的空白字符和換行符
        filtered_text = filtered_text.strip()
        
        # 移除開頭的多餘換行符
        while filtered_text.startswith('\n'):
            filtered_text = filtered_text[1:]
        
        print(f"原始回覆長度: {len(text)}, 過濾後長度: {len(filtered_text)}")
        
        return filtered_text
    
    async def ensure_workspace_exists(self, room_code: str, room_title: str) -> str:
        """
        確保指定討論室的工作區存在，如果不存在則創建
        
        Args:
            room_code: 討論室代碼
            room_title: 討論室名稱
        
        Returns:
            工作區的slug
        
        Raises:
            HTTPException: 當操作失敗時
        """
        if not self.config.api_key:
            raise HTTPException(status_code=500, detail="未配置 AnythingLLM API Key")
        
        # 生成工作區slug（使用討論室代碼，確保唯一性）
        workspace_slug = f"MBBuddy-{room_code.lower()}"
        
        try:
            # 1. 檢查工作區是否已存在（通過列出所有工作區）
            list_response = await self.config.httpx_client.get(
                self.config.get_workspaces_url(),
                headers=self.config.headers
            )
            
            workspace_exists = False
            if list_response.status_code == 200:
                workspaces_data = list_response.json()
                existing_workspaces = workspaces_data.get("workspaces", [])
                
                for ws in existing_workspaces:
                    if ws.get("slug") == workspace_slug:
                        print(f"工作區 '{workspace_slug}' 已存在 (ID: {ws.get('id')})")
                        workspace_exists = True
                        break
            
            if workspace_exists:
                return workspace_slug
            
            # 2. 如果不存在，創建新工作區
            print(f"工作區 '{workspace_slug}' 不存在，開始創建...")
            create_payload = {
                "name": f"MBBuddy-{room_title}"
            }
            
            create_response = await self.config.httpx_client.post(
                self.config.get_create_workspace_url(),
                headers=self.config.headers,
                json=create_payload
            )
            
            if create_response.status_code == 200:
                result = create_response.json()
                # 根據AnythingLLM API的響應格式提取工作區信息
                if "workspace" in result:
                    created_workspace = result["workspace"]
                    created_slug = created_workspace.get("slug", workspace_slug)
                    print(f"成功創建工作區 '{created_slug}' (ID: {created_workspace.get('id')}) 用於討論: {room_title}")
                    print(f"響應訊息: {result.get('message', 'Workspace created')}")
                    return created_slug
                else:
                    print(f"成功創建工作區，響應: {result}")
                    return workspace_slug
            else:
                error_detail = f"創建工作區失敗: {create_response.status_code}"
                try:
                    error_data = create_response.json()
                    error_detail += f" - {error_data.get('message', '未知錯誤')}"
                except:
                    error_detail += f" - {create_response.text}"
                raise HTTPException(status_code=500, detail=error_detail)
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=500, detail="AnythingLLM API 請求超時")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"AnythingLLM API 連接錯誤: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"確保工作區存在時發生未知錯誤: {str(e)}")
    
    async def get_workspace_info(self, workspace_slug: str) -> dict:
        """
        獲取workspace的詳細信息，包括ID
        
        Args:
            workspace_slug: workspace的slug
            
        Returns:
            workspace的詳細信息字典，包括id
        """
        try:
            response = await self.config.httpx_client.get(
                self.config.get_workspaces_url(),
                headers=self.config.headers
            )
            
            if response.status_code == 200:
                workspaces_data = response.json()
                existing_workspaces = workspaces_data.get("workspaces", [])
                
                for ws in existing_workspaces:
                    if ws.get("slug") == workspace_slug:
                        return ws
                        
            return None
        except Exception as e:
            print(f"獲取workspace信息失敗: {e}")
            return None
    
    async def call_chat_api(self, message: str, workspace_slug: str = None, mode: str = "chat") -> str:
        """
        調用 AnythingLLM 的聊天 API
        
        Args:
            message: 要發送的訊息
            workspace_slug: 工作區slug，如果未提供則使用預設
            mode: 聊天模式 (chat, query, 等)
        
        Returns:
            AI 的回覆文字
        
        Raises:
            HTTPException: 當 API 調用失敗時
        """
        if not self.config.api_key:
            raise HTTPException(status_code=500, detail="未配置 AnythingLLM API Key")
        
        # 如果沒有提供workspace_slug，使用預設的
        if not workspace_slug:
            workspace_slug = self.config.workspace_slug
        
        payload = {
            "message": message,
            "mode": mode
        }
        
        try:
            response = await self.config.httpx_client.post(
                self.config.get_workspace_url(workspace_slug),
                headers=self.config.headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = f"AnythingLLM API 錯誤: {response.status_code}"
                try:
                    error_data = response.json()
                    error_detail += f" - {error_data.get('message', '未知錯誤')}"
                except:
                    pass
                raise HTTPException(status_code=500, detail=error_detail)
            
            result = response.json()
            
            # 提取回覆文字（根據 AnythingLLM 的回覆格式調整）
            print(f"AnythingLLM 回覆: {result}")  # 調試日誌
            
            # 檢查是否有錯誤
            if "error" in result and result["error"]:
                raise HTTPException(status_code=500, detail=f"AnythingLLM 錯誤: {result['error']}")
            
            raw_response = ""
            if "textResponse" in result and result["textResponse"]:
                raw_response = result["textResponse"]
            elif "message" in result:
                raw_response = result["message"]
            elif "response" in result:
                raw_response = result["response"]
            else:
                # 如果找不到預期的欄位，返回整個回覆
                raw_response = str(result)
            
            # 過濾思考型模型的 <think> 標籤
            filtered_response = self.filter_thinking_tags(raw_response)
            return filtered_response
                
        except httpx.TimeoutException as e:
            print(f"AnythingLLM API 超時: {e}")
            raise HTTPException(status_code=500, detail="AnythingLLM API 請求超時")
        except httpx.RequestError as e:
            print(f"AnythingLLM 請求錯誤: {e}")
            print(f"請求URL: {self.config.get_workspace_url(workspace_slug)}")
            raise HTTPException(status_code=500, detail=f"AnythingLLM API 連接錯誤: {str(e)}")
        except Exception as e:
            print(f"AnythingLLM 未知錯誤: {e}")
            raise HTTPException(status_code=500, detail=f"調用 AnythingLLM API 時發生未知錯誤: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """測試AnythingLLM連接"""
        try:
            response = await self.config.httpx_client.get(
                self.config.get_workspaces_url(),
                headers=self.config.headers
            )
            
            if response.status_code == 200:
                workspaces = response.json()
                return {
                    "status": "success", 
                    "message": "成功連接到AnythingLLM",
                    "workspaces": workspaces.get("workspaces", [])
                }
            else:
                return {
                    "status": "error", 
                    "message": f"連接失敗: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {"status": "error", "message": f"連接錯誤: {str(e)}"}

# 全局客戶端實例
ai_client = AIClient()
