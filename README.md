# PackFlow

**Production Document Builder**

PackFlow is a desktop application for creating simple, consistent production documents from locked templates. The first module focuses on packaging guides: part information, box data, reference images, step-by-step packing instructions, live preview, project save/open, and PDF export.

## Current V0.1 status

Implemented:

- Python + PySide6 desktop application
- Packaging Guide 01 data model
- Part number and part name
- Box dimensions and quantity
- Configurable row arrangement
- Part and packing reference images
- Four editable instruction steps with images
- Branded two-page live document preview
- Save/open project data as JSON
- Branded two-page PDF export
- Formative 3D palette integrated into the UI and document renderer
- Preflight validation module for missing fields, missing images, and quantity/arrangement mismatches

## Next development targets

1. Wire preflight validation into export and show a compact issues panel.
2. Add reusable tag/label fields and tag preview.
3. Add QR-code generation with configurable destination data.
4. Add a template registry so additional production-document templates can be added without rewriting the UI.
5. Add template-specific field visibility and defaults.
6. Add recent projects and reusable part/package presets.
7. Package PackFlow as a Windows executable.

## Architecture

The document engine is kept separate from the UI. This lets PackFlow later support QR codes, labels, production metadata, additional templates, databases, and other production modules without coupling those features to the desktop interface.

```text
PackFlow UI
    ↓
Project Data Model
    ↓
Template / Preview Engine
    ↓
PDF Renderer
    ↓
Production Document
```
