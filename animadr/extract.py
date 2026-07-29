from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def extract_layer(source_path: Path, mask_path: Path, output_path: Path) -> Path:
    source = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if source is None:
        raise FileNotFoundError(source_path)
    if mask is None:
        raise FileNotFoundError(mask_path)
    if source.shape[:2] != mask.shape[:2]:
        mask = cv2.resize(mask, (source.shape[1], source.shape[0]), interpolation=cv2.INTER_LINEAR)

    rgba = cv2.cvtColor(source, cv2.COLOR_BGR2BGRA)
    rgba[..., 3] = np.clip(mask, 0, 255).astype(np.uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), rgba):
        raise RuntimeError(f"Could not write {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an RGBA layer from a source image and grayscale mask")
    parser.add_argument("source", type=Path)
    parser.add_argument("mask", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(extract_layer(args.source, args.mask, args.output))


if __name__ == "__main__":
    main()
