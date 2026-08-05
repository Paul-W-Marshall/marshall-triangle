"""
Regression tests for HarmonyIndex.render() — vectorised implementation.

Strategy
--------
1. A pixel-loop *reference* renderer is implemented here, mirroring the
   original pre-vectorisation logic (including the final GaussianBlur pass).
   The vectorised render() output is compared against this reference for a
   representative grid of harmonyState values.

2. Property tests check structural invariants that should hold regardless
   of harmonyState (triangle painted, dominant hue near each midpoint,
   exterior pixels black, etc.).

3. Cache-key quantisation tests verify that adjacent slider steps within the
   same 0.05 bucket produce identical quantised values (cache hits), while
   steps crossing a bucket boundary produce distinct values (cache misses).

Run:
    python -m pytest test_harmony_render.py -v
"""

import itertools
import sys
import types
import unittest.mock as mock
import numpy as np
import pytest
from PIL import Image, ImageFilter
from scipy import ndimage

from harmony_index import HarmonyIndex

# ---------------------------------------------------------------------------
# Stub streamlit so app.py can be imported without a running Streamlit server
# ---------------------------------------------------------------------------

def _make_streamlit_stub():
    """Return a minimal MagicMock that satisfies app.py's top-level imports."""
    st = mock.MagicMock()
    # cache_data must return a decorator that passes the function through
    def _cache_data(*args, **kwargs):
        def _decorator(fn):
            return fn
        # Handle both @st.cache_data and @st.cache_data(...) call styles
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]
        return _decorator
    st.cache_data = _cache_data
    return st

_st_stub = _make_streamlit_stub()
sys.modules.setdefault("streamlit", _st_stub)

# Import _quantise after the stub is in place
from app import _quantise  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIZE = 100          # small size → fast; still shows structural features
# Tolerance is intentionally generous (5 counts out of 255): the pixel loop
# accumulates results sequentially while the vectorised path uses float64
# throughout; both then get quantised by uint8 conversion, and the subsequent
# GaussianBlur spreads any residual error into neighbouring pixels.
ATOL = 5


# ---------------------------------------------------------------------------
# Reference pixel-loop renderer
# ---------------------------------------------------------------------------

