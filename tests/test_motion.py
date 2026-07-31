import numpy as np

from animadr.composite import alpha_composite
from animadr.motion import (
    MotionContext,
    breathe,
    depth_parallax,
    liquid,
    translate,
)


def sample_rgba(size: int = 32) -> np.ndarray:
    image = np.zeros((size, size, 4), dtype=np.uint8)
    image[8:24, 8:24] = (40, 80, 200, 255)
    return image


def test_translate_keeps_shape() -> None:
    image = sample_rgba()
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)
    out = translate(image, ctx, x_px=4, y_px=2)
    assert out.shape == image.shape


def test_breathe_keeps_shape() -> None:
    image = sample_rgba()
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)
    out = breathe(image, ctx, amount=0.05)
    assert out.shape == image.shape


def test_liquid_keeps_shape() -> None:
    image = sample_rgba()
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)
    out = liquid(image, ctx, amplitude=2.0)
    assert out.shape == image.shape


def test_depth_parallax_keeps_shape_and_is_deterministic() -> None:
    image = sample_rgba()
    depth = np.tile(np.linspace(0.0, 1.0, image.shape[1], dtype=np.float32), (image.shape[0], 1))
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)

    first = depth_parallax(image, ctx, depth, x_px=5.0, y_px=2.0)
    second = depth_parallax(image, ctx, depth, x_px=5.0, y_px=2.0)

    assert first.shape == image.shape
    assert np.array_equal(first, second)


def test_zero_depth_map_is_identity() -> None:
    image = sample_rgba()
    depth = np.zeros(image.shape[:2], dtype=np.float32)
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)

    out = depth_parallax(image, ctx, depth, x_px=8.0, y_px=4.0)

    assert np.array_equal(out, image)


def test_near_plane_moves_pixels() -> None:
    image = sample_rgba()
    depth = np.ones(image.shape[:2], dtype=np.float32)
    ctx = MotionContext(t=0.25, duration=1.0, frame_index=7, fps=30.0)

    out = depth_parallax(image, ctx, depth, x_px=5.0, y_px=0.0)

    assert not np.array_equal(out, image)


def test_alpha_composite_preserves_rgba() -> None:
    bg = np.zeros((16, 16, 4), dtype=np.uint8)
    bg[:] = (0, 0, 0, 255)
    fg = np.zeros((16, 16, 4), dtype=np.uint8)
    fg[4:12, 4:12] = (255, 255, 255, 128)
    out = alpha_composite(bg, fg)
    assert out.shape == bg.shape
    assert out[..., 3].min() == 255
