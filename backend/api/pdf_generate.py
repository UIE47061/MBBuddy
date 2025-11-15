# backend/api/pdf_generate.py
import io
import time
import datetime
from urllib.parse import quote
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import navy, gray

def export_room_pdf(room, room_data, room_topics, votes, FONT_NAME):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=(595.27, 841.89),  # letter
        rightMargin=50, 
        leftMargin=50,
        topMargin=60, 
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleStyle', fontName=FONT_NAME, fontSize=24, alignment=TA_CENTER, spaceAfter=20, textColor=navy, leading=30
    ))
    styles.add(ParagraphStyle(
        name='InfoBoxStyle', fontName=FONT_NAME, fontSize=10, alignment=TA_LEFT, spaceAfter=20, backColor="#F2F6FC",
        borderWidth=1, borderColor="#D4E0F4", borderPadding=10, leading=14
    ))
    styles.add(ParagraphStyle(
        name='HeaderStyle', fontName=FONT_NAME, fontSize=18, spaceBefore=10, spaceAfter=12, textColor=navy,
        borderColor=navy, borderWidth=0, borderPadding=5, borderRadius=5, leading=22
    ))
    styles.add(ParagraphStyle(
        name='SubHeaderStyle', fontName=FONT_NAME, fontSize=13, spaceAfter=8, textColor=gray, leading=16
    ))
    styles.add(ParagraphStyle(
        name='BodyStyle', fontName=FONT_NAME, fontSize=11, leading=16, alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        name='CommentStyle', fontName=FONT_NAME, fontSize=10, leading=14, leftIndent=20, spaceBefore=5,
        borderWidth=0.5, borderColor="#EEEEEE", borderPadding=5, backColor="#FAFAFA"
    ))
    styles.add(ParagraphStyle(
        name='FooterStyle', fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER, textColor=gray
    ))
    styles.add(ParagraphStyle(
        name='ChartTitleStyle', fontName=FONT_NAME, fontSize=14, alignment=TA_CENTER, spaceBefore=5, spaceAfter=5, textColor=navy
    ))
    styles.add(ParagraphStyle(
        name='LegendStyle', fontName=FONT_NAME, fontSize=11, leading=20, spaceAfter=8, alignment=TA_LEFT
    ))

    def footer(canvas, doc):
        canvas.saveState()
        footer_text = f"MBBuddy 討論系統產生於 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | 討論代碼: {room}"
        p = Paragraph(footer_text, styles["FooterStyle"])
        w, h = p.wrap(doc.width, doc.bottomMargin)
        p.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    story = []
    story.append(Paragraph(room_data.get('title', '討論記錄'), styles['TitleStyle']))
    story.append(Spacer(1, 5))
    created_time = datetime.datetime.fromtimestamp(room_data.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M')
    participants_count = len(room_data.get('participants_list', []))
    topics_count = len(room_topics)
    info_text = f"<b>討論代碼:</b> {room}<br/>"
    info_text += f"<b>建立時間:</b> {created_time}<br/>"
    info_text += f"<b>參與者數量:</b> {participants_count}<br/>"
    info_text += f"<b>主題數量:</b> {topics_count}<br/>"
    if room_data.get('topic_summary'):
        info_text += f"<br/><b>討論摘要:</b><br/>{room_data['topic_summary']}<br/>"
    if room_data.get('desired_outcome'):
        info_text += f"<br/><b>預期成果:</b><br/>{room_data['desired_outcome']}<br/>"
    story.append(Paragraph(info_text, styles['InfoBoxStyle']))
    story.append(Spacer(1, 10))
    if not room_topics:
        story.append(Paragraph("此討論尚未創建任何主題。", styles['BodyStyle']))
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buffer.seek(0)
        encoded_filename = quote(room_data.get('title', f'MBBuddy-Report-{room}'))
        return StreamingResponse(buffer, media_type='application/pdf', headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}.pdf"
        })
    story.append(Paragraph("主題目錄", styles['HeaderStyle']))
    story.append(Spacer(1, 5))
    for i, topic in enumerate(room_topics, 1):
        topic_name = topic.get('topic_name', '未命名主題')
        story.append(Paragraph(f"{i}. {topic_name}", styles['BodyStyle']))
    story.append(PageBreak())
    # --- 統計圖表頁 ---
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
    from reportlab.lib import colors as reportlab_colors

    # 統計數據
    topic_names = [t.get('topic_name', '未命名') for t in room_topics]
    topic_comment_counts = []
    topic_vote_counts = []
    topic_positive_percents = []

    for topic in room_topics:
        comments = topic.get('comments', [])
        comment_count = len(comments)
        topic_comment_counts.append(comment_count)
        good_votes = 0
        bad_votes = 0
        for comment in comments:
            comment_id = comment.get('id', '')
            if comment_id in votes:
                good_votes += len(votes[comment_id].get('good', []))
                bad_votes += len(votes[comment_id].get('bad', []))
        topic_vote_counts.append(good_votes + bad_votes)
        if good_votes + bad_votes > 0:
            positive_percent = (good_votes / (good_votes + bad_votes)) * 100
        else:
            positive_percent = 0
        topic_positive_percents.append(positive_percent)

    # 長條圖（主題留言數量）
    if topic_names and topic_comment_counts and len(topic_names) > 1:
        story.append(Paragraph("各主題留言數量比較", styles['ChartTitleStyle']))
        drawing = Drawing(450, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 350
        bc.data = [topic_comment_counts]
        bc.strokeColor = reportlab_colors.black
        bc.valueAxis.valueMin = 0
        max_count = max(topic_comment_counts) if topic_comment_counts else 0
        bc.valueAxis.valueMax = max_count + 2
        bc.valueAxis.valueStep = 1 if max_count < 10 else (max_count // 5)
        bc.categoryAxis.categoryNames = [str(i+1) for i in range(len(topic_names))]
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = -8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        bc.bars[0].fillColor = reportlab_colors.lightblue
        for i, value in enumerate(topic_comment_counts):
            label = String(bc.x + bc.width/len(topic_comment_counts) * (i + 0.5), 
                        bc.y + bc.height + 5, 
                        str(value))
            label.fontName = FONT_NAME
            label.fontSize = 8
            label.textAnchor = 'middle'
            drawing.add(label)
        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 10))
        legend_text = "主題對應表:<br/>"
        for i, name in enumerate(topic_names):
            legend_text += f"{i+1}. {name}<br/>"
        story.append(Paragraph(legend_text, styles['BodyStyle']))
        story.append(Spacer(1, 20))

    # 圓餅圖（正面評價百分比）
    if topic_names and any(topic_positive_percents) and any(v > 0 for v in topic_vote_counts):
        story.append(Paragraph("各主題正面評價百分比", styles['ChartTitleStyle']))
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 65
        pie.width = 130
        pie.height = 130
        pie.data = [p if p > 0 else 0.1 for p in topic_positive_percents]
        pie.labels = [str(i+1) for i in range(len(topic_names))]
        pie.slices.strokeWidth = 0.5
        colorscheme = [
            reportlab_colors.lightblue, reportlab_colors.lightgreen, 
            reportlab_colors.lightyellow, reportlab_colors.lightcoral,
            reportlab_colors.lightsteelblue, reportlab_colors.thistle
        ]
        for i, color in enumerate(colorscheme):
            if i < len(pie.slices):
                pie.slices[i].fillColor = color
        drawing.add(pie)
        story.append(drawing)
        story.append(Spacer(1, 10))
        legend_text = "主題正面評價百分比:<br/>"
        for i, (name, percent, color_idx) in enumerate(zip(topic_names, topic_positive_percents, range(len(topic_names)))):
            color_name = ["藍色", "綠色", "黃色", "紅色", "淺藍色", "紫色"][color_idx % 6]
            legend_text += f"{i+1}. {name} ({percent:.1f}%) - {color_name}<br/><br/>"
        story.append(Paragraph(legend_text, styles['LegendStyle']))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # --- 主題內容頁 ---
    for i, topic in enumerate(room_topics, 1):
        topic_name = topic.get('topic_name', '未命名主題')
        story.append(Paragraph(f"主題 {i}: {topic_name}", styles['HeaderStyle']))
        story.append(Spacer(1, 8))
        comments = topic.get('comments', [])
        if not comments:
            story.append(Paragraph("此主題下沒有任何留言。", styles['BodyStyle']))
        else:
            story.append(Paragraph(f"留言數量: {len(comments)}", styles['SubHeaderStyle']))
            good_votes_total = 0
            bad_votes_total = 0
            comment_votes = []
            for comment in comments:
                comment_id = comment.get('id', '')
                good_votes = 0
                bad_votes = 0
                if comment_id in votes:
                    good_votes = len(votes[comment_id].get('good', []))
                    bad_votes = len(votes[comment_id].get('bad', []))
                    good_votes_total += good_votes
                    bad_votes_total += bad_votes
                comment_votes.append((comment, good_votes, bad_votes))
            story.append(Paragraph(f"正面評價: {good_votes_total} | 負面評價: {bad_votes_total}", styles['SubHeaderStyle']))
            story.append(Spacer(1, 10))
            # 最受歡迎留言圖（如留言數>3）
            if len(comments) > 3:
                sorted_comments = sorted(comment_votes, key=lambda x: x[1] - x[2], reverse=True)[:5]
                if sorted_comments:
                    story.append(Paragraph("本主題最受歡迎留言", styles['ChartTitleStyle']))
                    labels = []
                    good_votes = []
                    bad_votes = []
                    for comment, g_vote, b_vote in sorted_comments:
                        nickname = comment.get('nickname', '匿名')
                        content = comment.get('content', '')
                        short_content = content[:15] + '...' if len(content) > 15 else content
                        labels.append(f"{nickname}: {short_content}")
                        good_votes.append(g_vote)
                        bad_votes.append(b_vote)
                    drawing = Drawing(450, 200)
                    bc = HorizontalBarChart()
                    bc.x = 100
                    bc.y = 20
                    bc.height = 150
                    bc.width = 300
                    bc.data = [good_votes, bad_votes]
                    bc.strokeColor = reportlab_colors.black
                    bc.categoryAxis.categoryNames = labels
                    bc.categoryAxis.labels.boxAnchor = 'e'
                    bc.categoryAxis.labels.dx = -2
                    bc.valueAxis.valueMin = 0
                    max_good = max(good_votes) if good_votes else 0
                    max_bad = max(bad_votes) if bad_votes else 0
                    max_votes = max(max_good, max_bad) + 1
                    bc.valueAxis.valueMax = max_votes
                    bc.valueAxis.valueStep = 1
                    bc.bars[0].fillColor = reportlab_colors.lightgreen
                    bc.bars[1].fillColor = reportlab_colors.lightcoral
                    bc.bars.strokeWidth = 0.5
                    drawing.add(bc)
                    story.append(drawing)
                    story.append(Spacer(1, 5))
                    story.append(Paragraph("綠色: 正面評價 | 紅色: 負面評價", styles['SubHeaderStyle']))
                    story.append(Spacer(1, 15))
            # 留言列表
            story.append(Paragraph("留言列表:", styles['SubHeaderStyle']))
            story.append(Spacer(1, 5))
            sorted_comments = sorted(comments, key=lambda c: 
                len(votes.get(c.get('id', ''), {}).get('good', [])) - 
                len(votes.get(c.get('id', ''), {}).get('bad', [])), 
                reverse=True)
            for j, comment in enumerate(sorted_comments, 1):
                nickname = comment.get('nickname', '匿名')
                content = comment.get('content', '').replace('\n', '<br/>')
                timestamp = datetime.datetime.fromtimestamp(comment.get('ts', time.time())).strftime('%H:%M:%S')
                good_votes = len(votes.get(comment.get('id', ''), {}).get('good', []))
                bad_votes = len(votes.get(comment.get('id', ''), {}).get('bad', []))
                vote_score = good_votes - bad_votes
                bg_color = "#FAFAFA"
                if vote_score > 2:
                    bg_color = "#F0FFF0"
                elif vote_score < -2:
                    bg_color = "#FFF0F0"
                comment_style = ParagraphStyle(
                    'CommentStyle'+str(j), 
                    parent=styles['CommentStyle'],
                    backColor=bg_color
                )
                comment_text = f"<b>{j}. {nickname}</b> <font size='8'>(於 {timestamp})</font><br/>"
                comment_text += f"<font color='green'>正評: {good_votes}</font> | <font color='red'>負評: {bad_votes}</font><br/>"
                comment_text += f"{content}"
                story.append(Paragraph(comment_text, comment_style))
                story.append(Spacer(1, 5))
        story.append(PageBreak())
    # 最後產生 PDF
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    meeting_title = room_data.get('title', f'MBBuddy-Report-{room}')
    encoded_filename = quote(meeting_title)
    return StreamingResponse(buffer, media_type='application/pdf', headers={
        'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}.pdf",
        'Access-Control-Allow-Origin': '*'
    })
