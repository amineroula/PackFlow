from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .model import PackagingGuide


FORMATIVE = {
    "dark_blue": colors.HexColor("#09314A"),
    "olive": colors.HexColor("#727562"),
    "black": colors.HexColor("#000000"),
    "white": colors.HexColor("#FFFFFF"),
    "red": colors.HexColor("#F9423A"),
    "taupe": colors.HexColor("#E3E4E0"),
    "blue": colors.HexColor("#4C78FF"),
    "yellow": colors.HexColor("#FFBC03"),
    "mint": colors.HexColor("#70DAB4"),
}


def _safe_image(path: str, width: float, height: float):
    if not path or not Path(path).exists():
        placeholder = Table([["IMAGE"]], colWidths=[width], rowHeights=[height])
        placeholder.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), FORMATIVE["taupe"]),
            ("TEXTCOLOR", (0, 0), (-1, -1), FORMATIVE["olive"]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C7C9C4")),
        ]))
        return placeholder
    img = Image(path)
    img._restrictSize(width, height)
    return img


def export_packaging_guide(guide: PackagingGuide, output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )

    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=21, leading=24, textColor=FORMATIVE["dark_blue"])
    eyebrow = ParagraphStyle("eyebrow", fontName="Courier-Bold", fontSize=8, leading=10, textColor=FORMATIVE["olive"])
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14, textColor=FORMATIVE["black"])
    step_title = ParagraphStyle("step_title", fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=FORMATIVE["dark_blue"])

    story = [
        Paragraph("PACKAGING GUIDE", eyebrow),
        Paragraph(f"{guide.part_number or 'PART NUMBER'} — {guide.part_name or 'PART NAME'}", title),
        Spacer(1, 0.18 * inch),
    ]

    info = Table([
        [_safe_image(guide.part_image_path, 3.55 * inch, 2.15 * inch),
         Table([
             [Paragraph("BOX", eyebrow), Paragraph(guide.box_dimensions or "—", body)],
             [Paragraph("QUANTITY", eyebrow), Paragraph(str(guide.quantity or "—"), body)],
             [Paragraph("ARRANGEMENT", eyebrow), Paragraph("2 rows × 14" if guide.quantity == 28 else "—", body)],
         ], colWidths=[1.05 * inch, 1.55 * inch])]
    ], colWidths=[3.75 * inch, 2.65 * inch])
    info.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [info, Spacer(1, 0.22 * inch)]

    story += [
        Paragraph("PACKING REFERENCE", eyebrow),
        Spacer(1, 0.06 * inch),
        _safe_image(guide.packing_image_path, 6.4 * inch, 3.3 * inch),
        Spacer(1, 0.22 * inch),
        Paragraph("Place the parts in the box exactly as shown in the reference image.", body),
    ]

    story.append(Spacer(1, 0.45 * inch))

    cards = []
    for index, step in enumerate(guide.steps, start=1):
        number = Table([[str(index)]], colWidths=[0.36 * inch], rowHeights=[0.36 * inch])
        number.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), FORMATIVE["blue"]),
            ("TEXTCOLOR", (0, 0), (-1, -1), FORMATIVE["white"]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, -1), "Courier-Bold"),
        ]))
        content = Table([
            [number, Paragraph(step.title, step_title)],
            ["", Paragraph(step.instruction, body)],
            ["", _safe_image(step.image_path, 2.55 * inch, 1.55 * inch)],
        ], colWidths=[0.48 * inch, 2.65 * inch])
        content.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        card = Table([[content]], colWidths=[3.15 * inch])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C9D8E3")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        cards.append(card)

    while len(cards) < 4:
        cards.append("")

    steps_table = Table([[cards[0], cards[1]], [cards[2], cards[3]]], colWidths=[3.2 * inch, 3.2 * inch], hAlign="CENTER")
    steps_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story += [Paragraph("PACKING STEPS", eyebrow), Spacer(1, 0.08 * inch), steps_table]
    doc.build(story)
