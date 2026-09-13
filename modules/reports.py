"""PDF report and certificate generators for demonstration purposes only."""
from __future__ import annotations

from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _table(rows: list[list[str]], widths=None) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FDFA")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def build_sustainability_report(summary: dict, recommendations, transactions: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = [Paragraph("Cloud Carbon Footprint Marketplace", styles["Title"]),
             Paragraph("Sustainability Report", styles["Heading2"]),
             Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", styles["Normal"]), Spacer(1, 14)]
    story += [Paragraph("Footprint summary", styles["Heading2"]), _table([
        ["Metric", "Value"], ["Total emissions", f"{summary['total_kg']:.2f} kg CO2e ({summary['total_tonnes']:.3f} tCO2e)"],
        ["Total cloud cost", f"${summary['total_cost']:.2f}"], ["Highest-emitting service", summary["top_service"]], ["Highest-emitting region", summary["top_region"]],
    ], [5*cm, 11*cm]), Spacer(1, 14)]
    story.append(Paragraph("Reduction recommendations", styles["Heading2"]))
    rec_rows = [["Recommendation", "Priority", "Est. savings"]]
    for _, rec in recommendations.head(8).iterrows():
        rec_rows.append([str(rec["title"]), str(rec["priority"]), f"{float(rec['estimated_savings_kg']):.2f} kg"])
    story += [_table(rec_rows, [10*cm, 3*cm, 3*cm]), Spacer(1, 14)]
    story.append(Paragraph("Offset transactions", styles["Heading2"]))
    tx_rows = [["Certificate", "Project", "Offset"]]
    for tx in transactions[:8]:
        tx_rows.append([tx["certificate_id"], tx["project_name"], f"{tx['offset_tonnes']:.3f} tCO2e"])
    if len(tx_rows) == 1:
        tx_rows.append(["No offsets yet", "—", "—"])
    story += [_table(tx_rows, [5*cm, 8*cm, 3*cm]), Spacer(1, 14)]
    story += [Paragraph("Methodology and limitations", styles["Heading2"]),
              Paragraph("Emissions equal energy use (kWh) multiplied by regional carbon intensity (kg CO2e/kWh).", styles["BodyText"])]
    doc.build(story)
    return buffer.getvalue()


def build_certificate(transaction: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = [Spacer(1, 40), Paragraph("CARBON-OFFSET CERTIFICATE", styles["Title"]), Spacer(1, 20),
             Paragraph("Cloud Carbon Footprint Marketplace", styles["Heading2"]), Spacer(1, 20),
             Paragraph(f"Certificate ID: <b>{transaction['certificate_id']}</b>", styles["BodyText"]),
             Paragraph(f"This certificate records an offset of <b>{transaction['offset_tonnes']:.3f} tCO2e</b> through <b>{transaction['project_name']}</b>.", styles["BodyText"]), Spacer(1, 40),
             Paragraph(f"Issued: {datetime.now().strftime('%d %b %Y')}", styles["Normal"])]
    doc.build(story)
    return buffer.getvalue()
