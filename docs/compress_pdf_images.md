# compress_pdf_images.py

Shrinks a PDF by recompressing lossless (PNG/Deflate) images to JPEG. Useful for PDFs generated from browsers or design tools that embed uncompressed background images.

## How it works

The script walks all image objects in the PDF, decodes each lossless image, re-encodes it as JPEG at a configurable quality, and replaces the stream in-place. All other content — text, vector graphics, fonts, metadata — is preserved untouched.

## Requirements

Python 3.7+:

```bash
pip install pikepdf pillow
```

## Usage

```bash
./compress_pdf_images.py input.pdf [output.pdf] [--quality 75] [--min-size 50]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `input.pdf` | Source PDF | — |
| `output.pdf` | Output path | `input_compressed.pdf` |
| `--quality N` | JPEG quality (1–95) | `75` |
| `--min-size N` | Skip images with a raw size below N KB (avoids mangling icons/logos) | `50` |

## Examples

```bash
# Output saved as login_compressed.pdf
./compress_pdf_images.py login.pdf

# Custom output path
./compress_pdf_images.py login.pdf smaller.pdf

# Higher quality, less compression
./compress_pdf_images.py login.pdf --quality 85

# Only compress images larger than 100 KB (raw)
./compress_pdf_images.py login.pdf --min-size 100
```

## Example output

```
Input:   login.pdf (1304K)
Output:  login_compressed.pdf
Quality: 75, min-size: 50K

  Object 4: 486x1024 — 1235K → 79K

Done: 1 image(s) recompressed, 0 skipped
  1304K  →  148K
```

## Behaviour

- Already-JPEG images (`DCTDecode`, `JPXDecode`) are skipped.
- Images smaller than `--min-size` are skipped.
- If the JPEG encoding would be *larger* than the original, the image is left unchanged.
- RGBA, palette, and CMYK images are converted to RGB before encoding.
