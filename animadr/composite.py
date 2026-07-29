from __future__ import annotations

import cv2
import numpy as np


def ensure_rgba(image: np.ndarray) -> np.ndarray:
    if image is None:
        raise ValueError("Image could not be loaded")
    if image.ndim != 3:
        raise ValueError("Expected HxWxC image")
    if image.shape[2] == 4:
        return image
    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    raise ValueError(f"Unsupported channel count: {image.shape[2]}")


def alpha_composite(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    bg = ensure_rgba(background).astype(np.float32) / 255.0
    fg = ensure_rgba(foreground).astype(np.float32) / 255.0

    if bg.shape != fg.shape:
        raise ValueError(f"Layer size mismatch: {bg.shape} != {fg.shape}")

    fg_a = fg[..., 3:4]
    bg_a = bg[..., 3:4]
    out_a = fg_a + bg_a * (1.0 - fg_a)

    premult = fg[..., :3] * fg_a + bg[..., :3] * bg_a * (1.0 - fg_a)
    out_rgb = np.divide(premult, np.maximum(out_a, 1e-8), out=np.zeros_like(premult), where=out_a > 1e-8)

    out = np.concatenate([out_rgb, out_a], axis=2)
    return np.clip(out * 255.0, 0, 255).astype(np.uint8)
