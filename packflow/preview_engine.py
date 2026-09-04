from __future__ import annotations
from html import escape
from pathlib import Path
from .brand import BRAND, logo_path
from .model import PackagingGuide

def _uri(path): return Path(path).resolve().as_uri()
def _img(path,label,height):
    if path and Path(path).exists(): return f'<div class="image-frame" style="height:{height}px"><img src="{_uri(path)}"></div>'
    return f'<div class="image-frame placeholder" style="height:{height}px">{escape(label.upper())}</div>'
def _logo():
    p=logo_path(); return f'<img class="logo" src="{_uri(p)}">' if p.exists() else '<b>Formative 3D</b>'

def render_packaging_preview(g: PackagingGuide)->str:
    cards=[]
    for i,s in enumerate(g.steps,1):
        cards.append(f'<div class="step-card"><div class="head"><span class="num">{i}</span><div><div class="st">{escape(s.title)}</div><div class="sc">{escape(s.instruction)}</div></div></div>{_img(s.image_path,f"Step {i}",210)}</div>')
    step_pages=[]
    for start in range(0,max(1,len(cards)),4):
        step_pages.append(f'<div class="page"><div class="top"><div><div class="eyebrow">PACKAGING / STEPS</div><h1>Packing Instructions</h1><p>Follow the steps in order. Use the images as the primary guide.</p><div class="rule"></div></div>{_logo()}</div><div class="shell"><div class="grid">{"".join(cards[start:start+4])}</div></div><div class="footer">FORMATIVE 3D / PACKAGING GUIDE / PAGE {2+start//4}<span></span></div></div>')
    return f'''<html><head><style>
body{{margin:0;padding:24px;background:#cfd2cf;font-family:Arial;color:#000}}.page{{width:760px;min-height:980px;margin:0 auto 28px;padding:46px 50px 30px;box-sizing:border-box;background:{BRAND['taupe']}}}.top{{display:flex;justify-content:space-between;align-items:flex-start}}.logo{{width:190px;max-height:62px;object-fit:contain}}.eyebrow{{color:{BRAND['red']};font:700 10px monospace;letter-spacing:.5px;margin-bottom:18px}}h1{{font-size:31px;margin:5px 0 3px}}p{{color:{BRAND['olive']};font-size:13px;margin:0}}.partno{{font-size:34px;font-weight:800}}.doc{{font-size:26px}}.pname{{color:{BRAND['olive']};font:12px monospace;margin-top:8px}}.rule{{width:90px;height:5px;background:{BRAND['red']};border-radius:3px;margin-top:12px}}.hero{{display:grid;grid-template-columns:1.08fr .92fr;gap:20px;margin-top:22px}}.card,.shell{{background:white;border-radius:18px;padding:18px;box-sizing:border-box}}.info{{padding:27px}}.redlabel{{color:{BRAND['red']};font:700 10px monospace;margin-bottom:20px}}.label{{color:{BRAND['olive']};font-size:11px;margin-top:13px}}.value{{font-size:24px;font-weight:800;margin-top:3px}}.small{{font-size:15px}}.refh{{color:{BRAND['red']};font:700 10px monospace;margin:28px 0 10px}}.image-frame{{background:#f7f7f5;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:10px}}.image-frame img{{width:100%;height:100%;object-fit:contain}}.placeholder{{border:1px dashed #c7cac4;color:{BRAND['olive']};font:11px monospace}}.refcopy{{font-size:13px;margin-top:16px}}.shell{{margin-top:34px;min-height:690px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}.step-card{{border:1px solid #9ec4d8;border-radius:9px;padding:10px;min-height:320px}}.head{{display:flex;gap:10px;min-height:82px}}.num{{width:48px;height:48px;border-radius:50%;background:{BRAND['blue']};color:white;display:flex;align-items:center;justify-content:center;font-size:29px;font-weight:800;flex:none}}.st{{color:{BRAND['dark_blue']};font-size:17px;font-weight:800}}.sc{{font-size:11px;margin-top:4px}}.footer{{margin-top:25px;text-align:right;color:{BRAND['olive']};font:8px monospace}}.footer span{{display:inline-block;width:7px;height:7px;background:{BRAND['red']};margin-left:10px}}
</style></head><body>
<div class="page"><div class="top"><div><div class="eyebrow">PACKAGING / WORK INSTRUCTION</div><div class="partno">{escape(g.part_number or 'PART NUMBER')}</div><div class="doc">Packaging Guide</div><div class="pname">{escape(g.part_name or 'PART NAME')}</div><div class="rule"></div></div>{_logo()}</div><div class="hero"><div class="card">{_img(g.part_image_path,'Part',225)}</div><div class="card info"><div class="redlabel">PACKING INFORMATION</div><div class="label">Box size</div><div class="value">{escape(g.box_dimensions)}</div><div class="label">Quantity per box</div><div class="value">{g.quantity or '-'}</div><div class="label">Arrangement</div><div class="value small">{escape(g.arrangement_text)}</div></div></div><div class="refh">CORRECT PACKING ARRANGEMENT</div><div class="card">{_img(g.packing_image_path,'Packing reference',315)}</div><div class="refcopy">{escape(g.reference_instruction)}</div><div class="footer">FORMATIVE 3D / PACKAGING GUIDE / PAGE 1<span></span></div></div>{''.join(step_pages)}</body></html>'''
