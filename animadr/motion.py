from __future__ import annotations

import math
from dataclasses import dataclass

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


def rotate(image: np.ndarray, ctx: MotionContext, speed_deg_s: float = 5.0, cx: float = 0.5, cy: float = 0.5) -> np.ndarray:
    h, w = image.shape[:2]
    angle = speed_deg_s * ctx.t
    matrix = cv2.getRotationMatrix2D((w * cx, h * cy), angle, 1.0)
    return _warp_affine_rgba(image, matrix)


def translate(image: np.ndarray, ctx: MotionContext, x_px: float = 0.0, y_px: float = 0.0, cycles: float = 1.0) -> np.ndarray:
    phase = ctx.phase * cycles
    dx = math.sin(phase) * x_px
    dy = math.cos(phase) * y_px
    matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy]], dtype=np.float32)
    return _warp_affine_rgba(image, matrix)


def breathe(image: np.ndarray, ctx: MotionContext, amount: float = 0.02, cycles: float = 1.0) -> np.ndarray:
    h, w = image.shape[:2]
    scale = 1.0 + math.sin(ctx.phase * cycles) * amount
    matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), 0.0, scale)
    return _warp_affine_rgba(image, matrix)


def liquid(image: np.ndarray, ctx: MotionContext, amplitude: float = 8.0, frequency: float = 0.018, speed: float = 1.0) -> np.ndarray:
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


def sway(image: np.ndarray, ctx: MotionContext, angle_deg: float = 3.0, cycles: float = 1.0, pivot_x: float = 0.5, pivot_y: float = 0.9) -> np.ndarray:
    h, w = image.shape[:2]
    angle = math.sin(ctx.phase * cycles) * angle_deg
    matrix = cv2.getRotationMatrix2D((w * pivot_x, h * pivot_y), angle, 1.0)
    return _warp_affine_rgba(image, matrix)


MOTION_REGISTRY = {
    "rotate": rotate,
    "translate": translate,
    "breathe": breathe,
    "liquid": liquid,
    "sway": sway,
}


def apply_motion_chain(image: np.ndarray, ctx: MotionContext, motions: list[dict]) -> np.ndarray:
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
