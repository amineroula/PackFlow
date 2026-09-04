from __future__ import annotations

import os
import sys
from dataclasses import dataclass
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

# PackFlow does not distribute proprietary font files. It discovers installed
# Formative 3D brand fonts on the workstation and embeds them into the PDF.
PDF_ELZA = "PackFlow-Elza"
PDF_ELZA_BOLD = "PackFlow-Elza-Bold"
PDF_DM_MONO = "PackFlow-DMMono"
PDF_DM_MONO_MEDIUM = "PackFlow-DMMono-Medium"

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
- Headline/body typeface: Elza.
- Technical/accent typeface: DM Mono.
- PackFlow refuses branded PDF export if the required brand fonts are unavailable.
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


def _font_roots() -> list[Path]:
    roots: list[Path] = []
    home = Path.home()

    if sys.platform.startswith("win"):
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        roots.extend([
            windir / "Fonts",
            Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local")) / "Microsoft/Windows/Fonts",
            Path(os.environ.get("APPDATA", home / "AppData/Roaming")) / "Adobe/CoreSync/plugins/livetype",
            Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local")) / "Adobe/CoreSync/plugins/livetype",
        ])
    elif sys.platform == "darwin":
        roots.extend([
            Path("/Library/Fonts"),
            Path("/System/Library/Fonts"),
            home / "Library/Fonts",
            home / "Library/Application Support/Adobe/CoreSync/plugins/livetype",
        ])
    else:
        roots.extend([
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            home / ".fonts",
            home / ".local/share/fonts",
        ])

    # Preserve order while removing duplicates.
    result: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root).lower()
        if key not in seen:
            seen.add(key)
            result.append(root)
    return result


def _font_candidates() -> list[Path]:
    files: list[Path] = []
    for root in _font_roots():
        if not root.exists():
            continue
        try:
            for ext in ("*.ttf", "*.otf", "*.TTF", "*.OTF"):
                files.extend(root.rglob(ext))
        except (OSError, PermissionError):
            continue
    return files


def _normalized_font_name(path: Path) -> str:
    return "".join(ch for ch in path.stem.lower() if ch.isalnum())


def _pick_font(files: list[Path], family_tokens: tuple[str, ...], weight_tokens: tuple[str, ...] = ()) -> Path | None:
    matches: list[Path] = []
    for path in files:
        name = _normalized_font_name(path)
        if all(token in name for token in family_tokens):
            matches.append(path)

    if not matches:
        return None

    if weight_tokens:
        weighted = [p for p in matches if any(token in _normalized_font_name(p) for token in weight_tokens)]
        if weighted:
            return sorted(weighted, key=lambda p: len(str(p)))[0]

    # Prefer Regular/Book if present.
    regular = [p for p in matches if any(t in _normalized_font_name(p) for t in ("regular", "book", "normal"))]
    if regular:
        return sorted(regular, key=lambda p: len(str(p)))[0]
    return sorted(matches, key=lambda p: len(str(p)))[0]


@dataclass(frozen=True)
class BrandFontStatus:
    elza_regular: Path | None
    elza_bold: Path | None
    dm_mono_regular: Path | None
    dm_mono_medium: Path | None

    @property
    def elza_ok(self) -> bool:
        return self.elza_regular is not None

    @property
    def dm_mono_ok(self) -> bool:
        return self.dm_mono_regular is not None

    @property
    def all_ok(self) -> bool:
        return self.elza_ok and self.dm_mono_ok


def detect_brand_fonts() -> BrandFontStatus:
    files = _font_candidates()
    elza_regular = _pick_font(files, ("elza",), ("regular", "book"))
    elza_bold = _pick_font(files, ("elza",), ("bold", "semibold", "demi")) or elza_regular
    dm_regular = _pick_font(files, ("dm", "mono"), ("regular",))
    dm_medium = _pick_font(files, ("dm", "mono"), ("medium", "bold")) or dm_regular
    return BrandFontStatus(elza_regular, elza_bold, dm_regular, dm_medium)


def logo_is_valid() -> bool:
    path = logo_path()
    if not path.exists() or path.stat().st_size < 100:
        return False
    try:
        from PIL import Image
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def register_pdf_brand_fonts(strict: bool = True) -> BrandFontStatus:
    """Discover and register Formative 3D fonts with ReportLab.

    Font files are read from fonts already installed on the user's workstation.
    PackFlow never bundles or redistributes Elza font files.
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    status = detect_brand_fonts()
    missing: list[str] = []
    if not status.elza_ok:
        missing.append("Elza")
    if not status.dm_mono_ok:
        missing.append("DM Mono")

    if missing:
        if strict:
            raise RuntimeError(
                "Required Formative 3D brand font(s) not found: " + ", ".join(missing) + ".\n\n"
                "Install/activate the fonts on this Windows computer (Adobe Fonts for Elza, and DM Mono), "
                "then restart PackFlow. PackFlow will not silently export a non-brand-compliant PDF."
            )
        return status

    registrations = [
        (PDF_ELZA, status.elza_regular),
        (PDF_ELZA_BOLD, status.elza_bold or status.elza_regular),
        (PDF_DM_MONO, status.dm_mono_regular),
        (PDF_DM_MONO_MEDIUM, status.dm_mono_medium or status.dm_mono_regular),
    ]
    for alias, path in registrations:
        if alias not in pdfmetrics.getRegisteredFontNames():
            try:
                pdfmetrics.registerFont(TTFont(alias, str(path)))
            except Exception as exc:
                if strict:
                    raise RuntimeError(
                        f"PackFlow found {path.name} but ReportLab could not embed it. "
                        "Use a TrueType/OpenType version with TrueType outlines.\n\n"
                        f"Technical detail: {exc}"
                    ) from exc
    return status


def validate_brand_assets(strict_fonts: bool = False) -> tuple[bool, str]:
    logo_ok = logo_is_valid()
    fonts = detect_brand_fonts()
    pieces = [
        f"Logo {'✓' if logo_ok else '✗'}",
        f"Elza {'✓' if fonts.elza_ok else '✗'}",
        f"DM Mono {'✓' if fonts.dm_mono_ok else '✗'}",
    ]
    ok = logo_ok and (fonts.all_ok if strict_fonts else True)
    return ok, "  |  ".join(pieces)
