from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import tempfile
from datetime import datetime
import json
from typing import Optional
from .participants_api import ROOMS, topics, votes
from .transparent_fusion import transparent_fusion
from .ai_client import ai_client

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])

class MindMapRequest(BaseModel):
    """心智圖生成請求模型"""
    room_code: Optional[str] = None  # 討論室代碼,如果提供則從討論室生成
    custom_content: Optional[str] = None  # 自訂內容,如果沒有討論室則使用

def build_mindmap_prompt(room_code: str) -> str:
    """構建心智圖生成的 prompt"""
    if room_code not in ROOMS:
        return None
    
    room_data = ROOMS[room_code]
    prompt = f"""請為以下討論室的內容生成一個結構化的心智圖 Markdown 格式總結。"""
    
    # 獲取所有主題及其討論內容
    room_topics = [(t_id, t) for t_id, t in topics.items() if t["room_id"] == room_code]
    
    if not room_topics:
        prompt += "目前討論室還沒有任何主題。\n"
        return prompt
    
    prompt += "討論主題與內容:\n\n"
    
    for topic_id, topic_data in room_topics:
        topic_name = topic_data.get("topic_name", "未命名主題")
        prompt += f"## 主題: {topic_name}\n\n"
        
        # 添加留言
        if "comments" in topic_data and topic_data["comments"]:
            prompt += "留言:\n"
            for comment in topic_data["comments"]:
                comment_id = comment.get("id")
                nickname = comment.get("nickname", "匿名")
                content = comment.get("content", "")
                
                # 獲取票數
                good_votes = len(votes.get(comment_id, {}).get("good", []))
                bad_votes = len(votes.get(comment_id, {}).get("bad", []))
                
                prompt += f"- {nickname}: {content} (👍{good_votes} 👎{bad_votes})\n"
            prompt += "\n"
    
    prompt += """
請根據以上內容,生成一個結構化的心智圖 Markdown 格式:

要求:
1. 使用 # 作為主標題 (主題列表)
2. 使用 ## 作為次級標題 (各個討論主題)
3. 使用 - 作為要點列表 (重要觀點、共識、分歧點)
4. 內容要精煉、結構清晰
5. 突出重點和共識
6. 標注有爭議的觀點
7. 使用繁體中文

範例格式:
# 討論主題名稱
## 主題一
- 主要觀點1
- 主要觀點2
- 共識: xxx
## 主題二  
- 重點1
- 重點2
- 分歧: xxx

請直接輸出 Markdown 格式,不要任何前綴說明:
"""
    
    return prompt

def parse_markdown_to_simple_structure(markdown_content):
    """將markdown文字解析為簡單結構以便測試"""
    lines = markdown_content.strip().split('\n')
    structure = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('# ').strip()
            structure.append({
                'level': level,
                'title': title,
                'type': 'heading'
            })
        elif line.startswith('-'):
            content = line.lstrip('- ').strip()
            structure.append({
                'level': 0,
                'title': content,
                'type': 'item'
            })
    
    return structure

def calculate_text_width(text, font_size):
    """計算文字寬度的更精確方法"""
    # 根據不同字符類型計算寬度
    chinese_chars = len([c for c in text if ord(c) > 127])
    english_chars = len(text) - chinese_chars
    
    # 中文字符比英文字符更寬
    chinese_width = chinese_chars * font_size * 0.9
    english_width = english_chars * font_size * 0.6
    
    return chinese_width + english_width

