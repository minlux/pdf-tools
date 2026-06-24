# pdf-tools

A collection of command-line scripts for processing PDF files.

## Tools

| Script | Description |
|---|---|
| [`compress_pdf_images.py`](docs/compress_pdf_images.md) | Shrink a PDF by recompressing lossless images to JPEG |
| [`autocrop_pdfs.py`](docs/autocrop_pdfs.md) | Batch auto-crop all PDFs in a folder, removing empty margins |
| `rewrite_pdf.sh` | Re-render a PDF via Ghostscript to permanently remove content outside crop boxes |
| `svg_to_pdf.sh` | Convert SVG files to PDF via Inkscape (single file, list, or folder) |

## Requirements

### compress_pdf_images.py

Python 3.7+:

```bash
pip install pikepdf pillow
```

### autocrop_pdfs.py

`pdfcrop` from TeX Live or MiKTeX:

```bash
# Debian/Ubuntu
sudo apt install texlive-extra-utils

# macOS
brew install --cask mactex
```

### rewrite_pdf.sh

Ghostscript:

```bash
# Debian/Ubuntu
sudo apt install ghostscript

# macOS
brew install ghostscript
```

### svg_to_pdf.sh

Inkscape:

```bash
# Debian/Ubuntu
sudo apt install inkscape

# macOS
brew install --cask inkscape
```
