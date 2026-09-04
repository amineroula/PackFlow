from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from packflow.model import PackagingGuide, default_guide
from packflow.pdf_engine import export_packaging_guide


class ImagePicker(QWidget):
    def __init__(self, label: str, changed_callback):
        super().__init__()
        self.path = ""
        self.changed_callback = changed_callback
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.button = QPushButton(f"Add {label}")
        self.preview = QLabel("No image selected")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(120)
        self.preview.setStyleSheet("border: 1px dashed #AAB3B8; background: white;")
        self.button.clicked.connect(self.choose)
        layout.addWidget(self.button)
        layout.addWidget(self.preview)

    def choose(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not path:
            return
        self.set_path(path)
        self.changed_callback()

    def set_path(self, path: str):
        self.path = path
        if path and Path(path).exists():
            pix = QPixmap(path)
            self.preview.setPixmap(pix.scaled(280, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.preview.setText("No image selected")


class PackFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PackFlow — Production Document Builder")
        self.resize(1400, 860)
        self.guide = default_guide()
        self.current_project_path = None
        self.step_editors = []
        self.build_ui()
        self.apply_style()
        self.refresh_preview()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        toolbar = QHBoxLayout()
        title = QLabel("PackFlow")
        title.setObjectName("appTitle")
        toolbar.addWidget(title)
        toolbar.addStretch()
        for text, slot in [
            ("New", self.new_project),
            ("Open", self.open_project),
            ("Save", self.save_project),
            ("Export PDF", self.export_pdf),
        ]:
            b = QPushButton(text)
            b.clicked.connect(slot)
            toolbar.addWidget(b)
        outer.addLayout(toolbar)

        splitter = QSplitter()
        outer.addWidget(splitter, 1)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.addWidget(QLabel("DOCUMENT INFORMATION"))
        form = QFormLayout()

        self.part_number = QLineEdit()
        self.part_name = QLineEdit()
        self.box_length = QLineEdit()
        self.box_width = QLineEdit()
        self.box_height = QLineEdit()
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 100000)

        for widget in [self.part_number, self.part_name, self.box_length, self.box_width, self.box_height, self.quantity]:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.refresh_preview)
            else:
                widget.valueChanged.connect(self.refresh_preview)

        form.addRow("Part number", self.part_number)
        form.addRow("Part name", self.part_name)
        form.addRow("Box length", self.box_length)
        form.addRow("Box width", self.box_width)
        form.addRow("Box height", self.box_height)
        form.addRow("Quantity", self.quantity)
        form_layout.addLayout(form)

        self.part_image = ImagePicker("part image", self.refresh_preview)
        self.packing_image = ImagePicker("packing reference", self.refresh_preview)
        form_layout.addWidget(self.part_image)
        form_layout.addWidget(self.packing_image)

        form_layout.addWidget(QLabel("PACKING STEPS"))
        for index in range(4):
            title_edit = QLineEdit()
            instruction_edit = QLineEdit()
            image = ImagePicker(f"step {index + 1} image", self.refresh_preview)
            title_edit.textChanged.connect(self.refresh_preview)
            instruction_edit.textChanged.connect(self.refresh_preview)
            card = QWidget()
            card_layout = QFormLayout(card)
            card_layout.addRow(f"Step {index + 1}", title_edit)
            card_layout.addRow("Instruction", instruction_edit)
            card_layout.addRow(image)
            form_layout.addWidget(card)
            self.step_editors.append((title_edit, instruction_edit, image))
        form_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_container)
        splitter.addWidget(scroll)

        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.addWidget(QLabel("LIVE PREVIEW"))
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.preview.setWordWrap(True)
        self.preview.setObjectName("preview")
        preview_layout.addWidget(self.preview, 1)
        splitter.addWidget(preview_panel)
        splitter.setSizes([430, 900])

        self.load_guide_into_ui(self.guide)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #F4F4F1; color: #09314A; font-size: 13px; }
            #appTitle { font-size: 28px; font-weight: 700; }
            QPushButton { background: #09314A; color: white; border: 0; padding: 9px 14px; border-radius: 4px; }
            QPushButton:hover { background: #4C78FF; }
            QLineEdit, QSpinBox { background: white; border: 1px solid #C8CAC4; padding: 7px; border-radius: 3px; }
            #preview { background: white; border: 1px solid #D6D8D2; padding: 28px; font-size: 15px; }
        """)

    def sync_model_from_ui(self):
        self.guide.part_number = self.part_number.text().strip()
        self.guide.part_name = self.part_name.text().strip()
        self.guide.box_length = self.box_length.text().strip()
        self.guide.box_width = self.box_width.text().strip()
        self.guide.box_height = self.box_height.text().strip()
        self.guide.quantity = self.quantity.value()
        self.guide.part_image_path = self.part_image.path
        self.guide.packing_image_path = self.packing_image.path
        for step, editors in zip(self.guide.steps, self.step_editors):
            title_edit, instruction_edit, image = editors
            step.title = title_edit.text().strip()
            step.instruction = instruction_edit.text().strip()
            step.image_path = image.path

    def load_guide_into_ui(self, guide: PackagingGuide):
        self.part_number.setText(guide.part_number)
        self.part_name.setText(guide.part_name)
        self.box_length.setText(guide.box_length)
        self.box_width.setText(guide.box_width)
        self.box_height.setText(guide.box_height)
        self.quantity.setValue(guide.quantity)
        self.part_image.set_path(guide.part_image_path)
        self.packing_image.set_path(guide.packing_image_path)
        for step, editors in zip(guide.steps, self.step_editors):
            title_edit, instruction_edit, image = editors
            title_edit.setText(step.title)
            instruction_edit.setText(step.instruction)
            image.set_path(step.image_path)
        self.refresh_preview()

    def refresh_preview(self):
        if not hasattr(self, "preview"):
            return
        self.sync_model_from_ui()
        steps_html = "".join(
            f"<div style='margin:10px 0;padding:12px;border:1px solid #d9e3e8'>"
            f"<b style='color:#4C78FF'>{i}</b> &nbsp; <b>{step.title}</b><br>"
            f"<span style='color:#444'>{step.instruction}</span></div>"
            for i, step in enumerate(self.guide.steps, 1)
        )
        self.preview.setText(
            f"<div style='font-family:Arial'>"
            f"<div style='font-family:monospace;color:#727562'>PACKAGING GUIDE</div>"
            f"<h1 style='color:#09314A'>{self.guide.part_number or 'PART NUMBER'} — {self.guide.part_name or 'PART NAME'}</h1>"
            f"<p><b>BOX</b> {self.guide.box_dimensions or '—'} &nbsp;&nbsp; <b>QTY</b> {self.guide.quantity or '—'}</p>"
            f"<hr><h3>PACKING STEPS</h3>{steps_html}</div>"
        )

    def new_project(self):
        self.guide = default_guide()
        self.current_project_path = None
        self.load_guide_into_ui(self.guide)

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PackFlow project", "", "PackFlow Project (*.json)")
        if not path:
            return
        try:
            self.guide = PackagingGuide.load(path)
            self.current_project_path = path
            self.load_guide_into_ui(self.guide)
        except Exception as exc:
            QMessageBox.critical(self, "Open failed", str(exc))

    def save_project(self):
        self.sync_model_from_ui()
        path = self.current_project_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Save PackFlow project", "packaging_guide.json", "PackFlow Project (*.json)")
        if not path:
            return
        self.guide.save(path)
        self.current_project_path = path

    def export_pdf(self):
        self.sync_model_from_ui()
        default_name = f"Packaging_{self.guide.part_number or 'Guide'}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", default_name, "PDF (*.pdf)")
        if not path:
            return
        try:
            export_packaging_guide(self.guide, path)
            QMessageBox.information(self, "Export complete", f"PDF exported to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackFlowWindow()
    window.show()
    sys.exit(app.exec())
