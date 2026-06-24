#!/usr/bin/env python3
"""
Recompress large PNG/lossless images inside a PDF to JPEG.

Usage:
    python3 compress_pdf_images.py input.pdf [output.pdf] [--quality 75] [--min-size 50]

Arguments:
    input.pdf       Path to the source PDF
    output.pdf      Output path (default: input_compressed.pdf)
    --quality N     JPEG quality 1-95 (default: 75)
    --min-size N    Skip images smaller than N KB (default: 50)

Requirements:
    pip install pikepdf pillow
"""

import argparse
import io
import sys
from pathlib import Path

import pikepdf
from PIL import Image


def compress_images(input_path: Path, output_path: Path, quality: int, min_size_kb: int):
    pdf = pikepdf.open(input_path)
    converted = 0
    skipped = 0

    # Walk all objects in the PDF, not just page resources — handles nested forms
    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object(objid, 0)
        except Exception:
            continue

        if not isinstance(obj, pikepdf.Stream):
            continue
        if obj.get("/Subtype") != pikepdf.Name("/Image"):
            continue

        width = int(obj.get("/Width", 0))
        height = int(obj.get("/Height", 0))
        current_filter = obj.get("/Filter")

        # Skip already-JPEG images
        if current_filter in (pikepdf.Name("/DCTDecode"), pikepdf.Name("/JPXDecode")):
            skipped += 1
            print(f"  Object {objid}: {width}x{height} — already JPEG, skipped")
            continue

        # Skip small images (icons, logos, etc.)
        raw_size_kb = width * height * 3 // 1024
        if raw_size_kb < min_size_kb:
            skipped += 1
            print(f"  Object {objid}: {width}x{height} — too small ({raw_size_kb}K), skipped")
            continue

        # Decode the image via Pillow
        try:
            raw = obj.read_raw_bytes()
            # Use stream_data for decoded pixels (pikepdf handles decompression)
            pixel_data = obj.read_bytes()
            color_components = int(obj.get("/BitsPerComponent", 8))
            cs = obj.get("/ColorSpace")

            # Determine PIL mode from color space
            n = int(obj.get("/BitsPerComponent", 8))
            if cs == pikepdf.Name("/DeviceGray") or cs == pikepdf.Name("/G"):
                mode = "L"
            elif cs == pikepdf.Name("/DeviceCMYK"):
                mode = "CMYK"
            else:
                mode = "RGB"

            img = Image.frombytes(mode, (width, height), pixel_data)
        except Exception as e:
            print(f"  Object {objid}: {width}x{height} — could not decode ({e}), skipped")
            skipped += 1
            continue

        # Convert to RGB (JPEG doesn't support alpha or CMYK well without profile)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        elif img.mode == "CMYK":
            img = img.convert("RGB")
        elif img.mode == "L":
            pass  # grayscale JPEG is fine

        # Encode to JPEG in memory
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        jpg_bytes = buf.getvalue()

        before_kb = len(obj.read_raw_bytes()) // 1024
        after_kb = len(jpg_bytes) // 1024

        # Only replace if we actually made it smaller
        if len(jpg_bytes) >= len(obj.read_raw_bytes()):
            print(f"  Object {objid}: {width}x{height} — JPEG would be larger, skipped")
            skipped += 1
            continue

        # Replace stream
        obj.write(jpg_bytes, filter=pikepdf.Name("/DCTDecode"))
        obj["/ColorSpace"] = pikepdf.Name("/DeviceRGB") if img.mode != "L" else pikepdf.Name("/DeviceGray")
        for key in ("/SMask", "/Mask", "/DecodeParms"):
            if key in obj:
                del obj[key]

        print(f"  Object {objid}: {width}x{height} — {before_kb}K → {after_kb}K")
        converted += 1

    pdf.save(output_path)
    print(f"\nDone: {converted} image(s) recompressed, {skipped} skipped")
    print(f"  {input_path.stat().st_size // 1024}K  →  {output_path.stat().st_size // 1024}K")


def main():
    parser = argparse.ArgumentParser(description="Recompress PDF images to JPEG")
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", nargs="?", help="Output PDF path (default: input_compressed.pdf)")
    parser.add_argument("--quality", type=int, default=75, help="JPEG quality (default: 75)")
    parser.add_argument("--min-size", type=int, default=50, dest="min_size",
                        help="Skip images with raw size below this many KB (default: 50)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(input_path.stem + "_compressed")

    print(f"Input:   {input_path} ({input_path.stat().st_size // 1024}K)")
    print(f"Output:  {output_path}")
    print(f"Quality: {args.quality}, min-size: {args.min_size}K\n")

    compress_images(input_path, output_path, args.quality, args.min_size)


if __name__ == "__main__":
    main()