def _reference_render(hi: HarmonyIndex, harmonyState: dict,
                      falloff_type: str = "gaussian") -> np.ndarray:
    """
    Pixel-loop reference that replicates the original pre-vectorisation logic,
    including the final GaussianBlur pass applied by HarmonyIndex.render().
    """
    # ---------- normalise / clamp (mirrors HarmonyIndex.render preamble) ----------
    state = {}
    for key in ["r", "g", "b"]:
        state[key] = max(0.0, min(1.0, harmonyState.get(key, 1.0)))

    max_cal = max(hi.calibrated_white_point.values())
    norm_state = {}
    for key in ["r", "g", "b"]:
        cwp = hi.calibrated_white_point[key]
        if cwp < 0.01:
            norm_state[key] = state[key] * max_cal
        else:
            norm_state[key] = state[key] * (max_cal / cwp)

    # ---------- geometry ----------
    x_lin = np.linspace(-1, 1, hi.size)
    y_lin = np.linspace(-1, 1, hi.size)
    xg, yg = np.meshgrid(x_lin, y_lin)

    vertices = hi._define_triangle()
    midpoints = hi._calculate_midpoints(vertices)
    v1, v2, v3 = vertices

    state_weights = [norm_state["r"], norm_state["g"], norm_state["b"]]

    red   = np.zeros((hi.size, hi.size), dtype=float)
    green = np.zeros((hi.size, hi.size), dtype=float)
    blue  = np.zeros((hi.size, hi.size), dtype=float)
    mask  = np.zeros((hi.size, hi.size), dtype=bool)

    sigma_eff = hi.sigma * 1.8

    for i in range(hi.size):
        for j in range(hi.size):
            x = xg[i, j]
            y = yg[hi.size - 1 - i, j]   # same as np.flipud(yg)[i, j]

            # Triangle membership (sign-test + buffer — mirrors vectorised code)
            def _sign(p1x, p1y, p2x, p2y, p3x, p3y):
                return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

            buf = 0.005
            d1 = _sign(x, y, v1[0], v1[1], v2[0], v2[1])
            d2 = _sign(x, y, v2[0], v2[1], v3[0], v3[1])
            d3 = _sign(x, y, v3[0], v3[1], v1[0], v1[1])
            inside = not (
                ((d1 < -buf) or (d2 < -buf) or (d3 < -buf)) and
                ((d1 >  buf) or (d2 >  buf) or (d3 >  buf))
            )
            mask[i, j] = inside
            if not inside:
                continue

            # Falloff per midpoint → one channel each
            for k, (mx, my) in enumerate(midpoints):
                dist_sq = (x - mx) ** 2 + (y - my) ** 2
                if falloff_type == "gaussian":
                    val = np.exp(-dist_sq / (2 * sigma_eff ** 2)) * hi.intensity
                else:
                    val = hi.intensity * 0.8 / (dist_sq + 0.05)
                val *= state_weights[k]
                if k == 0:
                    red[i, j] = val
                elif k == 1:
                    green[i, j] = val
                else:
                    blue[i, j] = val

    # Edge attenuation
    edges = ndimage.binary_dilation(mask) & ~mask
    red[edges]   *= hi.edge_factor
    green[edges] *= hi.edge_factor
    blue[edges]  *= hi.edge_factor

    # Normalise
    max_val = np.maximum.reduce([red, green, blue])
    max_val = np.maximum(max_val, 1e-10)
    norm = np.minimum(max_val, 1.0)
    mask_norm = norm > 0.1
    red[mask_norm]   /= norm[mask_norm]
    green[mask_norm] /= norm[mask_norm]
    blue[mask_norm]  /= norm[mask_norm]

    img_arr = np.stack(
        [np.clip(red, 0, 1), np.clip(green, 0, 1), np.clip(blue, 0, 1)], axis=-1
    )
    img_arr = (img_arr * 255).astype(np.uint8)

    # Apply the same GaussianBlur that HarmonyIndex.render() applies
    img = Image.fromarray(img_arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=hi.edge_blur))
    return np.array(img)


def _render_arr(hi: HarmonyIndex, state: dict) -> np.ndarray:
    """Return the vectorised render as a uint8 numpy array (H×W×3)."""
    return np.array(hi.render(harmonyState=state))


# ---------------------------------------------------------------------------
# Parametrised state grid
# ---------------------------------------------------------------------------

_LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]
_STATE_GRID = [
    {"r": r, "g": g, "b": b}
    for r, g, b in itertools.product(_LEVELS, _LEVELS, _LEVELS)
    if not (r == 0.0 and g == 0.0 and b == 0.0)   # all-zero is degenerate
]

# Focused cases used for property tests
_NAMED_STATES = [
    ("balanced",       {"r": 1.0, "g": 1.0, "b": 1.0}),
    ("red_dominant",   {"r": 1.0, "g": 0.0, "b": 0.0}),
    ("green_dominant", {"r": 0.0, "g": 1.0, "b": 0.0}),
    ("blue_dominant",  {"r": 0.0, "g": 0.0, "b": 1.0}),
    ("rg_equal",       {"r": 1.0, "g": 1.0, "b": 0.0}),
    ("rb_equal",       {"r": 1.0, "g": 0.0, "b": 1.0}),
    ("gb_equal",       {"r": 0.0, "g": 1.0, "b": 1.0}),
    ("mid_all",        {"r": 0.5, "g": 0.5, "b": 0.5}),
]


# ---------------------------------------------------------------------------
# 1. Vectorised output matches reference pixel-loop (core regression guard)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", _STATE_GRID)
def test_vectorised_matches_reference(state):
    """
    The vectorised render() must agree with the pixel-loop reference within
    ATOL for every pixel, for every combination in the slider grid.
    """
    hi  = HarmonyIndex(size=SIZE)
    vec = _render_arr(hi, state)
    ref = _reference_render(hi, state)

    diff = np.abs(vec.astype(int) - ref.astype(int))
    max_diff = int(diff.max())
    assert max_diff <= ATOL, (
        f"state={state}  max_diff={max_diff} > atol={ATOL}; "
        f"first worst pixel at "
        f"{np.unravel_index(diff.max(axis=-1).argmax(), diff[:, :, 0].shape)}"
    )


# ---------------------------------------------------------------------------
# 2. Triangle is actually painted (non-black pixels exist inside the mask)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,state", _NAMED_STATES)
def test_triangle_painted(label, state):
    hi  = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, state)
    interior = arr.any(axis=-1)
    n_painted = int(interior.sum())
    assert n_painted > (SIZE * SIZE * 0.25), (
        f"[{label}] Only {n_painted} interior pixels painted, expected > 25 % of canvas."
    )


# ---------------------------------------------------------------------------
# 3. Exterior corners are black (nothing rendered outside the triangle)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,state", _NAMED_STATES)
def test_exterior_is_black(label, state):
    hi  = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, state)
    # Image corners are well outside the equilateral triangle
    corners = [arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]]
    for c in corners:
        assert c.max() == 0, (
            f"[{label}] Corner pixel should be black but got {c}"
        )


# ---------------------------------------------------------------------------
# 4. Dominant hue matches the active channel near each midpoint
# ---------------------------------------------------------------------------

def _mean_patch(arr: np.ndarray, frac_x: float, frac_y: float,
                radius_frac: float = 0.05) -> np.ndarray:
    """Mean RGB of a small patch around a fractional image coordinate."""
    r = max(1, int(SIZE * radius_frac))
    cy = int(frac_y * (SIZE - 1))
    cx = int(frac_x * (SIZE - 1))
    patch = arr[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1]
    return patch.reshape(-1, 3).mean(axis=0)


@pytest.mark.parametrize("label,state,expected_ch", [
    # Red midpoint is on the left edge
    ("red_dominant",   {"r": 1.0, "g": 0.0, "b": 0.0}, 0),
    # Green midpoint is on the right edge
    ("green_dominant", {"r": 0.0, "g": 1.0, "b": 0.0}, 1),
    # Blue midpoint is on the bottom edge
    ("blue_dominant",  {"r": 0.0, "g": 0.0, "b": 1.0}, 2),
])
def test_dominant_hue_near_midpoint(label, state, expected_ch):
    """
    When only one channel is active, the midpoint of its corresponding edge
    should be brighter in that channel than in either of the other two.
    """
    hi = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, state)

    vertices = hi._define_triangle()
    midpoints = hi._calculate_midpoints(vertices)
    # convert from [-1, 1] math space to [0, 1] image fractions
    mx_frac = (midpoints[expected_ch][0] + 1) / 2
    my_frac = 1.0 - (midpoints[expected_ch][1] + 1) / 2   # y-axis flipped in image

    pixel = _mean_patch(arr, mx_frac, my_frac)
    dominant = int(pixel.argmax())
    assert dominant == expected_ch, (
        f"[{label}] Expected channel {expected_ch} dominant near midpoint, "
        f"got channel {dominant}. Patch mean ≈ {pixel}"
    )


# ---------------------------------------------------------------------------
# 5. Balanced state brightness symmetry
#    (the triangle is colour-asymmetric by design: left=red, right=green)
#    We verify that luminance is left-right symmetric instead.
# ---------------------------------------------------------------------------

def test_balanced_state_brightness_symmetry():
    """
    With equal weights (r=g=b=1) the per-pixel brightness (R+G+B sum) of the
    left half should mirror the right half exactly.  The triangle is
    geometrically symmetric: swapping left/right swaps the R and G channels
    (their midpoints are mirror images), so the channel sum is preserved.
    Individual RGB values are intentionally asymmetric (left=red, right=green),
    but total brightness must be symmetric.
    """
    hi  = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, {"r": 1.0, "g": 1.0, "b": 1.0}).astype(float)
    brightness = arr.sum(axis=-1)          # R+G+B per pixel
    left  = brightness[:, :SIZE // 2]
    right = brightness[:, SIZE // 2:][:, ::-1]   # mirror right half
    diff  = float(np.abs(left - right).mean())
    assert diff < 1.0, (
        f"Balanced render brightness is asymmetric; mean L/R diff = {diff:.4f}"
    )


# ---------------------------------------------------------------------------
# 6. Output shape and dtype sanity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,state", _NAMED_STATES)
def test_output_shape_and_dtype(label, state):
    hi  = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, state)
    assert arr.shape == (SIZE, SIZE, 3), f"[{label}] Unexpected shape {arr.shape}"
    assert arr.dtype == np.uint8,        f"[{label}] Unexpected dtype {arr.dtype}"
    assert arr.min() >= 0 and arr.max() <= 255, \
        f"[{label}] Values out of [0, 255]"


# ---------------------------------------------------------------------------
# 7. Inverse-square falloff still renders correctly (smoke test)
# ---------------------------------------------------------------------------

def test_inverse_square_falloff_renders():
    hi  = HarmonyIndex(size=SIZE)
    arr = np.array(hi.render(harmonyState={"r": 1.0, "g": 1.0, "b": 1.0},
                             falloff_type="inverse_square"))
    assert arr.shape == (SIZE, SIZE, 3)
    assert arr.any(), "inverse_square falloff produced all-black image"


# ---------------------------------------------------------------------------
# 8. Custom calibrated white-point does not break the render
# ---------------------------------------------------------------------------

def test_custom_calibration_renders():
    hi = HarmonyIndex(size=SIZE)
    hi.set_calibration({"r": 0.8, "g": 0.6, "b": 1.0})
    arr = _render_arr(hi, {"r": 0.8, "g": 0.6, "b": 1.0})
    assert arr.shape == (SIZE, SIZE, 3)
    assert arr.any(), "Custom calibration produced all-black image"


# ---------------------------------------------------------------------------
# 9. Edge slider positions — sliders at 0 or 1 extremes never crash
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", [
    {"r": 0.0, "g": 0.0, "b": 1.0},
    {"r": 0.0, "g": 1.0, "b": 0.0},
    {"r": 1.0, "g": 0.0, "b": 0.0},
    {"r": 1.0, "g": 1.0, "b": 1.0},
    {"r": 0.0, "g": 0.0, "b": 0.25},   # very low weights
    {"r": 1.0, "g": 0.25, "b": 0.5},
])
def test_extreme_slider_positions_do_not_crash(state):
    hi  = HarmonyIndex(size=SIZE)
    arr = _render_arr(hi, state)
    assert arr.shape == (SIZE, SIZE, 3)
    assert not np.isnan(arr).any(), f"NaN values in output for state={state}"


# ---------------------------------------------------------------------------
# 10. _quantise — cache-key quantisation helper
#
#  The sliders step at 0.01; we quantise r/g/b at 0.05 so that 5 consecutive
#  slider ticks collapse onto a single cache key.  The tests below confirm:
#    (a) values within the same 0.05 bucket → identical quantised key
#    (b) values in adjacent buckets         → distinct quantised keys
#    (c) bucket edges (0.00, 0.05, …, 1.00) → exact multiples of 0.05
#    (d) renders produced from the same quantised key are byte-identical
# ---------------------------------------------------------------------------

