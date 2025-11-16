"""
AI Prompt 構建模組
負責構建各種 AI 任務的 prompt，包括主題生成、總結等
"""

import json
import re
from typing import List, Dict, Any, Optional
from .participants_api import ROOMS, topics, votes

class PromptBuilder:
    """AI Prompt 構建器"""
    
    @staticmethod
    def build_summary_prompt(room: str, topic: str) -> str:
        """
        構建討論總結的 prompt
        
        Args:
            room: 討論室代碼
            topic: 要總結的主題名稱
        
        Returns:
            構建好的 prompt 字串
        """
        # 檢查討論室是否存在
        if room not in ROOMS:
            return "錯誤：找不到指定的討論室。"

        # 組合主題 ID 並檢查主題是否存在
        topic_id = f"{room}_{topic}"
        if topic_id not in topics:
            return "錯誤：在該討論室中找不到指定的主題。"

        room_data = ROOMS[room]
        topic_data = topics[topic_id]
        
        # 開始建立 Prompt
        prompt = f"主題: {topic}\n"

        # 取得參與者列表
        participants = [p.get("nickname", "匿名") for p in room_data.get("participants_list", [])]
        if participants:
            prompt += f"參與者: {', '.join(participants)}\n"

        prompt += "\n留言與票數:\n"

        # 取得該主題的所有留言與其對應的票數
        comments_for_prompt = []
        if "comments" in topic_data:
            for c in topic_data["comments"]:
                comment_id = c.get("id")
                nickname = c.get("nickname", "匿名")
                content = c.get("content", "")
                
                # 從 votes 字典中取得票數
                good_votes = len(votes.get(comment_id, {}).get("good", []))
                bad_votes = len(votes.get(comment_id, {}).get("bad", []))

                comments_for_prompt.append(
                    f"- {nickname}：{content}（👍{good_votes}、👎{bad_votes}）"
                )

        if not comments_for_prompt:
            prompt += "目前這個主題還沒有任何留言。\n"
        else:
            prompt += "\n".join(comments_for_prompt)

        # 加上固定的指令模板
        prompt += """

                    你的任務是擔任一個專業的討論記錄員。
                    你必須嚴格根據上方提供的「留言與票數」資訊，進行條列式彙整。
                    禁止臆測或生成任何未在資料中出現的數字、名稱或觀點。
                    你的回答內容，只能包含彙整後的結果，禁止加入任何開場白、問候語或結尾的免責聲明。

                    請直接以以下格式輸出，並將真實的內容填入：
                    ---
                    1. [第一個重點主題]
                    - 主流意見：
                    - 分歧點：（若無則寫"無"）
                    - 可能決議：
                    ---
                    2. [第二個重點主題]
                    - 主流意見：
                    - 分歧點：（若無則寫"無"）
                    - 可能決議：
                    ---
                    總結：
                    [此處條列討論的最重要共識或後續追蹤事項]
                """

        return prompt
    
    @staticmethod
    def build_topics_generation_prompt(meeting_title: str, topic_count: int) -> str:
        """
        構建主題生成的 prompt
        
        Args:
            meeting_title: 討論標題
            topic_count: 要生成的主題數量
        
        Returns:
            構建好的 prompt 字串
        """
        topic_count = max(1, min(10, topic_count))
        meeting_title = meeting_title.strip()

        if not meeting_title:
            return "錯誤：討論名稱不可為空。"

        prompt = f"""請為「{meeting_title}」討論設計 {topic_count} 個討論主題。

要求：
- 主題與「{meeting_title}」直接相關  
- 用繁體中文
- 具體可執行
- 直接以JSON陣列格式回答

回答格式：["主題一", "主題二", "主題三"]

請立即生成 {topic_count} 個主題："""

        return prompt
    
    @staticmethod
    def build_single_topic_generation_prompt(room: str, custom_prompt: str) -> str:
        """
        構建單個主題生成的 prompt
        
        Args:
            room: 討論室代碼
            custom_prompt: 自訂提示語句
        
        Returns:
            構建好的 prompt 字串
        """
        # 檢查討論室是否存在
        if room not in ROOMS:
            return "錯誤：找不到指定的討論室。"

        room_data = ROOMS[room]

        # 開始建立 Prompt
        prompt = f"討論名稱: {room_data.get('title', '未命名討論')}\n"
        prompt += f"討論代碼: {room}\n"
        
        # 添加討論描述/摘要（如果有）
        if room_data.get('topic_summary'):
            prompt += f"討論摘要: {room_data['topic_summary']}\n"
        if room_data.get('desired_outcome'):
            prompt += f"預期成果: {room_data['desired_outcome']}\n"
        
        # 取得參與者列表
        participants = [p.get("nickname", "匿名") for p in room_data.get("participants_list", [])]
        if participants:
            prompt += f"參與者: {', '.join(participants)}\n"
        
        # 找出該討論室的所有已有主題
        existing_topics = [
            t["topic_name"] for t_id, t in topics.items() 
            if t["room_id"] == room and "topic_name" in t
        ]
        
        if existing_topics:
            prompt += "\n已有的主題:\n"
            for i, topic_name in enumerate(existing_topics, 1):
                prompt += f"{i}. {topic_name}\n"
            
            prompt += "\n請生成一個與已有主題互補但不重複的新議程主題。主題應該既要與討論整體目標相關，又能夠覆蓋尚未討論的重要方面。"
        else:
            prompt += "\n目前討論尚未有任何主題。請生成一個適合作為第一個討論主題的議程。"

        # 加上使用者自訂的提示
        if custom_prompt:
            prompt += f"\n\n自訂提示: {custom_prompt}"
        
        prompt += "\n\n請直接返回一個簡潔、具體且不超過10個字的主題，不需要任何前綴或解釋。"

        return prompt

