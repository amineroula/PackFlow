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
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from packflow.model import PackagingGuide, default_guide
from packflow.pdf_engine import export_packaging_guide
from packflow.preview_engine import render_packaging_preview


class ImagePicker(QWidget):
    def __init__(self, label: str, changed_callback):
        super().__init__()
        self.label = label
        self.path = ""
        self.changed_callback = changed_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        controls = QHBoxLayout()
        self.button = QPushButton(f"Add {label}")
        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("secondaryButton")
        controls.addWidget(self.button)
        controls.addWidget(self.remove_button)
        layout.addLayout(controls)

        self.preview = QLabel("No image selected")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(110)
        self.preview.setStyleSheet("border:1px dashed #AAB3B8; background:#FFFFFF;")
        layout.addWidget(self.preview)

        self.button.clicked.connect(self.choose)
        self.remove_button.clicked.connect(self.clear)

    def choose(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Choose {self.label}",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not path:
            return
        self.set_path(path)
        self.changed_callback()

    def clear(self):
        self.set_path("")
        self.changed_callback()

    def set_path(self, path: str):
        self.path = path
        if path and Path(path).exists():
            pix = QPixmap(path)
            self.preview.setPixmap(
                pix.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.preview.setToolTip(path)
        else:
            self.preview.setPixmap(QPixmap())
            self.preview.setText("No image selected")
            self.preview.setToolTip("")


class PackFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PackFlow — Production Document Builder")
        self.resize(1540, 940)
        self.guide = default_guide()
        self.current_project_path: str | None = None
        self.step_editors = []
        self.build_ui()
        self.apply_style()
        self.refresh_preview()
        self.statusBar().showMessage("Ready")

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 14, 16, 16)

        toolbar = QHBoxLayout()
        title_group = QVBoxLayout()
        title = QLabel("PackFlow")
        title.setObjectName("appTitle")
        subtitle = QLabel("Production Document Builder")
        subtitle.setObjectName("appSubtitle")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        toolbar.addLayout(title_group)
        toolbar.addStretch()

        for text, slot, object_name in [
            ("New", self.new_project, "secondaryButton"),
            ("Open", self.open_project, "secondaryButton"),
            ("Save", self.save_project, "secondaryButton"),
            ("Export PDF", self.export_pdf, "primaryButton"),
        ]:
            button = QPushButton(text)
            button.setObjectName(object_name)
            button.clicked.connect(slot)
            toolbar.addWidget(button)
        outer.addLayout(toolbar)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        outer.addWidget(splitter, 1)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(4, 4, 10, 4)

        form_layout.addWidget(self.section_label("DOCUMENT INFORMATION"))
        form = QFormLayout()
        form.setVerticalSpacing(10)

        self.part_number = QLineEdit()
        self.part_name = QLineEdit()
        self.box_length = QLineEdit()
        self.box_width = QLineEdit()
        self.box_height = QLineEdit()
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 100000)
        self.arrangement_rows = QSpinBox()
        self.arrangement_rows.setRange(0, 1000)
        self.parts_per_row = QSpinBox()
        self.parts_per_row.setRange(0, 100000)

        self.part_number.setPlaceholderText("300026-01")
        self.part_name.setPlaceholderText("TOP CONNECT A")
        self.box_length.setPlaceholderText("18")
        self.box_width.setPlaceholderText("12")
        self.box_height.setPlaceholderText("6")

        for widget in [
            self.part_number,
            self.part_name,
            self.box_length,
            self.box_width,
            self.box_height,
        ]:
            widget.textChanged.connect(self.refresh_preview)
        for widget in [self.quantity, self.arrangement_rows, self.parts_per_row]:
            widget.valueChanged.connect(self.refresh_preview)

        form.addRow("Part number", self.part_number)
        form.addRow("Part name", self.part_name)
        form.addRow("Box length", self.box_length)
        form.addRow("Box width", self.box_width)
        form.addRow("Box height", self.box_height)
        form.addRow("Quantity", self.quantity)
        form.addRow("Rows", self.arrangement_rows)
        form.addRow("Parts per row", self.parts_per_row)
        form_layout.addLayout(form)

        form_layout.addWidget(self.section_label("REFERENCE IMAGES"))
        self.part_image = ImagePicker("part image", self.refresh_preview)
        self.packing_image = ImagePicker("packing reference", self.refresh_preview)
        form_layout.addWidget(self.part_image)
        form_layout.addWidget(self.packing_image)

        form_layout.addWidget(self.section_label("PACKING STEPS"))
        for index in range(4):
            card = QWidget()
            card.setObjectName("stepEditorCard")
            card_layout = QFormLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)

            title_edit = QLineEdit()
            instruction_edit = QLineEdit()
            image = ImagePicker(f"step {index + 1} image", self.refresh_preview)
            title_edit.textChanged.connect(self.refresh_preview)
            instruction_edit.textChanged.connect(self.refresh_preview)

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
        preview_layout.setContentsMargins(10, 4, 4, 4)
        preview_header = QHBoxLayout()
        preview_header.addWidget(self.section_label("LIVE DOCUMENT PREVIEW"))
        preview_header.addStretch()
        preview_hint = QLabel("Preview mirrors the two-page export structure")
        preview_hint.setObjectName("muted")
        preview_header.addWidget(preview_hint)
        preview_layout.addLayout(preview_header)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        self.preview.setObjectName("previewBrowser")
        preview_layout.addWidget(self.preview, 1)
        splitter.addWidget(preview_panel)
        splitter.setSizes([450, 1050])

        self.load_guide_into_ui(self.guide)

    def section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    def apply_style(self):
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background:#F4F4F1;
                color:#09314A;
                font-family:Arial;
                font-size:13px;
            }
            #appTitle { font-size:30px; font-weight:700; }
            #appSubtitle, #muted { color:#727562; }
            #sectionLabel {
                color:#727562;
                font-family:monospace;
                font-size:11px;
                font-weight:700;
                letter-spacing:1px;
                padding-top:10px;
                padding-bottom:5px;
            }
            QPushButton {
                min-height:34px;
                border-radius:4px;
                padding:0 14px;
                font-weight:600;
            }
            #primaryButton {
                background:#09314A;
                color:#FFFFFF;
                border:1px solid #09314A;
            }
            #primaryButton:hover { background:#4C78FF; border-color:#4C78FF; }
            #secondaryButton {
                background:#FFFFFF;
                color:#09314A;
                border:1px solid #C8CAC4;
            }
            #secondaryButton:hover { border-color:#4C78FF; }
            QLineEdit, QSpinBox {
                min-height:31px;
                background:#FFFFFF;
                border:1px solid #C8CAC4;
                padding:3px 7px;
                border-radius:3px;
            }
            QLineEdit:focus, QSpinBox:focus { border:1px solid #4C78FF; }
            #stepEditorCard {
                background:#FFFFFF;
                border:1px solid #D6D8D2;
                border-radius:5px;
                margin-bottom:7px;
            }
            #previewBrowser {
                background:#D9DCDA;
                border:1px solid #C9CDCA;
            }
            QScrollArea { border:none; }
            """
        )

    def sync_model_from_ui(self):
        self.guide.part_number = self.part_number.text().strip()
        self.guide.part_name = self.part_name.text().strip()
        self.guide.box_length = self.box_length.text().strip()
        self.guide.box_width = self.box_width.text().strip()
        self.guide.box_height = self.box_height.text().strip()
        self.guide.quantity = self.quantity.value()
        self.guide.arrangement_rows = self.arrangement_rows.value()
        self.guide.parts_per_row = self.parts_per_row.value()
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
        self.arrangement_rows.setValue(guide.arrangement_rows)
        self.parts_per_row.setValue(guide.parts_per_row)
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
        self.preview.setHtml(render_packaging_preview(self.guide))

    def new_project(self):
        self.guide = default_guide()
        self.current_project_path = None
        self.load_guide_into_ui(self.guide)
        self.statusBar().showMessage("New packaging guide", 3000)

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PackFlow project",
            "",
            "PackFlow Project (*.json)",
        )
        if not path:
            return
        try:
            self.guide = PackagingGuide.load(path)
            self.current_project_path = path
            self.load_guide_into_ui(self.guide)
            self.statusBar().showMessage(f"Opened {Path(path).name}", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "Open failed", str(exc))

    def save_project(self):
        self.sync_model_from_ui()
        path = self.current_project_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PackFlow project",
                "packaging_guide.json",
                "PackFlow Project (*.json)",
            )
        if not path:
            return
        try:
            self.guide.save(path)
            self.current_project_path = path
            self.statusBar().showMessage(f"Saved {Path(path).name}", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def export_pdf(self):
        self.sync_model_from_ui()
        default_name = f"Packaging_{self.guide.part_number or 'Guide'}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            default_name,
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            export_packaging_guide(self.guide, path)
            self.statusBar().showMessage(f"Exported {Path(path).name}", 5000)
            QMessageBox.information(self, "Export complete", f"PDF exported to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackFlowWindow()
    window.show()
    sys.exit(app.exec())
