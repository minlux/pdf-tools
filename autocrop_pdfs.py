#!/usr/bin/env python3
"""
Auto-crop single PDF or all PDFs in a folder using pdfcrop and write results to a 'cropped/' subfolder.

Usage:
    ./autocrop_pdfs.py [folder] [--margins N] [--margins "L T R B"] [--first-page-only] [--rewrite] [--verbose]

Arguments:
    folder             Folder containing PDFs (default: current directory)
    --margins N        Add N pt margin on all sides after cropping (default: 0)
    --first-page-only  Extract only the first page before cropping (requires pikepdf)
    --rewrite          Re-render via Ghostscript after cropping to permanently remove
                       content outside the crop box (requires gs in PATH)
    --verbose          Print pdfcrop output for each file

Requires: pdfcrop (part of TeX Live / MiKTeX)
          pikepdf (for --first-page-only): pip install pikepdf
          gs / Ghostscript (for --rewrite)
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_first_page(input_path: Path, output_path: Path) -> bool:
    try:
        import pikepdf
    except ImportError:
        print("Error: pikepdf is required for --first-page-only. Run: pip install pikepdf", file=sys.stderr)
        sys.exit(1)

    try:
        with pikepdf.open(input_path) as pdf:
            dst = pikepdf.Pdf.new()
            dst.pages.append(pdf.pages[0])
            dst.save(output_path)
        return True
    except Exception as e:
        print(f"Error extracting first page: {e}", file=sys.stderr)
        return False


def rewrite_pdf(path: Path) -> bool:
    tmp_fd, tmp_str = tempfile.mkstemp(dir=path.parent, suffix=".pdf")
    tmp_path = Path(tmp_str)
    os.close(tmp_fd)
    result = subprocess.run(
        ["gs", "-o", str(tmp_path), "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
         "-dPDFSETTINGS=/prepress", "-dNOPAUSE", "-dBATCH", "-dQUIET", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        tmp_path.replace(path)
        return True
    tmp_path.unlink(missing_ok=True)
    return False


def crop_pdf(input_path: Path, output_path: Path, margins: str, verbose: bool) -> bool:
    cmd = ["pdfcrop"]
    if margins:
        cmd += ["--margins", margins]
    cmd += [str(input_path), str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if verbose or result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Auto-crop all PDFs in a folder via pdfcrop")
    parser.add_argument("folder", nargs="?", default=".", help="Folder with PDFs (default: current dir)")
    parser.add_argument("--margins", default="0",
                        help='Margin in pt after cropping. One value for all sides, '
                             'or "left top right bottom" (default: 0)')
    parser.add_argument("--first-page-only", action="store_true",
                        help="Extract only the first page before cropping (requires pikepdf)")
    parser.add_argument("--rewrite", action="store_true",
                        help="Re-render via Ghostscript after cropping to permanently remove hidden content")
    parser.add_argument("--verbose", action="store_true", help="Show pdfcrop output for each file")
    args = parser.parse_args()

    target = Path(args.folder).resolve()
    if target.is_file():
        if target.suffix.lower() != ".pdf":
            print(f"Error: '{target}' is not a PDF file", file=sys.stderr)
            sys.exit(1)
        pdfs = [target]
        out_dir = target.parent / "cropped"
    elif target.is_dir():
        pdfs = sorted(target.glob("*.pdf"))
        if not pdfs:
            print(f"No PDF files found in '{target}'")
            sys.exit(0)
        out_dir = target / "cropped"
    else:
        print(f"Error: '{target}' is not a file or directory", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(exist_ok=True)
    folder = target if target.is_dir() else target.parent

    if args.rewrite and subprocess.run(["which", "gs"], capture_output=True).returncode != 0:
        print("Error: 'gs' (Ghostscript) not found in PATH", file=sys.stderr)
        sys.exit(1)

    print(f"Input:   {target}")
    print(f"Output:  {out_dir}")
    print(f"Margins: {args.margins} pt")
    print(f"First p: {'yes' if args.first_page_only else 'no'}")
    print(f"Rewrite: {'yes (Ghostscript)' if args.rewrite else 'no'}")
    print(f"Files:   {len(pdfs)}\n")

    ok = []
    failed = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for pdf in pdfs:
            out_path = out_dir / pdf.name
            print(f"  {pdf.name} ... ", end="", flush=True)

            crop_input = pdf
            if args.first_page_only:
                tmp_path = Path(tmp_dir) / pdf.name
                if not extract_first_page(pdf, tmp_path):
                    print("FAILED (first-page-only)")
                    failed.append(pdf.name)
                    continue
                crop_input = tmp_path

            if not crop_pdf(crop_input, out_path, args.margins, args.verbose):
                print("FAILED (pdfcrop)")
                failed.append(pdf.name)
                continue

            if args.rewrite and not rewrite_pdf(out_path):
                print("FAILED (rewrite-pdf)")
                failed.append(pdf.name)
                continue

            in_kb = pdf.stat().st_size // 1024
            out_kb = out_path.stat().st_size // 1024
            print(f"{in_kb}K → {out_kb}K")
            ok.append(pdf.name)

    print(f"\nDone: {len(ok)} cropped, {len(failed)} failed")
    if failed:
        for name in failed:
            print(f"  FAILED: {name}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