class TopicParser:
    """主題解析器，處理AI回覆的解析"""
    
    @staticmethod
    def flatten_and_clean_topics(items):
        """遞迴函式，用於攤平所有可能的巢狀結構"""
        if not isinstance(items, list):
            return []
        
        flat_list = []
        for item in items:
            # 如果項目是列表，遞迴攤平
            if isinstance(item, list):
                flat_list.extend(TopicParser.flatten_and_clean_topics(item))
            # 如果項目是字串
            elif isinstance(item, str):
                # 去除頭尾空白
                item = item.strip()
                # 嘗試將其視為 JSON 進行解析
                if item.startswith('[') and item.endswith(']'):
                    try:
                        nested_list = json.loads(item)
                        flat_list.extend(TopicParser.flatten_and_clean_topics(nested_list))
                    except json.JSONDecodeError:
                        # 解析失敗，當作普通字串，但過濾空值
                        if item:
                            flat_list.append(item)
                # 如果是普通字串，過濾空值
                elif item:
                    flat_list.append(item)
        return flat_list
    
    @staticmethod
    def parse_topics_from_response(raw_text: str, topic_count: int) -> List[str]:
        """
        從AI回覆中解析主題列表，增強過濾邏輯
        支援陣列格式 ["主題1", "主題2"] 和物件格式 {"主題一": "...", "主題二": "..."}
        
        Args:
            raw_text: AI的原始回覆
            topic_count: 期望的主題數量
        
        Returns:
            解析出的主題列表
        """
        import re
        import json
        
        print(f"原始回覆長度: {len(raw_text)}, 內容預覽: {raw_text[:200]}")
        
        # 預先清理：移除常見的無效內容
        cleaned_text = raw_text
        
        # 移除聊天模板標記
        cleaned_text = re.sub(r'<\|[^|]*\|>', '', cleaned_text)
        
        # 移除 Markdown 代碼塊
        cleaned_text = re.sub(r'```(json)?\s*', '', cleaned_text)
        cleaned_text = cleaned_text.strip('`').strip()
        
        # 移除常見的無效詞語
        invalid_patterns = [
            r'\bjson\b',           # 單獨的 "json" 詞
            r'\b範例\b',           # "範例" 詞
            r'\b例如\b',           # "例如" 詞  
            r'\b格式\b',           # "格式" 詞
            r'^\s*正確範例.*$',     # 整行範例說明
            r'^\s*錯誤範例.*$',     # 整行錯誤說明
        ]
        
        for pattern in invalid_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.MULTILINE | re.IGNORECASE)
        
        generated_topics = []
        
        try:
            # 步驟 1: 嘗試解析 JSON（陣列或物件）
            # 先找陣列
            array_start = cleaned_text.find('[')
            array_end = cleaned_text.rfind(']') + 1
            
            # 再找物件
            obj_start = cleaned_text.find('{')
            obj_end = cleaned_text.rfind('}') + 1
            
            json_str = None
            is_object = False
            
            # 判斷哪個 JSON 結構先出現
            if array_start != -1 and (obj_start == -1 or array_start < obj_start):
                json_str = cleaned_text[array_start:array_end]
                is_object = False
            elif obj_start != -1:
                json_str = cleaned_text[obj_start:obj_end]
                is_object = True
            
            if json_str:
                parsed_data = json.loads(json_str)
                
                if is_object and isinstance(parsed_data, dict):
                    # 物件格式：提取所有值
                    print(f"✅ 解析到物件格式，鍵值對數量: {len(parsed_data)}")
                    generated_topics = [str(value) for value in parsed_data.values() if value]
                else:
                    # 陣列格式：使用遞迴函式進行徹底的攤平與清理
                    print(f"✅ 解析到陣列格式")
                    generated_topics = TopicParser.flatten_and_clean_topics(parsed_data)
            else:
                raise ValueError("找不到 JSON 結構")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ JSON 解析失敗: {e}，使用備用方案")
            # 備用方案：按行分割並清理
            lines = cleaned_text.split('\n')
            
            for line in lines:
                line = line.strip().lstrip('-*').lstrip('123456789.').strip()
                # 過濾掉空行和無效內容
                if (line and 
                    line not in ['[', ']', ',', '{', '}'] and 
                    not line.lower().startswith(('json', '範例', '例如', '格式')) and
                    len(line) > 3):  # 主題至少要3個字符
                    generated_topics.append(line)
        
        # 最終清理：確保主題質量
        final_topics = []
        for topic in generated_topics:
            if isinstance(topic, str):
                topic = topic.strip(' "\',:')  # 移除多餘的引號、空格、逗號、冒號
                # 過濾掉明顯的無效主題
                invalid_topics = [
                    'json', '範例', '例如', '格式', 'example',
                    '請回答', '主題', '討論', '生成'
                ]
                
                # 移除 "主題一"、"主題二" 這類前綴
                topic = re.sub(r'^(主題|议题|議題)[一二三四五六七八九十\d]+[:：]?\s*', '', topic)
                
                if (len(topic) >= 4 and 
                    topic.lower() not in invalid_topics and
                    not topic.startswith(('[', '{')) and 
                    not topic.endswith((']', '}')) and
                    not any(invalid in topic.lower() for invalid in ['請回答', '格式'])):
                    final_topics.append(topic)
        
        print(f"✅ 最終解析出 {len(final_topics)} 個主題: {final_topics}")
        return final_topics[:topic_count]

# 全局實例
prompt_builder = PromptBuilder()
topic_parser = TopicParser()
