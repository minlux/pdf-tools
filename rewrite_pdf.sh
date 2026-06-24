#!/bin/bash

if ! command -v gs &>/dev/null; then
  echo "Error: 'gs' (Ghostscript) not found in PATH." >&2
  exit 1
fi

if [ -z "$1" ]; then
  echo "Error: No PDF file provided." >&2
  echo "Usage: $0 <input.pdf> [output.pdf]" >&2
  exit 1
fi

input="$1"
output="${2:-$1}"

if [ ! -f "$input" ]; then
  echo "Error: File not found: $input" >&2
  exit 1
fi

tmp=$(mktemp --suffix=.pdf)

gs -o "$tmp" -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/prepress -dNOPAUSE -dBATCH -dQUIET \
   "$input"

if [ $? -ne 0 ]; then
  echo "Error: Ghostscript failed on '$input'." >&2
  rm -f "$tmp"
  exit 1
fi

before=$(du -k "$input" | cut -f1)
mv "$tmp" "$output"
after=$(du -k "$output" | cut -f1)

echo "${before}K → ${after}K  $output"
