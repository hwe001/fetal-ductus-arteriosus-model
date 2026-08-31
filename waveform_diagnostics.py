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
Reviewer round 3, Step 3: diagnostic waveform-shape characterization,
sharper than raw PS/ED/S-D/PI. Given PS=41.6, ED=10.5 (post ED-definition
fix): target PI=2.15 implies TAMX=(PS-ED)/PI=14.47 cm/s; simulated PI=1.42
implies TAMX=(PS-ED)/PI=21.86 cm/s. The problem is not PS or ED individually
-- it's that simulated velocity stays too high through too much of the
cycle. This script quantifies exactly how.
"""
import numpy as np
from da_rlc_coupled_model import simulate_coupled, compute_indices_0d, T_PERIOD


def characterize_waveform(res, n_cycles=3):
    t = res["t"]
    n_whole = int(t[-1] / T_PERIOD)
    n_use = min(n_cycles, max(n_whole, 1))
    t_start = t[-1] - n_use * T_PERIOD
    mask = t >= t_start
    u = res["u_da"][mask]
    tt = t[mask]
    # use the LAST full cycle specifically for shape metrics
    cyc_mask = tt >= t[-1] - T_PERIOD
    u_c = u[cyc_mask]
    t_c = tt[cyc_mask] - (t[-1] - T_PERIOD)
    phase_c = t_c / T_PERIOD

    ps = u_c.max()
    ed = u_c[-1]
    tamx = u_c.mean()
    i_peak = np.argmax(u_c)
    time_to_peak_frac = phase_c[i_peak]

    above_half = phase_c[u_c > 0.5 * ps]
    frac_above_half = len(above_half) / len(phase_c)

    # systolic "width": duration (as fraction of cycle) that u > 0.5*PS,
    # measured as a contiguous span around the peak
    above_mask = u_c > 0.5 * ps
    # find contiguous run containing the peak
    idx = i_peak
    lo = idx
    while lo > 0 and above_mask[lo - 1]:
        lo -= 1
    hi = idx
    while hi < len(above_mask) - 1 and above_mask[hi + 1]:
        hi += 1
    systolic_width_frac = (hi - lo) / len(phase_c)

    return dict(PS=ps, ED=ed, TAMX=tamx, time_to_peak_frac=time_to_peak_frac,
                frac_cycle_above_half_PS=frac_above_half,
                systolic_width_frac=systolic_width_frac)


if __name__ == "__main__":
    res = simulate_coupled(n_cycles=8, steps_per_cycle=4000)
    idx = compute_indices_0d(res)
    shape = characterize_waveform(res)

    target_PS, target_ED, target_PI = 41.32, 13.05, 2.15
    target_TAMX = (target_PS - target_ED) / target_PI

    print("=== simulated (current default: Leao geometry, Cd=0.7) ===")
    for k, v in shape.items():
        print(f"  {k}: {v:.4f}")
    print(f"  PI (from indices): {idx['PI']:.3f}")

    print(f"\n=== target-implied ===")
    print(f"  TAMX implied by target PI: {target_TAMX:.2f} cm/s")
    print(f"  simulated TAMX: {shape['TAMX']:.2f} cm/s")
    print(f"  ratio (simulated/target): {shape['TAMX']/target_TAMX:.2f}x too high")

    print(f"\n=== diagnosis ===")
    print(f"  simulated spends {shape['frac_cycle_above_half_PS']:.1%} of the cycle above 50% of PS")
    print(f"  simulated time-to-peak: {shape['time_to_peak_frac']:.1%} of cycle")
    print(f"  simulated systolic width (contiguous >50%PS span): {shape['systolic_width_frac']:.1%} of cycle")
    print(f"  (ventricular ejection window SYSTOLIC_FRAC=0.35 for comparison)")
