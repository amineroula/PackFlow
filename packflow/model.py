from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
import json
from pathlib import Path


@dataclass
class PackagingStep:
    title: str
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
    tag_text: str = ""
    steps: list[PackagingStep] = field(default_factory=list)

    @property
    def box_dimensions(self) -> str:
        values = [self.box_length, self.box_width, self.box_height]
        return " × ".join(v for v in values if v)

    @property
    def arrangement_text(self) -> str:
        if self.arrangement_rows > 0 and self.parts_per_row > 0:
            return f"{self.arrangement_rows} rows × {self.parts_per_row} parts"
        return "—"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PackagingGuide":
        data = dict(data)
        data["steps"] = [PackagingStep(**step) for step in data.get("steps", [])]
        allowed = {item.name for item in fields(cls)}
        clean = {key: value for key, value in data.items() if key in allowed}
        return cls(**clean)

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
        steps=[
            PackagingStep("Tape box bottom", "Tape along the bottom seam."),
            PackagingStep("Stack 28 parts in box", "Place horizontally in 2 rows of 14."),
            PackagingStep("Close and tape box", "Make sure the box is not too lumpy."),
            PackagingStep("Put tag on left side", "Place one small tag on the left side."),
        ],
    )
