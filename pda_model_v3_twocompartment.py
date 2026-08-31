# =============================================================================
# Citation notice
#
# This code accompanies the manuscript:
#   J. Tang, S. Zhang, S. Ran, H. Ho. "A Coupled Reduced-Order Model of
#   First-Trimester Fetal Ductus Arteriosus Flow." Manuscript in preparation
#   / under review as of the time this repository was published -- please
#   check for the final published citation (journal, year, volume, DOI) and
#   cite that version if available; otherwise cite this repository directly.
#
# If you use, adapt, or build on this code, please cite the paper above.
# =============================================================================

"""
v3: DA flow driven by the two-compartment (pulmonary/systemic) lumped model
(two_compartment_model.py), NOT a hand-shaped/prescribed waveform -- the
reviewer's top-priority fix (model_plan_and_literature_data.md Section 8/9).
Q_DA(t) from the 0D layer is interpolated and fed as the 1D DA tube's
prescribed inlet flow (baker_1d_solver.py itself is still unchanged). Outlet
kappa is set near 0 (matched/non-reflecting) since the descending-aorta/
systemic downstream impedance is now represented explicitly by the 0D layer's
R_sys, not by a local reflection coefficient -- avoids double-counting the
systemic impedance.
"""
import numpy as np
from scipy.interpolate import interp1d

from da_geometry import da_geometry_cm
from two_compartment_model import simulate_two_compartment, T_PERIOD as T_PERIOD_0D

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "coarctation_aorta", "coa_1d_model"))
from baker_1d_solver import build_geometry_general, simulate

RHO = 1.05
MU = 0.035
NU = MU / RHO
K1, K2, K3 = 2.00e7, -22.53, 8.65e5
MMHG = 1333.22

GA_WEEKS = 13.5
L, R_PA, R_AO = da_geometry_cm(GA_WEEKS)
M = 100
HR_BPM = 150.0
T_PERIOD = 60.0 / HR_BPM
assert abs(T_PERIOD - T_PERIOD_0D) < 1e-9, "0D and 1D models must share the same heart rate/period"

P0_MMHG = 30.0
P0 = P0_MMHG * MMHG
DELTA = 0.1


def r0_func(x):
    frac = np.clip(x / L, 0.0, 1.0)
    return R_PA + (R_AO - R_PA) * frac


def make_f_func(k1, k2, k3, stiffness_scale):
    def f_func(x, r0):
        Eh_r0 = stiffness_scale * (k1 * np.exp(k2 * r0) + k3)
        return (4.0 / 3.0) * Eh_r0
    return f_func


def build_inlet_from_two_compartment(k_da, stiffness_scale_unused=None, **tc_kwargs):
    """Run the 0D model, build a periodic interpolant of its Q_DA(t) for use
    as the 1D tube's inlet flow. Returns (inlet_flow_func, tc_result)."""
    tc = simulate_two_compartment(k_da=k_da, **tc_kwargs)
    t = tc["t"]
    mask = t > t[-1] - T_PERIOD
    t_cycle = t[mask] - t[mask][0]
    q_cycle = tc["Q_DA"][mask]
    # ensure periodic wraparound for interp1d
    t_cycle = np.append(t_cycle, T_PERIOD)
    q_cycle = np.append(q_cycle, q_cycle[0])
    f = interp1d(t_cycle, q_cycle, kind="linear")

    def inlet_flow(t_query):
        return f(t_query % T_PERIOD)
    return inlet_flow, tc


def run(k_da, stiffness_scale, kappa=0.0, N=60000, CFL=0.9, verbose=False, **tc_kwargs):
    inlet_flow, tc = build_inlet_from_two_compartment(k_da, **tc_kwargs)
    geom = build_geometry_general(L, M, r0_func, make_f_func(K1, K2, K3, stiffness_scale), K1, K2, K3)
    res = simulate(geom, RHO, NU, DELTA, P0, inlet_flow, kappa, N, CFL=CFL, verbose=verbose)
    return geom, res, tc


def compute_indices(geom, res, node="pa", n_cycles=3):
    x = geom["x"]
    idx = int(np.argmin(np.abs(x - 0.0))) if node == "pa" else int(np.argmin(np.abs(x - L)))
    t = res["t"]
    n_whole_cycles = int(t[-1] / T_PERIOD)
    n_use = min(n_cycles, max(n_whole_cycles, 1))
    t_start = t[-1] - n_use * T_PERIOD
    mask = t >= t_start
    u = res["u"][idx, mask]
    ps = u.max()
    tt = t[mask]
    phase = ((tt - t_start) % T_PERIOD) / T_PERIOD
    diastolic_mask = phase > 0.85
    ed = u[diastolic_mask].mean() if diastolic_mask.any() else u.min()
    sd = ps / ed if ed != 0 else np.nan
    ri = (ps - ed) / ps if ps != 0 else np.nan
    pi = (ps - ed) / u.mean()
    return dict(PS=ps, ED=ed, SD=sd, PI=pi, RI=ri, u_mean=u.mean())


if __name__ == "__main__":
    from two_compartment_model import K_DA as K_DA_DEFAULT

    print(f"GA={GA_WEEKS}wk: L={L*10:.2f}mm, r_pa={R_PA*10:.3f}mm, r_ao={R_AO*10:.3f}mm")
    print(f"K_DA (0D orifice coeff, from literature-informed back-calc) = {K_DA_DEFAULT:.6e}")

    STIFFNESS_SCALE = 0.01  # start from the v2-calibrated value
    N = 150000
    geom, res, tc = run(K_DA_DEFAULT, STIFFNESS_SCALE, kappa=0.0, N=N, verbose=True)
    print("\nany NaN:", np.isnan(res["A"]).any())
    print(f"cycles: {res['t'][-1]/T_PERIOD:.1f}")

    idx_ao = compute_indices(geom, res, "ao")
    idx_pa = compute_indices(geom, res, "pa")
    print("\nPA end:", {k: round(float(v), 2) for k, v in idx_pa.items()})
    print("Ao end:", {k: round(float(v), 2) for k, v in idx_ao.items()})
    print("target: PS=41.32 ED=13.05 SD=3.85 PI=2.15")

    t = res["t"]
    p = res["p_mmHg"]
    mask3 = t > (t[-1] - 3 * T_PERIOD)
    p_pa_mean = p[0, mask3].mean()
    p_ao_mean = p[-1, mask3].mean()
    print(f"\n1D-tube-implied mean pressure: PA end={p_pa_mean:.2f}mmHg, Ao end={p_ao_mean:.2f}mmHg, "
          f"drop={p_pa_mean-p_ao_mean:.2f}mmHg")

    t0 = tc["t"]
    mask0 = t0 > t0[-1] - T_PERIOD
    print(f"0D-layer mean pressure: P_pa={tc['P_pa_mmHg'][mask0].mean():.2f}mmHg, "
          f"P_ao={tc['P_ao_mmHg'][mask0].mean():.2f}mmHg, "
          f"gradient={(tc['P_pa_mmHg'][mask0]-tc['P_ao_mmHg'][mask0]).mean():.2f}mmHg (lit ~5mmHg)")
