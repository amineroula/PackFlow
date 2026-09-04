from __future__ import annotations

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .brand import BRAND, logo_path
from .model import PackagingGuide, PackagingStep

PAGE_W, PAGE_H = letter
M = 38
TAUPE = colors.HexColor(BRAND["taupe"])
RED = colors.HexColor(BRAND["red"])
DARK_BLUE = colors.HexColor(BRAND["dark_blue"])
OLIVE = colors.HexColor(BRAND["olive"])
ACCENT_BLUE = colors.HexColor(BRAND["blue"])
WHITE = colors.white
BLACK = colors.black


def _image_size(path: str):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def _draw_fitted_image(c, path, x, y, w, h, pad=0):
    if not path or not Path(path).exists():
        c.setStrokeColor(colors.HexColor("#C7CAC4")); c.setDash(4,3)
        c.roundRect(x+pad,y+pad,w-2*pad,h-2*pad,8,fill=0,stroke=1); c.setDash()
        c.setFillColor(OLIVE); c.setFont("Courier-Bold",9); c.drawCentredString(x+w/2,y+h/2,"IMAGE"); return
    try:
        img=ImageReader(path); iw,ih=_image_size(path) or (w,h)
        scale=min((w-2*pad)/iw,(h-2*pad)/ih); dw,dh=iw*scale,ih*scale
        c.drawImage(img,x+(w-dw)/2,y+(h-dh)/2,dw,dh,preserveAspectRatio=True,mask="auto")
    except Exception:
        c.setFillColor(OLIVE); c.setFont("Helvetica",8); c.drawCentredString(x+w/2,y+h/2,"IMAGE COULD NOT BE LOADED")


def _draw_logo(c,x,y,w=170,h=45):
    p=logo_path()
    if p.exists(): _draw_fitted_image(c,str(p),x,y,w,h)
    else:
        c.setFillColor(BLACK); c.setFont("Helvetica-Bold",20); c.drawRightString(x+w,y+h/2,"Formative 3D")


def _draw_footer(c,page_no):
    c.setFillColor(OLIVE); c.setFont("Courier",6.7)
    c.drawRightString(PAGE_W-M-38,22,f"FORMATIVE 3D   /   PACKAGING GUIDE   /   PAGE {page_no}")
    c.setFillColor(RED); c.rect(PAGE_W-M-5,19,6,6,fill=1,stroke=0)


def _wrap(c,text,x,y,max_width,font,size,leading,max_lines=3):
    words=text.split(); lines=[]; current=""
    for word in words:
        test=(current+" "+word).strip()
        if c.stringWidth(test,font,size)<=max_width: current=test
        else:
            if current: lines.append(current)
            current=word
    if current: lines.append(current)
    c.setFont(font,size)
    for line in lines[:max_lines]: c.drawString(x,y,line); y-=leading
    return y


