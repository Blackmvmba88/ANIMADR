from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .composite import alpha_composite, ensure_rgba
from .depth import prepare_motion_assets
from .motion import MotionContext, apply_motion_chain
from .scene import LayerSpec, SceneSpec


def _load_layer(path: Path, width: int, height: int) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    image = ensure_rgba(image)
    if image.shape[1] != width or image.shape[0] != height:
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LANCZOS4)
    return image


def render_scene(scene: SceneSpec, scene_path: str | Path, output_path: str | Path) -> Path:
    scene_path = Path(scene_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    layers: list[tuple[LayerSpec, np.ndarray, list[dict[str, Any]]]] = []
    for layer in scene.layers:
        if not layer.enabled:
            continue
        file_path = (scene_path.parent / layer.file).resolve()
        source = _load_layer(file_path, scene.width, scene.height)
        motions = prepare_motion_assets(
            layer.motions,
            scene_dir=scene_path.parent,
            width=scene.width,
            height=scene.height,
        )
        layers.append((layer, source, motions))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        float(scene.fps),
        (scene.width, scene.height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {output_path}")

    total_frames = int(round(scene.duration * scene.fps))
    try:
        for frame_index in range(total_frames):
            t = frame_index / scene.fps
            ctx = MotionContext(
                t=t,
                duration=scene.duration,
                frame_index=frame_index,
                fps=float(scene.fps),
            )

            canvas = np.zeros((scene.height, scene.width, 4), dtype=np.uint8)
            canvas[:, :] = np.array(scene.background, dtype=np.uint8)

            for _layer, source, motions in layers:
                animated = apply_motion_chain(source, ctx, motions)
                canvas = alpha_composite(canvas, animated)

            writer.write(canvas[..., :3])
    finally:
        writer.release()

    return output_path
