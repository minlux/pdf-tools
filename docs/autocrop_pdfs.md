# autocrop_pdfs.py

Auto-crops PDFs using `pdfcrop`, writing results into a `cropped/` subfolder. Accepts either a single PDF file or a folder (processes all PDFs inside). Removes empty whitespace margins from each page.

## Requirements

`pdfcrop` from TeX Live or MiKTeX:

```bash
# Debian/Ubuntu
sudo apt install texlive-extra-utils

# macOS
brew install --cask mactex
```

## Usage

```bash
./autocrop_pdfs.py [file.pdf|folder] [--margins N] [--rewrite] [--verbose]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `file.pdf` or `folder` | Single PDF file or folder containing PDFs | current directory |
| `--margins N` | Add N pt padding around cropped content | `0` |
| `--margins "L T R B"` | Per-side padding (left top right bottom) | — |
| `--rewrite` | Re-render via Ghostscript to permanently remove hidden content | off |
| `--verbose` | Show full pdfcrop output for each file | off |

The output is always written to a `cropped/` subfolder: next to the file when a single PDF is given, inside the folder when a directory is given.

### Note on `--rewrite`

`pdfcrop` only adjusts the page boundary (MediaBox) — content outside the crop box is hidden but still present in the file. Passing `--rewrite` pipes each cropped PDF through Ghostscript (`rewrite-pdf`), which re-renders the page and permanently discards anything outside the visible area. Requires `rewrite-pdf` to be available in `PATH`.

## Examples

```bash
# Crop a single file → saved to cropped/invoice.pdf
./autocrop_pdfs.py invoice.pdf

# Crop all PDFs in the current folder
./autocrop_pdfs.py

# Crop all PDFs in a specific folder
./autocrop_pdfs.py ~/Documents/invoices

# Add 10 pt margin on all sides
./autocrop_pdfs.py ~/Documents/invoices --margins 10

# Different margin per side: top=5 right=10 bottom=5 left=10
./autocrop_pdfs.py . --margins "5 10 5 10"

# Crop and permanently remove hidden content via Ghostscript
./autocrop_pdfs.py invoice.pdf --rewrite
./autocrop_pdfs.py . --rewrite

# Trim 610pt from the bottom (e.g. to cut off a footer)
./autocrop_pdfs.py invoice.pdf --margins '0 0 0 -610' --rewrite
```

## Example output

```
Input:   /home/user/documents
Output:  /home/user/documents/cropped
Margins: 0 pt
Files:   4

  invoice-jan.pdf ... 113K → 93K
  invoice-feb.pdf ... 107K → 98K
  report.pdf ...      210K → 185K
  summary.pdf ...      72K → 67K

Done: 4 cropped, 0 failed
```
