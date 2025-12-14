import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, \
    TableStyle, Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def format_date(date_value):
    if not date_value:
        return ""
    if isinstance(date_value, datetime):
        return date_value.strftime("%d-%m-%Y")
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        return str(date_value)


def generate_allocation_form(allocation_data: dict, org_config: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Logo ---
    if org_config.get("logo_path"):
        try:
            logo = Image(org_config["logo_path"], width=280, height=59)
            elements.append(logo)
        except Exception:
            elements.append(Paragraph("<< LOGO MISSING >>", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # --- Title ---

    elements.append(
        Paragraph(org_config.get("title", "Laptop Allocation Form"),
                  styles["Title"])
    )
    elements.append(Spacer(1, 20))

    # --- ISO Control Block ---
    control_block = Table([
        ["Doc No:", org_config.get("doc_number", "N/A"),
         "Revision:", org_config.get("revision", "01")],
        ["Approved By:", org_config.get("approved_by", "IT Manager"),
         "Date:", datetime.now().strftime("%d-%m-%Y")],
    ])
    control_block.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    elements.append(control_block)
    elements.append(Spacer(1, 20))

    # --- Allocation Info ---
    elements.append(Paragraph("<b>Allocation Details</b>", styles["Heading2"]))
    alloc_table = Table([
        ["Employee Name",
         f"{allocation_data['user']['first_name']} {allocation_data['user']['last_name']}"],
        ["Username", allocation_data['user']['username']],
        ["Laptop Description",
         f"{allocation_data['laptop']['brand']} {allocation_data['laptop']['model']}"],
        ["Laptop Serial", allocation_data['laptop']['serial_number']],
        ["Asset Tag", allocation_data['laptop']['asset_tag']],
        ["Allocation Date", format_date(allocation_data['allocation_date'])],
        ["Condition on Allocation", allocation_data['allocation_condition']],
        ["Reason for Allocation", allocation_data['reason_for_allocation']],
        ["Return Date",
         allocation_data.get('return_date', "Not yet returned")],
        ["Reason for Return", allocation_data['return_comment']],
        ["Condition on Return", allocation_data['condition_on_return']],
    ], colWidths=[150, 300])
    alloc_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(alloc_table)
    elements.append(Spacer(1, 30))

    # --- Signatures ---
    elements.append(Paragraph("<b>Signatures</b>", styles["Heading2"]))
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph("Employee: ____________________", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph("IT Officer: ____________________", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph("Manager: ____________________", styles["Normal"]))

    # --- Build PDF ---
    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    return pdf_value
