from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LayerSpec:
    name: str
    file: str
    z: int
    motions: list[dict]
    enabled: bool = True


@dataclass(frozen=True)
class SceneSpec:
    width: int
    height: int
    fps: int
    duration: float
    background: tuple[int, int, int, int]
    layers: list[LayerSpec]


def load_scene(path: str | Path) -> SceneSpec:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    canvas = data.get("canvas", {})
    width = int(canvas.get("width", 1080))
    height = int(canvas.get("height", 1920))
    fps = int(data.get("fps", 30))
    duration = float(data.get("duration", 8.0))
    background = tuple(data.get("background", [0, 0, 0, 255]))

    if width <= 0 or height <= 0 or fps <= 0 or duration <= 0:
        raise ValueError("Scene width, height, fps and duration must be positive")
    if len(background) != 4:
        raise ValueError("background must be [B, G, R, A]")

    layers: list[LayerSpec] = []
    for item in data.get("layers", []):
        layers.append(
            LayerSpec(
                name=str(item["name"]),
                file=str(item["file"]),
                z=int(item.get("z", 0)),
                motions=list(item.get("motions", [])),
                enabled=bool(item.get("enabled", True)),
            )
        )

    return SceneSpec(
        width=width,
        height=height,
        fps=fps,
        duration=duration,
        background=background,  # type: ignore[arg-type]
        layers=sorted(layers, key=lambda x: x.z),
    )
