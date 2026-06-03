import io
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

INDIGO      = colors.HexColor("#4F46E5")
INDIGO_LIGHT= colors.HexColor("#EEF2FF")
SLATE_900   = colors.HexColor("#0F172A")
SLATE_700   = colors.HexColor("#334155")
SLATE_500   = colors.HexColor("#64748B")
SLATE_200   = colors.HexColor("#E2E8F0")
SLATE_50    = colors.HexColor("#F8FAFC")
EMERALD     = colors.HexColor("#059669")
EMERALD_LIGHT = colors.HexColor("#ECFDF5")
AMBER       = colors.HexColor("#D97706")
WHITE       = colors.white

CATEGORY_COLORS = {
    "software": colors.HexColor("#6366F1"),
    "hardware": colors.HexColor("#D97706"),
    "email":    colors.HexColor("#059669"),
}
CATEGORY_LABELS = {
    "software": "Software",
    "hardware": "Hardware",
    "email":    "Email / Correo",
}


def _hex_to_rl(hex_str):
    try:
        return colors.HexColor(hex_str)
    except Exception:
        return SLATE_500


def generate_ticket_pdf(ticket):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Ticket {ticket.token}",
        author="SoporteApp",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TicketTitle",
        parent=styles["Normal"],
        fontSize=20, fontName="Helvetica-Bold",
        textColor=SLATE_900, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=SLATE_500, spaceAfter=0,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=8, fontName="Helvetica-Bold",
        textColor=SLATE_500, spaceBefore=0, spaceAfter=2,
        leading=10,
    )
    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=SLATE_900, spaceBefore=0, spaceAfter=6,
        leading=14,
    )
    value_bold = ParagraphStyle(
        "ValueBold",
        parent=value_style,
        fontName="Helvetica-Bold",
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=9, fontName="Helvetica-Bold",
        textColor=SLATE_500, spaceBefore=12, spaceAfter=6,
    )
    desc_style = ParagraphStyle(
        "Desc",
        parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=SLATE_700, leading=15, spaceAfter=6,
    )
    comment_author = ParagraphStyle(
        "CommentAuthor",
        parent=styles["Normal"],
        fontSize=9, fontName="Helvetica-Bold",
        textColor=SLATE_700,
    )
    comment_text = ParagraphStyle(
        "CommentText",
        parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=SLATE_700, leading=13,
    )

    story = []
    page_w = A4[0] - 4*cm  # usable width

    header_data = [[
        Paragraph(f"<b>TICKET DE SOPORTE</b>", ParagraphStyle(
            "hdr", parent=styles["Normal"],
            fontSize=9, fontName="Helvetica-Bold",
            textColor=WHITE,
        )),
        Paragraph(ticket.company.name, ParagraphStyle(
            "hdr2", parent=styles["Normal"],
            fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#C7D2FE"),
            alignment=TA_RIGHT,
        )),
    ]]
    header_table = Table(header_data, colWidths=[page_w/2, page_w/2])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INDIGO),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [INDIGO]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))
    story.append(Paragraph(f"<font color='#4F46E5'><b># {ticket.token}</b></font>", title_style))
    story.append(Paragraph(ticket.subject, subtitle_style))
    story.append(Spacer(1, 12))

    cat_color  = CATEGORY_COLORS.get(ticket.category, SLATE_500)
    cat_label  = CATEGORY_LABELS.get(ticket.category, ticket.category)
    stat_color = _hex_to_rl(ticket.status.color) if ticket.status else SLATE_500
    stat_name  = ticket.status.name if ticket.status else "—"
    prio_color = _hex_to_rl(ticket.priority.color) if ticket.priority else SLATE_200
    prio_name  = ticket.priority.name if ticket.priority else "Sin prioridad"

    def badge_para(text, bg_color, text_color=WHITE):
        return Paragraph(
            f"<b>{text}</b>",
            ParagraphStyle("badge", parent=styles["Normal"],
                           fontSize=8, fontName="Helvetica-Bold",
                           textColor=text_color,
                           backColor=bg_color,
                           borderPadding=(3, 6, 3, 6),
                           leading=12)
        )

    grid_data = [
        [
            Paragraph("EMPRESA", label_style),
            Paragraph("SOLICITANTE", label_style),
            Paragraph("EMAIL", label_style),
        ],
        [
            Paragraph(f"<b>{ticket.company.name}</b>", value_bold),
            Paragraph(ticket.requester_name, value_style),
            Paragraph(ticket.requester_email, value_style),
        ],
        [
            Paragraph("CATEGORÍA", label_style),
            Paragraph("ESTADO", label_style),
            Paragraph("PRIORIDAD", label_style),
        ],
        [
            badge_para(cat_label, cat_color),
            badge_para(stat_name, stat_color),
            badge_para(prio_name, prio_color),
        ],
        [
            Paragraph("FECHA CREACIÓN", label_style),
            Paragraph("FECHA CIERRE", label_style),
            Paragraph("", label_style),
        ],
        [
            Paragraph(ticket.created_at.strftime("%d/%m/%Y %H:%M"), value_style),
            Paragraph(ticket.closed_at.strftime("%d/%m/%Y %H:%M") if ticket.closed_at else "—", value_style),
            Paragraph("", value_style),
        ],
    ]

    col_w = page_w / 3
    grid_table = Table(grid_data, colWidths=[col_w, col_w, col_w])
    grid_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), SLATE_50),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 1), (-1, 1), 0.5, SLATE_200),
        ("LINEBELOW",     (0, 3), (-1, 3), 0.5, SLATE_200),
        ("BOX",           (0, 0), (-1, -1), 1, SLATE_200),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 16))

    if ticket.assigned_value is not None:
        value_clp = f"${int(ticket.assigned_value):,}".replace(",", ".")
        billed_str = "SÍ — Facturado" if ticket.is_billed else "PENDIENTE de facturación"
        billed_color = EMERALD if ticket.is_billed else AMBER

        billing_data = [[
            Paragraph("VALOR DEL SERVICIO", label_style),
            Paragraph("ESTADO FACTURACIÓN", label_style),
        ], [
            Paragraph(f"<b><font color='#059669' size=14>{value_clp} CLP</font></b>",
                      ParagraphStyle("val", parent=styles["Normal"], fontSize=14,
                                     fontName="Helvetica-Bold", textColor=EMERALD)),
            badge_para(billed_str, billed_color),
        ]]
        billing_table = Table(billing_data, colWidths=[page_w*0.55, page_w*0.45])
        billing_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), EMERALD_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("LINEBELOW",     (0, 0), (-1, 0), 0.5, colors.HexColor("#6EE7B7")),
            ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#6EE7B7")),
        ]))
        story.append(billing_table)
        story.append(Spacer(1, 16))

    story.append(Paragraph("DESCRIPCIÓN", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SLATE_200, spaceAfter=8))
    desc_text = ticket.description.replace("\n", "<br/>")
    story.append(Paragraph(desc_text, desc_style))
    story.append(Spacer(1, 12))

    public_comments = list(ticket.comments.filter(is_internal=False).order_by("created_at"))
    if public_comments:
        story.append(Paragraph("CONVERSACIÓN", section_style))
        story.append(HRFlowable(width="100%", thickness=1, color=SLATE_200, spaceAfter=8))
        for comment in public_comments:
            role = "Equipo de Soporte" if comment.is_staff else comment.author_name
            date_str = comment.created_at.strftime("%d/%m/%Y %H:%M")
            bg = INDIGO_LIGHT if comment.is_staff else SLATE_50
            border = INDIGO if comment.is_staff else SLATE_200
            comment_data = [[
                Paragraph(f"<b>{role}</b>", comment_author),
                Paragraph(date_str, ParagraphStyle("dt", parent=styles["Normal"],
                          fontSize=8, textColor=SLATE_500, alignment=TA_RIGHT)),
            ], [
                Paragraph(comment.message.replace("\n", "<br/>"), comment_text),
                Paragraph("", comment_text),
            ]]
            ct = Table(comment_data, colWidths=[page_w*0.7, page_w*0.3])
            ct.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), bg),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("SPAN",          (0, 1), (1, 1)),
                ("BOX",           (0, 0), (-1, -1), 1, border),
                ("LINEBELOW",     (0, 0), (-1, 0), 0.5, border),
            ]))
            story.append(KeepTogether(ct))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SLATE_200, spaceAfter=6))
    story.append(Paragraph(
        f"<font color='#94A3B8'>Generado por SoporteApp · Ticket {ticket.token} · {ticket.company.name}</font>",
        ParagraphStyle("footer", parent=styles["Normal"],
                       fontSize=8, textColor=SLATE_500, alignment=TA_CENTER)
    ))

    doc.build(story)
    buf.seek(0)
    return buf


