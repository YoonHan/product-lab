#!/usr/bin/env bash
# Create a new product directory from products/_template.
# Usage: scripts/new-product.sh <product-name>
set -euo pipefail

name="${1:-}"
if [[ ! "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "usage: $0 <product-name>  (lowercase kebab-case)" >&2
  exit 1
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
dest="$root/products/$name"
if [[ -e "$dest" ]]; then
  echo "already exists: products/$name" >&2
  exit 1
fi

cp -R "$root/products/_template" "$dest"
echo "created products/$name"
