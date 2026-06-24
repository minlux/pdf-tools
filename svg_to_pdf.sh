#!/bin/bash

if ! command -v inkscape &>/dev/null; then
  echo "Error: 'inkscape' not found in PATH." >&2
  exit 1
fi

if [ -z "$1" ]; then
  echo "Error: No input provided." >&2
  echo "Usage: $0 <file.svg> [file.svg ...]" >&2
  echo "       $0 <folder>" >&2
  exit 1
fi

svgs=()

for arg in "$@"; do
  if [ -d "$arg" ]; then
    while IFS= read -r -d '' f; do
      svgs+=("$f")
    done < <(find "$arg" -maxdepth 1 -name "*.svg" -print0 | sort -z)
  elif [ -f "$arg" ]; then
    if [[ "$arg" != *.svg ]]; then
      echo "Warning: '$arg' is not an SVG file, skipping." >&2
    else
      svgs+=("$arg")
    fi
  else
    echo "Warning: '$arg' not found, skipping." >&2
  fi
done

if [ ${#svgs[@]} -eq 0 ]; then
  echo "No SVG files found." >&2
  exit 1
fi

echo "Files: ${#svgs[@]}"
echo ""

ok=0
failed=0

for svg in "${svgs[@]}"; do
  pdf="${svg%.svg}.pdf"
  printf "  %s ... " "$(basename "$svg")"

  output=$(inkscape --export-type=pdf "$svg" 2>&1)

  if [ $? -ne 0 ]; then
    echo "FAILED"
    echo "$output" >&2
    ((failed++))
    continue
  fi

  in_kb=$(du -k "$svg" | cut -f1)
  out_kb=$(du -k "$pdf" | cut -f1)
  echo "${in_kb}K → ${out_kb}K"
  ((ok++))
done

echo ""
echo "Done: $ok converted, $failed failed"
[ $failed -gt 0 ] && exit 1
exit 0