def generate_ticket_image(ticket):
    W, H = 800, 560
    SCALE = 2  
    w, h = W * SCALE, H * SCALE

    img = Image.new("RGB", (w, h), "#FFFFFF")
    d   = ImageDraw.Draw(img)

    def px(n):  return int(n * SCALE)
    def hex2rgb(hx):
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

    def rect(x, y, x2, y2, fill, radius=0):
        if radius:
            d.rounded_rectangle([px(x), px(y), px(x2), px(y2)],
                                 radius=px(radius), fill=hex2rgb(fill))
        else:
            d.rectangle([px(x), px(y), px(x2), px(y2)], fill=hex2rgb(fill))

    def rect_outline(x, y, x2, y2, fill, outline, radius=0):
        if radius:
            d.rounded_rectangle([px(x), px(y), px(x2), px(y2)],
                                 radius=px(radius), fill=hex2rgb(fill),
                                 outline=hex2rgb(outline), width=px(1))
        else:
            d.rectangle([px(x), px(y), px(x2), px(y2)],
                        fill=hex2rgb(fill), outline=hex2rgb(outline), width=px(1))

    def text(x, y, txt, size, color, bold=False):
        from PIL import ImageFont
        try:
            font_name = "arialbd.ttf" if bold else "arial.ttf"
            font = ImageFont.truetype(font_name, px(size))
        except Exception:
            font = ImageFont.load_default(size=px(size))
        d.text((px(x), px(y)), txt, fill=hex2rgb(color), font=font)

    def badge(x, y, txt, bg, w_badge=130, h_badge=22):
        rect(x, y, x + w_badge, y + h_badge, bg, radius=5)
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arialbd.ttf", px(9))
        except Exception:
            font = ImageFont.load_default(size=px(9))
        bbox = d.textbbox((0, 0), txt, font=font)
        tw = bbox[2] - bbox[0]
        tx = x + (w_badge - tw) / 2
        ty = y + (h_badge - px(9)) / 2 - 1
        d.text((px(tx), px(ty)), txt, fill=(255, 255, 255), font=font)

    rect(0, 0, W, 52, "#4F46E5")
    text(24, 16, "TICKET DE SOPORTE", 10, "#FFFFFF", bold=True)
    comp = ticket.company.name[:40]
    text(W - len(comp) * 7 - 24, 17, comp, 10, "#C7D2FE")

    text(24, 66, f"#{ticket.token}", 20, "#4F46E5", bold=True)
    subj = (ticket.subject[:65] + "…") if len(ticket.subject) > 65 else ticket.subject
    text(24, 96, subj, 11, "#334155")

    rect(24, 118, W - 24, 119, "#E2E8F0")

    cols = [
        ("EMPRESA",     ticket.company.name[:28]),
        ("SOLICITANTE", ticket.requester_name[:28]),
        ("EMAIL",       (ticket.requester_email[:30] + "…") if len(ticket.requester_email) > 30 else ticket.requester_email),
    ]
    for i, (lbl, val) in enumerate(cols):
        x = 24 + i * 254
        text(x, 128, lbl, 8, "#94A3B8", bold=True)
        text(x, 142, val, 10, "#0F172A", bold=True)

    cat_label = CATEGORY_LABELS.get(ticket.category, ticket.category)
    cat_hex   = {"software": "#6366F1", "hardware": "#D97706", "email": "#059669"}.get(ticket.category, "#6B7280")
    stat_name = ticket.status.name if ticket.status else "Sin estado"
    stat_hex  = ticket.status.color if ticket.status else "#6B7280"
    prio_name = ticket.priority.name if ticket.priority else "Sin prioridad"
    prio_hex  = ticket.priority.color if ticket.priority else "#6B7280"

    badge(24,  170, cat_label, cat_hex)
    badge(168, 170, stat_name, stat_hex)
    badge(312, 170, prio_name, prio_hex)

    rect(24, 202, W - 24, 203, "#E2E8F0")

    y_cur = 212
    if ticket.assigned_value is not None:
        value_str  = f"${int(ticket.assigned_value):,} CLP".replace(",", ".")
        billed_str = "Facturado" if ticket.is_billed else "Pendiente"
        bill_hex   = "#059669" if ticket.is_billed else "#D97706"
        rect_outline(24, y_cur, W - 24, y_cur + 58, "#ECFDF5", "#6EE7B7", radius=8)
        text(36, y_cur + 8,  "VALOR DEL SERVICIO", 8, "#059669", bold=True)
        text(36, y_cur + 22, value_str, 16, "#059669", bold=True)
        badge(W - 168, y_cur + 18, billed_str, bill_hex, w_badge=130)
        y_cur += 70

    created_str = ticket.created_at.strftime("%d/%m/%Y  %H:%M")
    closed_str  = ticket.closed_at.strftime("%d/%m/%Y  %H:%M") if ticket.closed_at else "—"
    text(24,  y_cur,      "CREADO",  8,  "#94A3B8", bold=True)
    text(24,  y_cur + 14, created_str, 10, "#334155")
    text(220, y_cur,      "CERRADO", 8,  "#94A3B8", bold=True)
    text(220, y_cur + 14, closed_str, 10, "#334155")
    y_cur += 42

    rect_outline(24, y_cur, W - 24, y_cur + 70, "#F8FAFC", "#E2E8F0", radius=6)
    text(36, y_cur + 8, "DESCRIPCION", 8, "#94A3B8", bold=True)
    desc = ticket.description.replace("\n", " ")
    lines = [desc[i:i+90] for i in range(0, min(len(desc), 180), 90)]
    for li, line in enumerate(lines[:2]):
        text(36, y_cur + 22 + li * 17, line, 9, "#475569")
    y_cur += 82

    rect(0, H - 34, W, H, "#F1F5F9")
    footer = f"SoporteApp  ·  Ticket {ticket.token}  ·  {ticket.company.name}"
    text(W // 2 - len(footer) * 3, H - 22, footer, 8, "#94A3B8")

    img = img.resize((W, H), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf