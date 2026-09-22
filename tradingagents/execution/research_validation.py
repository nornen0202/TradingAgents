"""Temporal invariance checks; these detect some biases, not historical PIT validity."""

import numpy as np
import pandas as pd


def prefix_invariance(close, target_function, *, checkpoints=12):
    if len(close) < 3:
        raise ValueError("At least three observations required")
    full = target_function(close.copy())
    failures = []
    cuts = sorted(
        set(np.linspace(2, len(close) - 1, min(checkpoints, len(close) - 2), dtype=int))
    )
    for cut in cuts:
        prefix = target_function(close.iloc[:cut].copy())
        try:
            pd.testing.assert_frame_equal(
                full.iloc[:cut], prefix, check_exact=False, atol=1e-12, rtol=1e-12
            )
        except AssertionError:
            failures.append(str(close.index[cut - 1]))
    return {
        "passed": not failures,
        "checked_prefixes": len(cuts),
        "failed_cutoffs": failures,
    }


def warmup_invariance(close, target_function, *, lengths=(201, 252, 504)):
    full = target_function(close.copy()).iloc[-1]
    result = []
    for length in lengths:
        if length > len(close):
            continue
        short = target_function(close.iloc[-length:].copy()).iloc[-1]
        if not full.index.equals(short.index):
            raise ValueError("Warmup output changed instruments")
        delta = float((full - short).abs().max())
        result.append(
            {
                "history_rows": length,
                "max_weight_difference": delta,
                "passed": bool(np.isfinite(delta) and delta <= 1e-12),
            }
        )
    return result
