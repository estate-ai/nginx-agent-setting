from __future__ import annotations

from typing import Any

import numpy as np

SCORE_CALIBRATION_VERSION = "robust_sigmoid_quantile_v1"
DEFAULT_SCORE_CENTER = 0.0
DEFAULT_SCORE_SCALE = 4.0
MIN_SCORE_SCALE = 1e-6
SCORE_EPSILON = 1e-3


def build_score_calibration(scores: np.ndarray) -> dict[str, float | str]:
    flattened = np.asarray(scores, dtype=np.float64).reshape(-1)
    finite_scores = flattened[np.isfinite(flattened)]
    if finite_scores.size == 0:
        return {
            "version": SCORE_CALIBRATION_VERSION,
            "center": DEFAULT_SCORE_CENTER,
            "scale": DEFAULT_SCORE_SCALE,
            "min": DEFAULT_SCORE_CENTER,
            "p05": DEFAULT_SCORE_CENTER,
            "p50": DEFAULT_SCORE_CENTER,
            "p95": DEFAULT_SCORE_CENTER,
            "max": DEFAULT_SCORE_CENTER,
        }

    p05, p50, p95 = np.quantile(finite_scores, [0.05, 0.5, 0.95])
    robust_scale = float((p95 - p05) / 4.0)
    fallback_scale = float(np.std(finite_scores))
    scale = max(robust_scale, fallback_scale, DEFAULT_SCORE_SCALE, MIN_SCORE_SCALE)
    return {
        "version": SCORE_CALIBRATION_VERSION,
        "center": round(float(p50), 6),
        "scale": round(float(scale), 6),
        "min": round(float(np.min(finite_scores)), 6),
        "p05": round(float(p05), 6),
        "p50": round(float(p50), 6),
        "p95": round(float(p95), 6),
        "max": round(float(np.max(finite_scores)), 6),
    }


def scale_scores_to_unit_interval(
    scores: np.ndarray,
    calibration: dict[str, Any] | None = None,
) -> np.ndarray:
    center = DEFAULT_SCORE_CENTER
    scale = DEFAULT_SCORE_SCALE
    if calibration:
        center = float(calibration.get("center", center))
        scale = float(calibration.get("scale", scale))
    if not np.isfinite(scale) or scale < MIN_SCORE_SCALE:
        scale = DEFAULT_SCORE_SCALE
    if not np.isfinite(center):
        center = DEFAULT_SCORE_CENTER

    normalized = (np.asarray(scores, dtype=np.float64) - center) / scale
    normalized = np.clip(normalized, -8.0, 8.0)
    scaled = 1.0 / (1.0 + np.exp(-normalized))
    return np.clip(scaled, SCORE_EPSILON, 1.0 - SCORE_EPSILON).astype(np.float32)