def _page_one(c,g):
    c.setFillColor(TAUPE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    c.setFillColor(RED); c.setFont("Courier-Bold",7.2); c.drawString(M,PAGE_H-50,"PACKAGING / WORK INSTRUCTION")
    _draw_logo(c,PAGE_W-M-170,PAGE_H-76,170,48)
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",25); c.drawString(M,PAGE_H-94,g.part_number or "PART NUMBER")
    c.setFont("Helvetica",19); c.drawString(M,PAGE_H-119,"Packaging Guide")
    c.setFillColor(OLIVE); c.setFont("Courier",8); c.drawString(M,PAGE_H-138,g.part_name or "PART NAME")
    c.setFillColor(RED); c.roundRect(M,PAGE_H-155,72,4,2,fill=1,stroke=0)

    card_y=PAGE_H-395; left_x,left_w=M,275; gap=18; right_x=left_x+left_w+gap; right_w=PAGE_W-M-right_x; card_h=220
    c.setFillColor(WHITE); c.roundRect(left_x,card_y,left_w,card_h,14,fill=1,stroke=0)
    _draw_fitted_image(c,g.part_image_path,left_x+14,card_y+20,left_w-28,card_h-32,2)
    c.setFillColor(DARK_BLUE); c.setFont("Courier-Bold",6.8); c.drawString(left_x+14,card_y+8,"PART")

    c.setFillColor(WHITE); c.roundRect(right_x,card_y,right_w,card_h,14,fill=1,stroke=0); tx=right_x+22
    c.setFillColor(RED); c.setFont("Courier-Bold",7); c.drawString(tx,card_y+card_h-31,"PACKING INFORMATION")
    c.setFillColor(OLIVE); c.setFont("Helvetica",7.5); c.drawString(tx,card_y+card_h-67,"Box size")
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",18); c.drawString(tx,card_y+card_h-91,g.box_dimensions)
    c.setFillColor(OLIVE); c.setFont("Helvetica",7.5); c.drawString(tx,card_y+card_h-127,"Quantity per box")
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",23); c.drawString(tx,card_y+card_h-154,str(g.quantity or "-"))
    c.setFillColor(OLIVE); c.setFont("Helvetica",7.5); c.drawString(tx,card_y+31,"Arrangement")
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",10); c.drawString(tx,card_y+14,g.arrangement_text)

    ref_head=card_y-34; c.setFillColor(RED); c.setFont("Courier-Bold",7); c.drawString(M,ref_head,"CORRECT PACKING ARRANGEMENT")
    ref_y=112; ref_h=ref_head-ref_y-13
    c.setFillColor(WHITE); c.roundRect(M,ref_y,PAGE_W-2*M,ref_h,14,fill=1,stroke=0)
    _draw_fitted_image(c,g.packing_image_path,M+16,ref_y+16,PAGE_W-2*M-32,ref_h-32,2)
    c.setFillColor(BLACK); _wrap(c,g.reference_instruction,M,83,PAGE_W-2*M,"Helvetica",8.5,11,2)
    _draw_footer(c,1); c.showPage()


def _step_card(c,s,index,x,y,w,h):
    c.setFillColor(WHITE); c.setStrokeColor(colors.HexColor("#9EC4D8")); c.setLineWidth(1); c.roundRect(x,y,w,h,7,fill=1,stroke=1)
    cx,cy,r=x+34,y+h-34,23; c.setFillColor(ACCENT_BLUE); c.circle(cx,cy,r,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",24); c.drawCentredString(cx,cy-8,str(index))
    tx=x+70; c.setFillColor(DARK_BLUE); _wrap(c,s.title or f"Step {index}",tx,y+h-30,w-82,"Helvetica-Bold",11.8,13,2)
    c.setFillColor(colors.HexColor("#303638")); _wrap(c,s.instruction,tx,y+h-58,w-82,"Helvetica",7.7,9.3,3)
    _draw_fitted_image(c,s.image_path,x+8,y+8,w-16,h-102,1)


def _steps_page(c,g,steps,start_index,page_no):
    c.setFillColor(TAUPE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    c.setFillColor(RED); c.setFont("Courier-Bold",7.2); c.drawString(M,PAGE_H-50,"PACKAGING / STEPS")
    _draw_logo(c,PAGE_W-M-170,PAGE_H-76,170,48)
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",24); c.drawString(M,PAGE_H-98,"Packing Instructions")
    c.setFillColor(OLIVE); c.setFont("Helvetica",8.5); c.drawString(M,PAGE_H-118,"Follow the steps in order. Use the images as the primary guide.")
    c.setFillColor(RED); c.roundRect(M,PAGE_H-137,72,4,2,fill=1,stroke=0)
    sx,sy=M-12,92; sw,sh=PAGE_W-2*(M-12),PAGE_H-255
    c.setFillColor(WHITE); c.roundRect(sx,sy,sw,sh,14,fill=1,stroke=0)
    pad=14; gap=5; cw=(sw-2*pad-gap)/2; ch=(sh-2*pad-gap)/2
    pos=[(sx+pad,sy+pad+ch+gap),(sx+pad+cw+gap,sy+pad+ch+gap),(sx+pad,sy+pad),(sx+pad+cw+gap,sy+pad)]
    for offset,s in enumerate(steps): _step_card(c,s,start_index+offset,*pos[offset],cw,ch)
    _draw_footer(c,page_no); c.showPage()


def export_packaging_guide(g: PackagingGuide, output_path: str)->None:
    c=canvas.Canvas(output_path,pagesize=letter); c.setTitle(f"{g.part_number or 'Part'} Packaging Guide"); c.setAuthor("Formative 3D / PackFlow")
    _page_one(c,g); steps=g.steps or [PackagingStep()]
    for i in range(0,len(steps),4): _steps_page(c,g,steps[i:i+4],i+1,2+i//4)
    c.save()