def wrap_text(text, max_width, font_size):
    """將長文字分行顯示"""
    if calculate_text_width(text, font_size) <= max_width:
        return [text]
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if calculate_text_width(test_line, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [text]

def create_simple_svg_mindmap(structure):
    """創建向右延伸的優美SVG心智圖"""
    width = 1200
    height = 800
    
    # 定義顏色主題
    colors = {
        'background': '#f8fffe',
        'main': '#2e7d6b',
        'level1': '#4a9b8e',
        'level2': '#7bb3a9',
        'level3': '#a8cdc4',
        'text': '#1a4037',
        'line': '#4a9b8e'
    }
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="mainGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:{colors['main']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{colors['level1']};stop-opacity:1" />
        </linearGradient>
        <linearGradient id="branchGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:{colors['level1']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{colors['level2']};stop-opacity:1" />
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <style>
        .main-title {{ font-family: 'Arial', sans-serif; font-size: 18px; font-weight: bold; fill: white; }}
        .branch-title {{ font-family: 'Arial', sans-serif; font-size: 14px; font-weight: 600; fill: white; }}
        .item-text {{ font-family: 'Arial', sans-serif; font-size: 11px; fill: {colors['text']}; }}
        .connector {{ stroke: {colors['line']}; stroke-width: 2; fill: none; }}
    </style>
    
    <!-- 背景 -->
    <rect width="{width}" height="{height}" fill="{colors['background']}"/>
'''
    
    # 處理結構數據並創建佈局
    main_topics = []
    current_topic = None
    
    for item in structure:
        if item['type'] == 'heading':
            if item['level'] == 1:
                current_topic = {
                    'title': item['title'],
                    'subtopics': [],
                    'items': []
                }
                main_topics.append(current_topic)
            elif item['level'] == 2 and current_topic:
                subtopic = {
                    'title': item['title'],
                    'items': []
                }
                current_topic['subtopics'].append(subtopic)
        elif item['type'] == 'item' and current_topic:
            if current_topic['subtopics']:
                current_topic['subtopics'][-1]['items'].append(item['title'])
            else:
                current_topic['items'].append(item['title'])
    
    # 如果沒有找到結構化數據，創建一個預設結構
    if not main_topics:
        main_topics = [{
            'title': '人工智慧的未來',
            'subtopics': [
                {
                    'title': '技術發展',
                    'items': ['機器學習進步', '深度學習突破', '自然語言處理']
                },
                {
                    'title': '應用領域',
                    'items': ['醫療診斷', '智能交通', '金融科技']
                }
            ],
            'items': []
        }]
    
    # 繪製主要標題（左側）
    if main_topics:
        main_topic = main_topics[0]
        main_y = height // 2
        main_x = 100
        
        # 主標題框 - 使用更精確的文字寬度計算
        main_title_lines = wrap_text(main_topic['title'], 300, 18)
        title_width = max(160, max(calculate_text_width(line, 18) for line in main_title_lines) + 40)
        title_height = max(50, len(main_title_lines) * 22 + 10)
        
        svg_content += f'''
    <!-- 主標題 -->
    <rect x="{main_x - title_width//2}" y="{main_y - title_height//2}" 
          width="{title_width}" height="{title_height}" 
          fill="url(#mainGrad)" rx="25" filter="url(#shadow)"/>
'''
        
        # 渲染多行文字
        for i, line in enumerate(main_title_lines):
            line_y = main_y - (len(main_title_lines) - 1) * 11 + i * 22
            svg_content += f'<text x="{main_x}" y="{line_y + 5}" text-anchor="middle" class="main-title">{line}</text>\n'
        
        # 繪製分支主題
        branch_start_x = main_x + title_width//2 + 50
        total_branches = len(main_topic['subtopics'])
        
        if total_branches > 0:
            branch_spacing = min(150, (height - 200) // total_branches)
            start_y = main_y - (total_branches - 1) * branch_spacing // 2
            
            for i, subtopic in enumerate(main_topic['subtopics']):
                branch_y = start_y + i * branch_spacing
                # 使用更精確的文字寬度計算和文字換行
                branch_title_lines = wrap_text(subtopic['title'], 200, 14)
                branch_width = max(120, max(calculate_text_width(line, 14) for line in branch_title_lines) + 30)
                branch_height = max(35, len(branch_title_lines) * 18 + 10)
                
                # 連接線
                svg_content += f'''
    <path d="M {main_x + title_width//2} {main_y} Q {branch_start_x - 20} {main_y} {branch_start_x - 20} {branch_y}" class="connector"/>
    <line x1="{branch_start_x - 20}" y1="{branch_y}" x2="{branch_start_x}" y2="{branch_y}" class="connector"/>
'''
                
                # 分支標題框
                svg_content += f'''
    <rect x="{branch_start_x}" y="{branch_y - branch_height//2}" 
          width="{branch_width}" height="{branch_height}" 
          fill="url(#branchGrad)" rx="17" filter="url(#shadow)"/>
'''
                
                # 渲染多行分支標題文字
                for j, line in enumerate(branch_title_lines):
                    line_y = branch_y - (len(branch_title_lines) - 1) * 9 + j * 18
                    svg_content += f'<text x="{branch_start_x + branch_width//2}" y="{line_y + 4}" text-anchor="middle" class="branch-title">{line}</text>\n'
                
                # 繪製子項目
                item_start_x = branch_start_x + branch_width + 30
                for j, item in enumerate(subtopic['items'][:5]):  # 限制顯示5個項目
                    item_y = branch_y + (j - 2) * 30  # 增加間距以容納多行文字
                    # 使用更精確的文字寬度計算和文字換行
                    item_lines = wrap_text(item, 150, 11)
                    item_width = max(100, max(calculate_text_width(line, 11) for line in item_lines) + 20)
                    item_height = max(20, len(item_lines) * 14 + 6)
                    
                    # 連接線到項目
                    svg_content += f'''
    <line x1="{branch_start_x + branch_width}" y1="{branch_y}" x2="{item_start_x}" y2="{item_y}" class="connector" stroke-width="1"/>
'''
                    
                    # 項目框
                    svg_content += f'''
    <rect x="{item_start_x}" y="{item_y - item_height//2}" 
          width="{item_width}" height="{item_height}" 
          fill="{colors['level3']}" stroke="{colors['level2']}" stroke-width="1" rx="10" opacity="0.9"/>
'''
                    
                    # 渲染多行項目文字
                    for k, line in enumerate(item_lines):
                        line_y = item_y - (len(item_lines) - 1) * 7 + k * 14
                        svg_content += f'<text x="{item_start_x + 10}" y="{line_y + 3}" class="item-text">{line}</text>\n'
    
    svg_content += '</svg>'
    return svg_content

@router.post("/generate")
async def generate_mindmap(request: MindMapRequest = None):
    """生成心智圖 - 支援從討論室 AI 生成或使用自訂內容"""
    try:
        print(f"📊 收到心智圖生成請求: {request}")
        markdown_content = None
        
        # 優先使用討論室代碼生成
        if request and request.room_code:
            room_code = request.room_code
            print(f"🏠 使用討論室代碼: {room_code}")
            
            # 檢查討論室是否存在
            if room_code not in ROOMS:
                print(f"❌ 找不到討論室: {room_code}")
                raise HTTPException(status_code=404, detail=f"找不到討論室: {room_code}")
            
            # 構建 prompt
            prompt = build_mindmap_prompt(room_code)
            if not prompt:
                print(f"❌ 無法構建 prompt")
                raise HTTPException(status_code=400, detail="無法構建心智圖 prompt")
            
            print(f"📝 已構建 prompt, 長度: {len(prompt)}")
            
            # 使用 AI 生成心智圖 markdown
            try:
                room_data = ROOMS[room_code]
                workspace_slug = room_data.get('workspace_slug')
                
                if not workspace_slug:
                    print(f"⚠️ 討論 {room_code} 沒有預設workspace,正在創建...")
                    workspace_slug = await ai_client.ensure_workspace_exists(
                        room_code, 
                        room_data.get('title', f'討論室-{room_code}')
                    )
                    ROOMS[room_code]['workspace_slug'] = workspace_slug
                
                print(f"🤖 使用 AI 生成心智圖 for 討論室: {room_code}, workspace: {workspace_slug}")
                markdown_content = await transparent_fusion.process_request(
                    prompt, 
                    workspace_slug, 
                    task_type="mindmap"
                )
                
                print(f"✅ AI 生成成功, markdown 長度: {len(markdown_content)}")
                
                # 清理可能的 markdown 代碼塊標記
                markdown_content = markdown_content.strip()
                if markdown_content.startswith('```'):
                    lines = markdown_content.split('\n')
                    markdown_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else markdown_content
                    print(f"🧹 已清理 markdown 代碼塊標記")
                    
            except Exception as e:
                print(f"❌ AI 生成失敗: {str(e)}, 使用預設內容")
                markdown_content = f"""# {ROOMS[room_code].get('title', '討論總結')}"""
        
        # 其次使用自訂內容
        elif request and request.custom_content:
            print(f"📄 使用自訂內容")
            markdown_content = request.custom_content
        
        # 最後嘗試從檔案讀取
        else:
            print(f"📂 嘗試從檔案讀取")
            possible_paths = [
                "frontend/public/AIresult.txt",
                "/app/frontend/public/AIresult.txt",
                "../frontend/public/AIresult.txt"
            ]
            
            file_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
            
            if file_path:
                print(f"✅ 找到檔案: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
            else:
                print(f"⚠️ 未找到檔案,使用預設示例")
                # 預設示例
                markdown_content = """# AI心智圖示例
## 人工智慧應用
- 機器學習
- 深度學習
- 自然語言處理
## 技術發展
- 神經網路
- 大型語言模型
- 電腦視覺"""
        
        print(f"🔄 開始解析 markdown...")
        # 解析markdown為簡單結構
        structure = parse_markdown_to_simple_structure(markdown_content)
        
        if not structure:
            print(f"❌ 無法解析 markdown 內容")
            raise HTTPException(status_code=400, detail="無法解析markdown內容")
        
        print(f"✅ 解析成功,結構元素數量: {len(structure)}")
        
        # 創建SVG心智圖
        print(f"🎨 開始創建 SVG...")
        svg_content = create_simple_svg_mindmap(structure)
        print(f"✅ SVG 創建成功,長度: {len(svg_content)}")
        
        # 保存到臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg', mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(svg_content)
            print(f"💾 已保存到臨時檔案: {tmp_file.name}")
            
            return FileResponse(
                tmp_file.name,
                media_type='image/svg+xml',
                filename=f'mindmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.svg'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 生成心智圖時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成心智圖時發生錯誤: {str(e)}")

@router.post("/preview")
async def preview_mindmap_markdown(request: MindMapRequest):
    """預覽心智圖的 Markdown 內容 (用於測試和調試)"""
    try:
        if not request.room_code:
            raise HTTPException(status_code=400, detail="需要提供 room_code")
        
        room_code = request.room_code
        
        if room_code not in ROOMS:
            raise HTTPException(status_code=404, detail=f"找不到討論室: {room_code}")
        
        # 構建 prompt
        prompt = build_mindmap_prompt(room_code)
        if not prompt:
            raise HTTPException(status_code=400, detail="無法構建心智圖 prompt")
        
        # 使用 AI 生成心智圖 markdown
        room_data = ROOMS[room_code]
        workspace_slug = room_data.get('workspace_slug')
        
        if not workspace_slug:
            workspace_slug = await ai_client.ensure_workspace_exists(
                room_code, 
                room_data.get('title', f'討論室-{room_code}')
            )
            ROOMS[room_code]['workspace_slug'] = workspace_slug
        
        markdown_content = await transparent_fusion.process_request(
            prompt, 
            workspace_slug, 
            task_type="mindmap"
        )
        
        # 清理可能的 markdown 代碼塊標記
        markdown_content = markdown_content.strip()
        if markdown_content.startswith('```'):
            lines = markdown_content.split('\n')
            markdown_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else markdown_content
        
        return {
            "room_code": room_code,
            "room_title": room_data.get('title'),
            "markdown": markdown_content,
            "prompt_used": prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"預覽失敗: {str(e)}")
