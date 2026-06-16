from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os
import datetime


def generate_pdf_report(case_data: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#1A237E")
    )
    story.append(Paragraph(f"CTI Intelligence Report - Case #{case_data['id']}", title_style))
    story.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Executive Summary", styles['Heading2']))
    story.append(Paragraph(case_data.get('summary', 'No summary available.'), styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Risk Assessment", styles['Heading2']))
    risk_data = [
        ["Metric", "Value"],
        ["Risk Score", f"{case_data.get('risk_score', 0)}/100"],
        ["Status", case_data.get('status', 'N/A')],
        ["User Hash", case_data.get('user_hash', 'N/A')]
    ]
    t = Table(risk_data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Specialized Analyses", styles['Heading2']))

    analysis = case_data.get('agent_analysis', {})
    story.append(Paragraph("Agent A - Psychological Profile:", styles['Heading3']))
    story.append(Paragraph(str(analysis.get('agent_a', 'Pending')), styles['Normal']))

    story.append(Paragraph("Agent B - Threat Intelligence:", styles['Heading3']))
    story.append(Paragraph(str(analysis.get('agent_b', 'Pending')), styles['Normal']))

    story.append(Paragraph("Agent C - Strategic Consolidation:", styles['Heading3']))
    story.append(Paragraph(str(analysis.get('agent_c', 'Pending')), styles['Normal']))

    doc.build(story)
    return output_path
