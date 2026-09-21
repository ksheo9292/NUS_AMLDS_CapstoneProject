"""Create the responsible AI report PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


project_folder = Path(__file__).parent
output_file = project_folder / "responsible_ai_report.pdf"

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=25,
    textColor=colors.HexColor("#183B56"),
    spaceAfter=10,
)
subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#176B87"),
    spaceAfter=16,
)
heading_style = ParagraphStyle(
    "SectionHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=colors.HexColor("#183B56"),
    spaceBefore=9,
    spaceAfter=5,
)
body_style = ParagraphStyle(
    "ReportBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor("#263238"),
    spaceAfter=7,
)


def page_header_footer(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#183B56"))
    canvas.rect(0, height - 10 * mm, width, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(18 * mm, height - 6.7 * mm, "SMART CITY TRAFFIC INTELLIGENCE")
    canvas.setFillColor(colors.HexColor("#607D8B"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 10 * mm, "NUS SOC AI ML and Data Science Capstone")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


document = SimpleDocTemplate(
    str(output_file),
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=17 * mm,
    title="Responsible AI Report",
    author="KS Heo",
)

story = [
    Spacer(1, 8 * mm),
    Paragraph("Responsible and Sustainable AI Report", title_style),
    Paragraph("Part 3 Machine Learning and Intelligent Mobility Solution", subtitle_style),
    Paragraph("Main conclusion", heading_style),
    Paragraph(
        "The traffic-demand model may support a controlled classroom deployment simulation. "
        "However, the proxy risk classifier must not be used as a real accident-prediction model. "
        "It must first be replaced with validated incident data and reviewed by traffic-safety and data-governance specialists.",
        body_style,
    ),
    Paragraph("Data and coverage limitations", heading_style),
    Paragraph(
        "The dataset represents hourly westbound traffic on one I-94 corridor near Minneapolis-St Paul. "
        "It does not represent other roads, directions, cities, road users or transport modes. Historical patterns may change because of construction, policy, remote work, weather or other long-term changes.",
        body_style,
    ),
    Paragraph("Proxy accident-risk label", heading_style),
    Paragraph(
        "No accident dataset was supplied. The project therefore labels a record as high risk when High or Severe congestion occurs together with severe or low-visibility weather. This label is only used to demonstrate classification. High accuracy mainly shows that the model can reproduce the engineered proxy definition; it does not prove that the model can predict real accidents.",
        body_style,
    ),
]

risk_data = [
    ["Risk area", "Possible problem", "Required control"],
    ["Coverage", "One corridor and direction", "Test additional locations"],
    ["Proxy label", "Not a real accident outcome", "Use validated incident data"],
    ["Uneven errors", "Rare weather and time groups", "Check subgroup metrics"],
    ["Recommendations", "Low traffic may mean late hours", "Add practical user limits"],
    ["Drift", "Recent conditions may change", "Investigate alerts before retraining"],
]

risk_table = Table(risk_data, colWidths=[35 * mm, 62 * mm, 62 * mm], repeatRows=1)
risk_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183B56")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#EEF4F7")),
            ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#EEF4F7")),
        ]
    )
)

story.extend(
    [
        Paragraph("Main risks and controls", heading_style),
        risk_table,
        Spacer(1, 5 * mm),
        Paragraph("Bias and fairness", heading_style),
        Paragraph(
            "Errors may be higher during nighttime hours, weekends, holidays and rare severe-weather conditions because these groups contain fewer records. Overall MAE, accuracy and F1 scores may hide poor performance in smaller groups. The city should report results separately by hour band, day type and weather condition.",
            body_style,
        ),
        PageBreak(),
        Paragraph("Governance", heading_style),
        Paragraph(
            "The solution should have documented data sources, model versions, access controls, audit logs and a named owner. A human reviewer should approve model changes. The proxy classifier must not control enforcement, emergency response or public-safety decisions. A monitoring ALERT should start an investigation rather than automatic retraining or deployment.",
            body_style,
        ),
        Paragraph("Sustainability", heading_style),
        Paragraph(
            "Linear models use less computing power but produced higher prediction error. The random forest provided the best demand-prediction result, while the neural network required more training without improving on the random forest. The production team should use the smallest model that meets performance requirements and retrain only when monitoring shows a clear need.",
            body_style,
        ),
        Paragraph("Recommended actions", heading_style),
        Paragraph(
            "1. Replace the proxy label with validated accident or incident outcomes before safety use.<br/>"
            "2. Report performance for different times, weather conditions and day types.<br/>"
            "3. Add practical user constraints to travel-time recommendations.<br/>"
            "4. Require human approval for alerts, retraining and deployment.<br/>"
            "5. Keep an audit trail using model files, metrics and MLflow experiments.",
            body_style,
        ),
    ]
)

document.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)
print(output_file)
