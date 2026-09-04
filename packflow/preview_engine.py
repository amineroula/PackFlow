from __future__ import annotations

from html import escape
from pathlib import Path

from .model import PackagingGuide


BRAND = {
    "dark_blue": "#09314A",
    "olive": "#727562",
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#F9423A",
    "taupe": "#E3E4E0",
    "blue": "#4C78FF",
    "yellow": "#FFBC03",
    "mint": "#70DAB4",
}


def _image_html(path: str, label: str, height: int) -> str:
    if path and Path(path).exists():
        uri = Path(path).resolve().as_uri()
        return (
            f'<div class="image-frame" style="height:{height}px">'
            f'<img src="{uri}" alt="{escape(label)}" />'
            "</div>"
        )
    return (
        f'<div class="image-frame placeholder" style="height:{height}px">'
        f'{escape(label.upper())}'
        "</div>"
    )


def render_packaging_preview(guide: PackagingGuide) -> str:
    step_cards = []
    for index, step in enumerate(guide.steps, start=1):
        step_cards.append(
            f"""
            <div class="step-card">
                <div class="step-head">
                    <span class="step-number">{index}</span>
                    <div>
                        <div class="step-title">{escape(step.title or f'Step {index}')}</div>
                        <div class="step-copy">{escape(step.instruction)}</div>
                    </div>
                </div>
                {_image_html(step.image_path, f'Step {index} image', 150)}
            </div>
            """
        )

    while len(step_cards) < 4:
        step_cards.append('<div class="step-card"></div>')

    return f"""
    <html>
    <head>
    <style>
        body {{ margin:0; padding:24px; background:#D9DCDA; color:{BRAND['black']}; font-family:Arial, sans-serif; }}
        .page {{ width:720px; min-height:930px; margin:0 auto 28px auto; padding:40px 44px; box-sizing:border-box; background:white; border:1px solid #CDD1CF; }}
        .brand-row {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:26px; }}
        .brand {{ color:{BRAND['dark_blue']}; font-size:22px; font-weight:700; letter-spacing:-0.4px; }}
        .eyebrow {{ color:{BRAND['olive']}; font-family:monospace; font-size:11px; font-weight:700; letter-spacing:1.2px; }}
        h1 {{ color:{BRAND['dark_blue']}; font-size:29px; line-height:1.08; margin:6px 0 24px 0; font-weight:700; }}
        .hero {{ display:grid; grid-template-columns:1.45fr 1fr; gap:22px; align-items:start; }}
        .info {{ background:{BRAND['taupe']}; padding:18px; }}
        .label {{ color:{BRAND['olive']}; font-family:monospace; font-size:10px; font-weight:700; letter-spacing:0.8px; margin-top:10px; }}
        .value {{ color:{BRAND['dark_blue']}; font-size:17px; font-weight:700; margin-top:3px; }}
        .section-label {{ color:{BRAND['olive']}; font-family:monospace; font-size:11px; font-weight:700; letter-spacing:1px; margin:28px 0 8px 0; }}
        .image-frame {{ background:#F2F3F0; border:1px solid #D3D7D3; display:flex; align-items:center; justify-content:center; overflow:hidden; box-sizing:border-box; }}
        .image-frame img {{ max-width:100%; max-height:100%; object-fit:contain; }}
        .placeholder {{ color:{BRAND['olive']}; font-family:monospace; font-size:12px; letter-spacing:1px; }}
        .reference-copy {{ font-size:13px; line-height:1.4; color:#343A3D; margin-top:10px; }}
        .steps-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
        .step-card {{ border:1px solid #CBD9E2; padding:16px; min-height:340px; box-sizing:border-box; }}
        .step-head {{ display:flex; gap:12px; align-items:flex-start; min-height:74px; }}
        .step-number {{ display:inline-flex; width:30px; height:30px; border-radius:15px; align-items:center; justify-content:center; background:{BRAND['blue']}; color:white; font-family:monospace; font-weight:700; font-size:15px; flex:none; }}
        .step-title {{ color:{BRAND['dark_blue']}; font-size:16px; font-weight:700; line-height:1.2; }}
        .step-copy {{ color:#42484A; font-size:12px; line-height:1.35; margin-top:5px; }}
        .footer {{ margin-top:28px; padding-top:10px; border-top:1px solid #D7DAD7; color:{BRAND['olive']}; font-family:monospace; font-size:9px; display:flex; justify-content:space-between; }}
    </style>
    </head>
    <body>
        <div class="page">
            <div class="brand-row"><div class="brand">Formative 3D</div><div class="eyebrow">PACKAGING GUIDE</div></div>
            <h1>{escape(guide.part_number or 'PART NUMBER')} — {escape(guide.part_name or 'PART NAME')}</h1>
            <div class="hero">
                {_image_html(guide.part_image_path, 'Part image', 245)}
                <div class="info">
                    <div class="label">BOX</div><div class="value">{escape(guide.box_dimensions or '—')}</div>
                    <div class="label">QUANTITY</div><div class="value">{guide.quantity or '—'}</div>
                    <div class="label">ARRANGEMENT</div><div class="value">{escape(guide.arrangement_text)}</div>
                </div>
            </div>
            <div class="section-label">PACKING REFERENCE</div>
            {_image_html(guide.packing_image_path, 'Packing reference', 390)}
            <div class="reference-copy">Place the parts in the box exactly as shown in the reference image.</div>
            <div class="footer"><span>PACKFLOW / PACKAGING GUIDE 01</span><span>PAGE 1 / 2</span></div>
        </div>
        <div class="page">
            <div class="brand-row"><div class="brand">Formative 3D</div><div class="eyebrow">PACKING STEPS</div></div>
            <h1>{escape(guide.part_number or 'PART NUMBER')} — Packing Instructions</h1>
            <div class="steps-grid">{''.join(step_cards[:4])}</div>
            <div class="footer"><span>PACKFLOW / PACKAGING GUIDE 01</span><span>PAGE 2 / 2</span></div>
        </div>
    </body>
    </html>
    """
