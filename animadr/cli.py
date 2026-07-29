from __future__ import annotations

import argparse
from pathlib import Path

from .render import render_scene
from .scene import load_scene


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a layered still image scene into MP4")
    parser.add_argument("scene", type=Path, help="Path to scene JSON")
    parser.add_argument("-o", "--output", type=Path, default=Path("output.mp4"), help="Output MP4 path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scene = load_scene(args.scene)
    output = render_scene(scene, args.scene, args.output)
    print(f"Rendered: {output}")


if __name__ == "__main__":
    main()
