from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


def normalize_depth_map(
    depth_map: np.ndarray,
    *,
    width: int | None = None,
    height: int | None = None,
) -> np.ndarray:
    """Return a finite float32 depth map in the inclusive range [0, 1].

    Black represents the far plane and white represents the near plane.
    RGB/RGBA maps are converted to grayscale. A target width and height can
    be supplied to make the map match the render canvas.
    """

    depth = np.asarray(depth_map)
    if depth.ndim == 3:
        channels = depth.shape[2]
        if channels == 4:
            depth = cv2.cvtColor(depth, cv2.COLOR_BGRA2GRAY)
        elif channels == 3:
            depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError(f"Unsupported depth-map channel count: {channels}")
    elif depth.ndim != 2:
        raise ValueError("Depth map must be HxW, HxWx3 or HxWx4")

    if width is not None or height is not None:
        if width is None or height is None or width <= 0 or height <= 0:
            raise ValueError("width and height must both be positive")
        if depth.shape[1] != width or depth.shape[0] != height:
            depth = cv2.resize(depth, (width, height), interpolation=cv2.INTER_LINEAR)

    depth = depth.astype(np.float32)
    depth = np.nan_to_num(depth, nan=0.0, posinf=1.0, neginf=0.0)
    if depth.size and float(depth.max()) > 1.0:
        depth /= 255.0
    return np.clip(depth, 0.0, 1.0)


def load_depth_map(path: str | Path, *, width: int, height: int) -> np.ndarray:
    path = Path(path)
    depth = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if depth is None:
        raise FileNotFoundError(path)
    return normalize_depth_map(depth, width=width, height=height)


def prepare_motion_assets(
    motions: list[dict[str, Any]],
    *,
    scene_dir: str | Path,
    width: int,
    height: int,
) -> list[dict[str, Any]]:
    """Resolve external motion assets without mutating the scene contract."""

    scene_dir = Path(scene_dir)
    prepared: list[dict[str, Any]] = []

    for spec in motions:
        if not isinstance(spec, dict) or len(spec) != 1:
            raise ValueError(f"Invalid motion spec: {spec!r}")

        name, raw_params = next(iter(spec.items()))
        params = dict(raw_params or {})

        if name == "depth_parallax":
            depth_map = params.get("depth_map")
            if isinstance(depth_map, (str, Path)):
                params["depth_map"] = load_depth_map(
                    (scene_dir / depth_map).resolve(),
                    width=width,
                    height=height,
                )
            elif isinstance(depth_map, np.ndarray):
                params["depth_map"] = normalize_depth_map(
                    depth_map,
                    width=width,
                    height=height,
                )
            else:
                raise ValueError("depth_parallax requires a depth_map path or ndarray")

        prepared.append({name: params})

    return prepared
