from pathlib import Path

import cv2
import numpy as np

from animadr.depth import normalize_depth_map, prepare_motion_assets


def test_normalize_uint8_depth_map_to_unit_range() -> None:
    source = np.array([[0, 127, 255]], dtype=np.uint8)

    depth = normalize_depth_map(source)

    assert depth.dtype == np.float32
    assert float(depth.min()) == 0.0
    assert float(depth.max()) == 1.0
    assert 0.49 < float(depth[0, 1]) < 0.51


def test_prepare_motion_assets_loads_relative_depth_map(tmp_path: Path) -> None:
    depth_path = tmp_path / "depth.png"
    source = np.zeros((4, 4), dtype=np.uint8)
    source[:, 2:] = 255
    assert cv2.imwrite(str(depth_path), source)

    motions = [
        {
            "depth_parallax": {
                "depth_map": "depth.png",
                "x_px": 12.0,
                "y_px": 4.0,
            }
        }
    ]

    prepared = prepare_motion_assets(
        motions,
        scene_dir=tmp_path,
        width=8,
        height=6,
    )

    params = prepared[0]["depth_parallax"]
    depth = params["depth_map"]
    assert isinstance(depth, np.ndarray)
    assert depth.shape == (6, 8)
    assert depth.dtype == np.float32
    assert float(depth.min()) == 0.0
    assert float(depth.max()) == 1.0
    assert params["x_px"] == 12.0
