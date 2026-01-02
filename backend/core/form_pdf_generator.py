import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, \
    TableStyle, Image, PageBreak, ListItem, ListFlowable

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


def iso_header_footer(canvas, doc, org_config):
    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        40, 820,
        f"{org_config.get('title', 'Laptop Allocation Form')} | "
        f"Doc No: {org_config.get('doc_number', 'N/A')} | "
        f"Rev: {org_config.get('revision', '01')}"
    )

    canvas.drawRightString(
        550, 820,
        f"Page {doc.page}"
    )

    canvas.drawString(40, 30, "Uncontrolled when printed")


def generate_allocation_form(allocation_data: dict, org_config: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    elements = []

    # ===== Header Table (Logo + Title) =====
    logo_cell = ""
    if org_config.get("logo_path"):
        try:
            logo_cell = Image(org_config["logo_path"], width=120, height=30)
        except Exception:
            logo_cell = "<< LOGO >>"

    header_table = Table(
        [
            [
                logo_cell,
                Paragraph(
                    f"<b>{org_config.get('title', 'Laptop Allocation Form')}</b>",
                    styles["Title"]
                )
            ]
        ],
        colWidths=[150, 300]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # ===== Document Control Block =====
    control_block = Table([
        ["Doc No", org_config.get("doc_number", "N/A"),
         "Revision", org_config.get("revision", "01")],
        ["Approved By", org_config.get("approved_by", "IT Manager"),
         "Date", datetime.now().strftime("%d-%m-%Y")],
    ], colWidths=[80, 160, 80, 130])

    control_block.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.75, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(control_block)
    elements.append(Spacer(1, 20))

    # ===== Allocation Details =====
    elements.append(Paragraph("1. Allocation Details", styles["Heading2"]))

    allocation_table = Table([
        ["Employee Name",
         f"{allocation_data['user']['first_name']} {allocation_data['user']['last_name']}"],
        ["Username", allocation_data['user']['username']],
        ["Laptop Description",
         f"{allocation_data['laptop']['brand']} {allocation_data['laptop']['model']}"],
        ["Serial Number", allocation_data['laptop']['serial_number']],
        ["Asset Tag", allocation_data['laptop']['asset_tag']],
        ["Allocation Date", format_date(allocation_data['allocation_date'])],
        ["Condition on Allocation", allocation_data['allocation_condition']],
        ["Reason for Allocation", allocation_data['reason_for_allocation']],
    ], colWidths=[180, 280])

    allocation_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
    ]))

    elements.append(allocation_table)
    elements.append(Spacer(1, 20))

    # ===== Return Details =====
    elements.append(Paragraph("2. Return Details", styles["Heading2"]))

    return_table = Table([
        ["Return Date", allocation_data.get("return_date", "")],
        ["Reason for Return", allocation_data.get("return_comment", "")],
        ["Condition on Return",
         allocation_data.get("condition_on_return", "")],
    ], colWidths=[180, 280])

    return_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
    ]))

    elements.append(return_table)
    elements.append(Spacer(1, 30))

    # ===== Signatures =====
    elements.append(Paragraph("3. Signatures", styles["Heading2"]))

    signature_table = Table(
        [
            ["Role", "Name", "Signature", "Date"],
            ["Employee", "", "", ""],
            ["IT Officer", "", "", ""],
        ],
        colWidths=[90, 140, 180, 80],
        rowHeights=[25, 50, 50]  # 👈 space to sign
    )

    signature_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.75, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    ]))

    elements.append(signature_table)

    # Force content onto a new page
    elements.append(PageBreak())

    # Section Title
    elements.append(
        Paragraph(
            "Terms and Conditions of IT Asset Allocation",
            styles["Heading1"]
        )
    )
    elements.append(Spacer(1, 15))

    # Terms list (ISO 9001:2015 & ISO 27001 aligned)
    terms_and_conditions = [
        "The employee acknowledges receipt of the assigned IT equipment and accessories in good working condition.",
        "The employee agrees to be solely responsible for the safekeeping, proper use, and care of the assigned equipment and accessories.",
        "The equipment shall be used strictly for authorized company business purposes and in accordance with organizational policies.",
        "The employee shall not install unauthorized software, alter system configurations, or disable security controls without written approval from the IT department.",
        "Loss, theft, damage, or suspected compromise of the equipment or data must be reported immediately to the IT department.",
        "The employee is responsible for protecting all company information stored or accessed on the device, including the use of passwords, encryption, and physical security measures.",
        "The organization reserves the right to monitor, audit, retrieve, or remotely secure the equipment in accordance with company policies and applicable laws.",
        "All equipment, accessories, and associated documentation must be returned upon termination of employment, reassignment, or upon request by the organization.",
        "Failure to comply with these terms and conditions may result in disciplinary action in accordance with organizational policies.",
    ]

    # Render terms as a structured ISO-style list
    elements.append(
        ListFlowable(
            [
                ListItem(
                    Paragraph(term, styles["Normal"]),
                    leftIndent=20
                )
                for term in terms_and_conditions
            ],
            bulletType="bullet",
            start="circle"
        )
    )

    elements.append(Spacer(1, 25))

    # ISO Reference Table (Strong audit signal)
    iso_reference_table = Table(
        [
            ["Standard", "Relevant Clause"],
            ["ISO 9001:2015", "7.5 – Documented Information"],
            ["ISO 9001:2015", "8.1 – Operational Planning and Control"],
            ["ISO 27001:2022", "A.5 – Information Security Policies"],
            ["ISO 27001:2022", "A.8 – Asset Management"],
            ["ISO 27001:2022", "A.6 – Organizational Controls"],
        ],
        colWidths=[200, 260]
    )

    iso_reference_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(iso_reference_table)

    # ===== Build =====
    doc.build(
        elements,
        onFirstPage=lambda c, d: iso_header_footer(c, d, org_config),
        onLaterPages=lambda c, d: iso_header_footer(c, d, org_config)
    )

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
