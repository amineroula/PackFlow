from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
import json
from pathlib import Path


@dataclass
class PackagingStep:
    title: str = "New step"
    instruction: str = ""
    image_path: str = ""


@dataclass
class PackagingGuide:
    template_id: str = "packaging_guide_01"
    part_number: str = ""
    part_name: str = ""
    box_length: str = ""
    box_width: str = ""
    box_height: str = ""
    quantity: int = 0
    arrangement_rows: int = 2
    parts_per_row: int = 14
    part_image_path: str = ""
    packing_image_path: str = ""
    reference_instruction: str = "Place the parts horizontally in even rows as shown."
    steps: list[PackagingStep] = field(default_factory=list)

    @property
    def box_dimensions(self) -> str:
        values = [self.box_length, self.box_width, self.box_height]
        if not any(values):
            return "-"
        return " x ".join(v or "-" for v in values) + " in"

    @property
    def arrangement_text(self) -> str:
        if self.arrangement_rows > 0 and self.parts_per_row > 0:
            return f"{self.arrangement_rows} rows x {self.parts_per_row} parts"
        return "-"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PackagingGuide":
        data = dict(data)
        data["steps"] = [PackagingStep(**step) for step in data.get("steps", [])]
        allowed = {item.name for item in fields(cls)}
        clean = {key: value for key, value in data.items() if key in allowed}
        guide = cls(**clean)
        if not guide.steps:
            guide.steps = [PackagingStep()]
        return guide

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "PackagingGuide":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def default_guide() -> PackagingGuide:
    return PackagingGuide(
        quantity=28,
        arrangement_rows=2,
        parts_per_row=14,
        reference_instruction="Place the parts horizontally in two even rows as shown.",
        steps=[
            PackagingStep("Tape box bottom.", "Tape directly along the bottom seam."),
            PackagingStep("Stack 28 parts in box.", "Place the parts horizontally. Make 2 rows of 14 parts (28 total)."),
            PackagingStep("Close and tape box.", "Make sure the box is not too lumpy."),
            PackagingStep("Put tag on left side.", "Use one small white tag with the part image and identifying text."),
        ],
    )
