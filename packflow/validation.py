from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import PackagingGuide


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    message: str


def validate_guide(guide: PackagingGuide) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not guide.part_number:
        issues.append(ValidationIssue("error", "Part number is required."))
    if not guide.part_name:
        issues.append(ValidationIssue("warning", "Part name is empty."))
    if guide.quantity <= 0:
        issues.append(ValidationIssue("error", "Quantity must be greater than zero."))

    expected = guide.arrangement_rows * guide.parts_per_row
    if guide.arrangement_rows > 0 and guide.parts_per_row > 0 and expected != guide.quantity:
        issues.append(
            ValidationIssue(
                "warning",
                f"Arrangement contains {expected} parts but quantity is {guide.quantity}.",
            )
        )

    for label, path in [
        ("Part image", guide.part_image_path),
        ("Packing reference", guide.packing_image_path),
    ]:
        if not path:
            issues.append(ValidationIssue("warning", f"{label} is missing."))
        elif not Path(path).exists():
            issues.append(ValidationIssue("error", f"{label} file cannot be found."))

    for index, step in enumerate(guide.steps[:4], start=1):
        if not step.title:
            issues.append(ValidationIssue("warning", f"Step {index} has no title."))
        if not step.image_path:
            issues.append(ValidationIssue("warning", f"Step {index} image is missing."))
        elif not Path(step.image_path).exists():
            issues.append(ValidationIssue("error", f"Step {index} image file cannot be found."))

    return issues