class TestQuantise:
    """Unit tests for _quantise(value, step)."""

    STEP = 0.05   # the step used for r/g/b in app.py

    # (a) — within-bucket collapse
    #
    # With step=0.05 each bucket covers a ±0.025 range around its centre.
    # Slider values at 0.01 increments that fall within a bucket:
    #   bucket 0.50  → [0.475, 0.525)  → slider ticks: 0.48 0.49 0.50 0.51 0.52
    #   bucket 0.55  → [0.525, 0.575)  → slider ticks: 0.53 0.54 0.55 0.56 0.57
    #   bucket 0.60  → [0.575, 0.625)  → slider ticks: 0.58 0.59 0.60 0.61 0.62
    @pytest.mark.parametrize("raw,expected", [
        # bucket 0.50: values within ±0.02 of 0.50
        (0.50, 0.50), (0.51, 0.50), (0.52, 0.50),
        (0.49, 0.50), (0.48, 0.50),
        # bucket 0.55: 0.53, 0.54 are >0.025 away from 0.50 → land in 0.55
        (0.53, 0.55), (0.54, 0.55), (0.55, 0.55), (0.56, 0.55), (0.57, 0.55),
        # bucket 0.60: 0.58 and 0.59 are >0.025 away from 0.55
        (0.58, 0.60), (0.59, 0.60),
        # exact multiples and endpoints
        (0.00, 0.00), (1.00, 1.00),
    ])
    def test_within_bucket_collapse(self, raw, expected):
        result = _quantise(raw, self.STEP)
        assert abs(result - expected) < 1e-9, (
            f"_quantise({raw}, {self.STEP}) = {result}, expected {expected}"
        )

    # (b) — adjacent buckets produce distinct keys
    @pytest.mark.parametrize("a, b", [
        (0.50, 0.55),
        (0.00, 0.05),
        (0.95, 1.00),
        (0.20, 0.25),
    ])
    def test_adjacent_buckets_are_distinct(self, a, b):
        qa = _quantise(a, self.STEP)
        qb = _quantise(b, self.STEP)
        assert abs(qa - qb) > 1e-9, (
            f"_quantise({a}) == _quantise({b}) == {qa}; expected distinct keys"
        )

    # (c) — exact multiples pass through unchanged
    @pytest.mark.parametrize("exact", [v / 20 for v in range(21)])  # 0.00 … 1.00
    def test_exact_multiples_are_identity(self, exact):
        result = _quantise(exact, self.STEP)
        assert abs(result - exact) < 1e-9, (
            f"_quantise({exact}, {self.STEP}) = {result}; expected {exact}"
        )


class TestQuantisedRendersMatchCacheKey:
    """
    Confirm that two slider values that quantise to the same bucket produce
    byte-identical renders (i.e. would always hit the same cache entry), while
    values in different buckets produce distinct renders.
    """

    STEP = 0.05
    RENDER_SIZE = 100   # small for speed

    def _render_bytes(self, r: float, g: float, b: float) -> bytes:
        """Render via HarmonyIndex using quantised r/g/b, return PNG bytes."""
        import io as _io
        qr = _quantise(r, self.STEP)
        qg = _quantise(g, self.STEP)
        qb = _quantise(b, self.STEP)
        hi = HarmonyIndex(size=self.RENDER_SIZE)
        img = hi.render(harmonyState={"r": qr, "g": qg, "b": qb})
        buf = _io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # (d) — same bucket → identical bytes
    #
    # Only values within ±0.025 of a bucket centre collapse to the same key.
    # Slider step=0.01, so a bucket at 0.50 captures ticks 0.48–0.52 (5 ticks).
    @pytest.mark.parametrize("r1,r2,g,b", [
        # bucket 0.50: all of 0.48, 0.49, 0.50, 0.51, 0.52 → 0.50
        (0.50, 0.51, 0.75, 0.25),
        (0.50, 0.52, 0.75, 0.25),
        (0.50, 0.49, 0.75, 0.25),
        (0.50, 0.48, 0.75, 0.25),
        # bucket 0.20: 0.18–0.22 → 0.20
        (0.20, 0.21, 0.50, 0.50),
        (0.20, 0.22, 0.50, 0.50),
    ])
    def test_same_bucket_produces_identical_render(self, r1, r2, g, b):
        bytes1 = self._render_bytes(r1, g, b)
        bytes2 = self._render_bytes(r2, g, b)
        assert bytes1 == bytes2, (
            f"r={r1} and r={r2} should quantise to the same bucket "
            f"({_quantise(r1, self.STEP)}) but produced different renders"
        )

    # (e) — different buckets → different bytes
    @pytest.mark.parametrize("r1,r2,g,b", [
        (0.50, 0.55, 0.75, 0.25),
        (0.20, 0.25, 0.50, 0.50),
        (0.00, 0.05, 1.00, 0.50),
    ])
    def test_different_buckets_produce_distinct_renders(self, r1, r2, g, b):
        bytes1 = self._render_bytes(r1, g, b)
        bytes2 = self._render_bytes(r2, g, b)
        assert bytes1 != bytes2, (
            f"r={r1} (bucket {_quantise(r1, self.STEP)}) and "
            f"r={r2} (bucket {_quantise(r2, self.STEP)}) "
            f"produced identical renders; buckets should be visually distinct"
        )
