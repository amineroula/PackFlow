from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea,
    QSpinBox, QSplitter, QTextBrowser, QVBoxLayout, QWidget,
)

from packflow.brand import APP_BG, BRAND, BRAND_RULES_SUMMARY
from packflow.model import PackagingGuide, PackagingStep, default_guide
from packflow.pdf_engine import export_packaging_guide
from packflow.preview_engine import render_packaging_preview

IMAGE_FILTER = "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff)"


class ImagePicker(QFrame):
    def __init__(self, label: str, changed_callback):
        super().__init__(); self.label=label; self.path=""; self.changed_callback=changed_callback
        self.setAcceptDrops(True); self.setObjectName("imagePicker")
        layout=QVBoxLayout(self); layout.setContentsMargins(10,10,10,10); layout.setSpacing(7)
        controls=QHBoxLayout(); self.button=QPushButton(f"Choose {label}..."); self.button.setObjectName("primarySmall")
        self.remove_button=QPushButton("Remove"); self.remove_button.setObjectName("secondaryButton")
        controls.addWidget(self.button,1); controls.addWidget(self.remove_button); layout.addLayout(controls)
        self.preview=QLabel("Drop an image here\nor click Choose Image"); self.preview.setAlignment(Qt.AlignCenter); self.preview.setMinimumHeight(120); self.preview.setObjectName("imagePreview"); self.preview.setWordWrap(True); layout.addWidget(self.preview)
        self.path_label=QLabel(""); self.path_label.setObjectName("pathLabel"); layout.addWidget(self.path_label)
        self.button.clicked.connect(self.choose); self.remove_button.clicked.connect(self.clear)

    def choose(self):
        start=str(Path(self.path).parent) if self.path and Path(self.path).exists() else str(Path.home())
        path,_=QFileDialog.getOpenFileName(self,f"Choose {self.label}",start,IMAGE_FILTER)
        if path: self.load_image(path)

    def load_image(self,path:str):
        reader=QImageReader(path); reader.setAutoTransform(True); image=reader.read()
        if image.isNull():
            QMessageBox.warning(self,"Image could not be opened",f"PackFlow could not read this image:\n{path}\n\n{reader.errorString()}"); return
        self.path=path; pix=QPixmap.fromImage(image); self.preview.setPixmap(pix.scaled(320,170,Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.preview.setToolTip(path); self.path_label.setText(Path(path).name); self.changed_callback()

    def set_path(self,path:str):
        self.path=""
        if path and Path(path).exists():
            reader=QImageReader(path); reader.setAutoTransform(True); image=reader.read()
            if not image.isNull():
                self.path=path; pix=QPixmap.fromImage(image); self.preview.setPixmap(pix.scaled(320,170,Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.preview.setToolTip(path); self.path_label.setText(Path(path).name); return
        self.preview.setPixmap(QPixmap()); self.preview.setText("Drop an image here\nor click Choose Image"); self.preview.setToolTip(""); self.path_label.setText("")

    def clear(self): self.set_path(""); self.changed_callback()
    def dragEnterEvent(self,event):
        urls=event.mimeData().urls()
        if urls and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).suffix.lower() in {".png",".jpg",".jpeg",".webp",".bmp",".tif",".tiff"}: event.acceptProposedAction()
        else: event.ignore()
    def dropEvent(self,event):
        urls=event.mimeData().urls()
        if urls: self.load_image(urls[0].toLocalFile()); event.acceptProposedAction()


class StepEditor(QFrame):
    def __init__(self,index,step,change_callback,delete_callback):
        super().__init__(); self.index=index; self.delete_callback=delete_callback; self.setObjectName("stepEditorCard")
        outer=QVBoxLayout(self); outer.setContentsMargins(12,12,12,12); outer.setSpacing(8)
        head=QHBoxLayout(); self.heading=QLabel(f"Step {index}"); self.heading.setObjectName("stepHeading")
        delete=QPushButton("Delete Step"); delete.setObjectName("dangerButton"); delete.clicked.connect(lambda:self.delete_callback(self)); head.addWidget(self.heading); head.addStretch(); head.addWidget(delete); outer.addLayout(head)
        form=QFormLayout(); self.title_edit=QLineEdit(step.title); self.instruction_edit=QLineEdit(step.instruction); self.title_edit.textChanged.connect(change_callback); self.instruction_edit.textChanged.connect(change_callback); form.addRow("Title",self.title_edit); form.addRow("Instruction",self.instruction_edit); outer.addLayout(form)
        self.image=ImagePicker(f"step {index} image",change_callback); self.image.set_path(step.image_path); outer.addWidget(self.image)
    def to_step(self): return PackagingStep(self.title_edit.text().strip(),self.instruction_edit.text().strip(),self.image.path)


class BrandRulesDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Formative 3D Brand Rules"); self.resize(720,650)
        layout=QVBoxLayout(self); title=QLabel("Formative 3D Brand Rules"); title.setObjectName("dialogTitle"); layout.addWidget(title)
        note=QLabel("These rules are locked into PackFlow's Formative 3D templates."); note.setObjectName("muted"); layout.addWidget(note)
        text=QTextBrowser(); text.setPlainText(BRAND_RULES_SUMMARY); layout.addWidget(text,1); close=QPushButton("Close"); close.clicked.connect(self.accept); layout.addWidget(close,alignment=Qt.AlignRight)


class PackFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("PackFlow - Production Document Builder"); self.resize(1600,980)
        self.guide=default_guide(); self.current_project_path=None; self.step_editors=[]; self.build_ui(); self.apply_style(); self.load_guide_into_ui(self.guide); self.statusBar().showMessage("Ready")

    def section_label(self,text): label=QLabel(text); label.setObjectName("sectionLabel"); return label

    def build_ui(self):
        root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root); outer.setContentsMargins(16,14,16,16)
        toolbar=QHBoxLayout(); tg=QVBoxLayout(); title=QLabel("PackFlow"); title.setObjectName("appTitle"); sub=QLabel("Production Document Builder"); sub.setObjectName("appSubtitle"); tg.addWidget(title); tg.addWidget(sub); toolbar.addLayout(tg); toolbar.addStretch()
        for text,slot,obj in [("Brand Rules",self.show_brand_rules,"secondaryButton"),("New",self.new_project,"secondaryButton"),("Open",self.open_project,"secondaryButton"),("Save",self.save_project,"secondaryButton"),("Export PDF",self.export_pdf,"primaryButton")]:
            b=QPushButton(text); b.setObjectName(obj); b.clicked.connect(slot); toolbar.addWidget(b)
        outer.addLayout(toolbar)
        splitter=QSplitter(); splitter.setChildrenCollapsible(False); outer.addWidget(splitter,1)
        fc=QWidget(); self.form_layout=QVBoxLayout(fc); self.form_layout.setContentsMargins(4,4,10,4); self.form_layout.setSpacing(9)
        locked=QLabel("BRAND: FORMATIVE 3D  /  TEMPLATE: PACKAGING GUIDE 01  /  LOCKED"); locked.setObjectName("brandLocked"); self.form_layout.addWidget(locked)
        self.form_layout.addWidget(self.section_label("DOCUMENT INFORMATION")); form=QFormLayout(); form.setVerticalSpacing(10)
        self.part_number=QLineEdit(); self.part_name=QLineEdit(); self.box_length=QLineEdit(); self.box_width=QLineEdit(); self.box_height=QLineEdit(); self.quantity=QSpinBox(); self.quantity.setRange(0,100000); self.arrangement_rows=QSpinBox(); self.arrangement_rows.setRange(0,1000); self.parts_per_row=QSpinBox(); self.parts_per_row.setRange(0,100000); self.reference_instruction=QLineEdit()
        self.part_number.setPlaceholderText("300026-01"); self.part_name.setPlaceholderText("TOP CONNECT A"); self.box_length.setPlaceholderText("18"); self.box_width.setPlaceholderText("12"); self.box_height.setPlaceholderText("6")
        for w in [self.part_number,self.part_name,self.box_length,self.box_width,self.box_height,self.reference_instruction]: w.textChanged.connect(self.refresh_preview)
        for w in [self.quantity,self.arrangement_rows,self.parts_per_row]: w.valueChanged.connect(self.refresh_preview)
        for label,w in [("Part number",self.part_number),("Part name",self.part_name),("Box length (in)",self.box_length),("Box width (in)",self.box_width),("Box height (in)",self.box_height),("Quantity",self.quantity),("Rows",self.arrangement_rows),("Parts per row",self.parts_per_row),("Packing note",self.reference_instruction)]: form.addRow(label,w)
        self.form_layout.addLayout(form)
        self.form_layout.addWidget(self.section_label("REFERENCE IMAGES")); self.part_image=ImagePicker("part image",self.refresh_preview); self.packing_image=ImagePicker("packing reference",self.refresh_preview); self.form_layout.addWidget(self.part_image); self.form_layout.addWidget(self.packing_image)
        sh=QHBoxLayout(); sh.addWidget(self.section_label("PACKING STEPS")); sh.addStretch(); add=QPushButton("+ Add Step"); add.setObjectName("primarySmall"); add.clicked.connect(self.add_step); sh.addWidget(add); self.form_layout.addLayout(sh)
        self.steps_container=QWidget(); self.steps_layout=QVBoxLayout(self.steps_container); self.steps_layout.setContentsMargins(0,0,0,0); self.steps_layout.setSpacing(8); self.form_layout.addWidget(self.steps_container); self.form_layout.addStretch()
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(fc); splitter.addWidget(scroll)
        pp=QWidget(); pl=QVBoxLayout(pp); ph=QHBoxLayout(); ph.addWidget(self.section_label("LIVE DOCUMENT PREVIEW")); ph.addStretch(); hint=QLabel("Uses the same Formative 3D visual system as the PDF"); hint.setObjectName("muted"); ph.addWidget(hint); pl.addLayout(ph); self.preview=QTextBrowser(); self.preview.setObjectName("previewBrowser"); pl.addWidget(self.preview,1); splitter.addWidget(pp); splitter.setSizes([500,1100])

    def apply_style(self):
        self.setStyleSheet(f"""QMainWindow,QWidget{{background:{APP_BG};color:{BRAND['dark_blue']};font-family:Arial;font-size:13px}}#appTitle{{font-size:30px;font-weight:700}}#appSubtitle,#muted,#pathLabel{{color:{BRAND['olive']}}}#brandLocked{{background:{BRAND['taupe']};color:{BRAND['dark_blue']};padding:9px 10px;border-left:4px solid {BRAND['red']};font-family:monospace;font-size:10px;font-weight:700}}#sectionLabel{{color:{BRAND['red']};font-family:monospace;font-size:10px;font-weight:700;padding-top:10px;padding-bottom:5px}}#stepHeading{{font-size:15px;font-weight:700}}#dialogTitle{{font-size:24px;font-weight:700}}QPushButton{{min-height:34px;border-radius:4px;padding:0 14px;font-weight:600}}#primaryButton,#primarySmall{{background:{BRAND['dark_blue']};color:white;border:1px solid {BRAND['dark_blue']}}}#primaryButton:hover,#primarySmall:hover{{background:{BRAND['blue']}}}#secondaryButton{{background:white;color:{BRAND['dark_blue']};border:1px solid #C8CAC4}}#dangerButton{{background:white;color:{BRAND['red']};border:1px solid #F2B1AE}}QLineEdit,QSpinBox{{min-height:31px;background:white;border:1px solid #C8CAC4;padding:3px 7px;border-radius:3px}}#stepEditorCard{{background:white;border:1px solid #D6D8D2;border-radius:6px}}#imagePicker{{background:#FAFAF8;border:1px solid #D6D8D2;border-radius:5px}}#imagePreview{{background:white;border:1px dashed #AAB3B8;color:{BRAND['olive']}}}#previewBrowser{{background:#D1D4D1;border:1px solid #C9CDCA}}QScrollArea{{border:none}}""")

    def show_brand_rules(self): BrandRulesDialog(self).exec()
    def rebuild_steps(self,steps):
        while self.steps_layout.count():
            item=self.steps_layout.takeAt(0); w=item.widget()
            if w: w.deleteLater()
        self.step_editors=[]
        for i,s in enumerate(steps,1):
            e=StepEditor(i,s,self.refresh_preview,self.delete_step); self.step_editors.append(e); self.steps_layout.addWidget(e)
    def add_step(self):
        self.sync_model_from_ui(); self.guide.steps.append(PackagingStep(title=f"Step {len(self.guide.steps)+1}")); self.rebuild_steps(self.guide.steps); self.refresh_preview()
    def delete_step(self,editor):
        self.sync_model_from_ui()
        if len(self.guide.steps)<=1: QMessageBox.information(self,"Keep one step","A packaging guide must contain at least one step."); return
        self.guide.steps.pop(self.step_editors.index(editor)); self.rebuild_steps(self.guide.steps); self.refresh_preview()
    def sync_model_from_ui(self):
        self.guide.part_number=self.part_number.text().strip(); self.guide.part_name=self.part_name.text().strip(); self.guide.box_length=self.box_length.text().strip(); self.guide.box_width=self.box_width.text().strip(); self.guide.box_height=self.box_height.text().strip(); self.guide.quantity=self.quantity.value(); self.guide.arrangement_rows=self.arrangement_rows.value(); self.guide.parts_per_row=self.parts_per_row.value(); self.guide.reference_instruction=self.reference_instruction.text().strip(); self.guide.part_image_path=self.part_image.path; self.guide.packing_image_path=self.packing_image.path; self.guide.steps=[e.to_step() for e in self.step_editors]
    def load_guide_into_ui(self,g):
        self.part_number.setText(g.part_number); self.part_name.setText(g.part_name); self.box_length.setText(g.box_length); self.box_width.setText(g.box_width); self.box_height.setText(g.box_height); self.quantity.setValue(g.quantity); self.arrangement_rows.setValue(g.arrangement_rows); self.parts_per_row.setValue(g.parts_per_row); self.reference_instruction.setText(g.reference_instruction); self.part_image.set_path(g.part_image_path); self.packing_image.set_path(g.packing_image_path); self.rebuild_steps(g.steps or [PackagingStep()]); self.refresh_preview()
    def refresh_preview(self):
        if hasattr(self,"preview"): self.sync_model_from_ui(); self.preview.setHtml(render_packaging_preview(self.guide))
    def new_project(self): self.guide=default_guide(); self.current_project_path=None; self.load_guide_into_ui(self.guide)
    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,"Open PackFlow project",str(Path.home()),"PackFlow Project (*.json)")
        if path:
            try: self.guide=PackagingGuide.load(path); self.current_project_path=path; self.load_guide_into_ui(self.guide)
            except Exception as exc: QMessageBox.critical(self,"Open failed",str(exc))
    def save_project(self):
        self.sync_model_from_ui(); path=self.current_project_path
        if not path: path,_=QFileDialog.getSaveFileName(self,"Save PackFlow project","packaging_guide.json","PackFlow Project (*.json)")
        if path:
            try: self.guide.save(path); self.current_project_path=path
            except Exception as exc: QMessageBox.critical(self,"Save failed",str(exc))
    def export_pdf(self):
        self.sync_model_from_ui(); expected=self.guide.arrangement_rows*self.guide.parts_per_row
        if self.guide.quantity and expected and expected!=self.guide.quantity and QMessageBox.question(self,"Quantity mismatch",f"Rows x parts per row = {expected}, but quantity is {self.guide.quantity}. Export anyway?")!=QMessageBox.Yes: return
        path,_=QFileDialog.getSaveFileName(self,"Export PDF",f"Packaging_{self.guide.part_number or 'Guide'}.pdf","PDF (*.pdf)")
        if path:
            try: export_packaging_guide(self.guide,path); QMessageBox.information(self,"Export complete",f"PDF exported to:\n{path}")
            except Exception as exc: QMessageBox.critical(self,"Export failed",str(exc))

if __name__=="__main__":
    app=QApplication(sys.argv); app.setApplicationName("PackFlow"); w=PackFlowWindow(); w.show(); sys.exit(app.exec())
