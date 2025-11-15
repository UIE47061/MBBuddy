from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile
from datetime import datetime
import json

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])

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
async def generate_mindmap():
    """生成心智圖"""
    try:
        # 在Docker環境中尋找AIresult.txt檔案
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
        
        if not file_path:
            # 如果找不到檔案，提供一個預設的示例
            markdown_content = """# AI心智圖示例
## 人工智慧應用
- 機器學習
- 深度學習
- 自然語言處理
## 技術發展
- 神經網路
- 大型語言模型
- 電腦視覺"""
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        
        # 解析markdown為簡單結構
        structure = parse_markdown_to_simple_structure(markdown_content)
        
        if not structure:
            raise HTTPException(status_code=400, detail="無法解析markdown內容")
        
        # 創建SVG心智圖
        svg_content = create_simple_svg_mindmap(structure)
        
        # 保存到臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg', mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(svg_content)
            
            return FileResponse(
                tmp_file.name,
                media_type='image/svg+xml',
                filename=f'mindmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.svg'
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成心智圖時發生錯誤: {str(e)}")
