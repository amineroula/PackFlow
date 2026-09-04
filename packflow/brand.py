from __future__ import annotations

import sys
from pathlib import Path

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

APP_BG = "#F4F4F1"
PREFERRED_HEADLINE_FONT = "Elza"
PREFERRED_ACCENT_FONT = "DM Mono"
FALLBACK_HEADLINE_FONT = "Arial"
FALLBACK_PDF_FONT = "Helvetica"
FALLBACK_PDF_MONO = "Courier"

BRAND_RULES_SUMMARY = """
FORMATIVE 3D BRAND RULES - LOCKED IN PACKFLOW

Logo
- Use the approved Formative 3D logo only.
- Do not rotate, distort, recolor, outline, shadow, or separate the mark from the wordmark.
- Keep the logo on a clean, high-contrast background with clear space around it.

Color
- Primary: Warm Red #F9423A, Olive #727562, Light Taupe #E3E4E0.
- Secondary: Dark Blue #09314A, Black #000000, White #FFFFFF.
- Accent: Blue #4C78FF, Yellow #FFBC03, Mint #70DAB4.
- Prefer one accent color per background/layout.

Typography
- Preferred headline/body typeface: Elza.
- Preferred technical/accent typeface: DM Mono.
- PackFlow uses system-safe fallbacks when those fonts are not installed.
- Avoid all-caps headlines. Technical eyebrows/callouts may use uppercase mono styling.

Graphic system
- Keep layouts premium, clean, technical, and restrained.
- Use rounded cards/expression shapes with generous negative space.
- Background texture, if used, must stay subtle and never reduce legibility.

Photography / imagery
- Favor clear tones, strong angles, useful negative space, and authentic product/manufacturing imagery.
- Avoid busy imagery and decorative overlays that interfere with the instruction.

Writing
- Always write the company name as "Formative 3D".
- Use clear, direct, active language.
- Avoid jargon, vague claims, and unnecessary copy.
- Prefer positive, practical instructions.
""".strip()


def resource_path(relative: str) -> Path:
    """Return a path that works in source and PyInstaller builds."""
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / relative
    return Path(__file__).resolve().parent.parent / relative


def logo_path() -> Path:
    return resource_path("assets/formative3d_logo.png")
