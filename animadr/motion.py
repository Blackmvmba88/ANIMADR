from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class MotionContext:
    t: float
    duration: float
    frame_index: int
    fps: float

    @property
    def phase(self) -> float:
        if self.duration <= 0:
            return 0.0
        return (self.t / self.duration) * (2.0 * math.pi)


def _warp_affine_rgba(image: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )


def rotate(
    image: np.ndarray,
    ctx: MotionContext,
    speed_deg_s: float = 5.0,
    cx: float = 0.5,
    cy: float = 0.5,
) -> np.ndarray:
    h, w = image.shape[:2]
    angle = speed_deg_s * ctx.t
    matrix = cv2.getRotationMatrix2D((w * cx, h * cy), angle, 1.0)
    return _warp_affine_rgba(image, matrix)


def translate(
    image: np.ndarray,
    ctx: MotionContext,
    x_px: float = 0.0,
    y_px: float = 0.0,
    cycles: float = 1.0,
) -> np.ndarray:
    phase = ctx.phase * cycles
    dx = math.sin(phase) * x_px
    dy = math.cos(phase) * y_px
    matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy]], dtype=np.float32)
    return _warp_affine_rgba(image, matrix)


def breathe(
    image: np.ndarray,
    ctx: MotionContext,
    amount: float = 0.02,
    cycles: float = 1.0,
) -> np.ndarray:
    h, w = image.shape[:2]
    scale = 1.0 + math.sin(ctx.phase * cycles) * amount
    matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), 0.0, scale)
    return _warp_affine_rgba(image, matrix)


def liquid(
    image: np.ndarray,
    ctx: MotionContext,
    amplitude: float = 8.0,
    frequency: float = 0.018,
    speed: float = 1.0,
) -> np.ndarray:
    h, w = image.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    p = ctx.t * speed
    map_x = xx + amplitude * np.sin(yy * frequency + p)
    map_y = yy + amplitude * np.cos(xx * frequency + p * 0.8)
    return cv2.remap(
        image,
        map_x.astype(np.float32),
        map_y.astype(np.float32),
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )


def sway(
    image: np.ndarray,
    ctx: MotionContext,
    angle_deg: float = 3.0,
    cycles: float = 1.0,
    pivot_x: float = 0.5,
    pivot_y: float = 0.9,
) -> np.ndarray:
    h, w = image.shape[:2]
    angle = math.sin(ctx.phase * cycles) * angle_deg
    matrix = cv2.getRotationMatrix2D((w * pivot_x, h * pivot_y), angle, 1.0)
    return _warp_affine_rgba(image, matrix)


def depth_parallax(
    image: np.ndarray,
    ctx: MotionContext,
    depth_map: np.ndarray,
    x_px: float = 18.0,
    y_px: float = 8.0,
    cycles: float = 1.0,
    phase_offset: float = 0.0,
    depth_gamma: float = 1.0,
    invert_depth: bool = False,
) -> np.ndarray:
    """Warp pixels according to their depth and a deterministic camera orbit.

    The depth map must be normalized to [0, 1], where zero is the far plane
    and one is the near plane. Near pixels move farther than distant pixels.
    """

    if depth_gamma <= 0:
        raise ValueError("depth_gamma must be positive")
    if depth_map.ndim != 2:
        raise ValueError("depth_map must be a normalized HxW array")
    if depth_map.shape != image.shape[:2]:
        raise ValueError(
            f"Depth-map size mismatch: {depth_map.shape} != {image.shape[:2]}"
        )

    depth = np.clip(depth_map.astype(np.float32), 0.0, 1.0)
    if invert_depth:
        depth = 1.0 - depth
    weight = np.power(depth, depth_gamma).astype(np.float32)

    phase = ctx.phase * cycles + phase_offset
    camera_x = math.sin(phase) * x_px
    camera_y = math.cos(phase) * y_px

    h, w = image.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    map_x = xx - camera_x * weight
    map_y = yy - camera_y * weight

    return cv2.remap(
        image,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )


MOTION_REGISTRY = {
    "rotate": rotate,
    "translate": translate,
    "breathe": breathe,
    "liquid": liquid,
    "sway": sway,
    "depth_parallax": depth_parallax,
}


def apply_motion_chain(
    image: np.ndarray,
    ctx: MotionContext,
    motions: list[dict[str, Any]],
) -> np.ndarray:
    out = image
    for spec in motions:
        if not isinstance(spec, dict) or len(spec) != 1:
            raise ValueError(f"Invalid motion spec: {spec!r}")
        name, params = next(iter(spec.items()))
        fn = MOTION_REGISTRY.get(name)
        if fn is None:
            raise ValueError(f"Unknown motion: {name}")
        out = fn(out, ctx, **(params or {}))
    return out
