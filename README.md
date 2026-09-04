# PackFlow

**Production Document Builder**

PackFlow is a desktop application for creating simple, consistent production documents from locked templates. The first module focuses on packaging guides: part information, box data, reference images, step-by-step packing instructions, live preview, project save/open, and PDF export.

## V0.1 goals

- Python + PySide6 desktop application
- Packaging Guide template
- Part number and part name
- Box dimensions and quantity
- Part and packing reference images
- Editable instruction steps
- Live document preview
- Save/open project data as JSON
- Export a branded PDF

The document engine is kept separate from the UI so future modules can add QR codes, labels, production metadata, additional templates, and database integration.
