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
Reviewer round 3, Step 2: a controlled hierarchy testing candidate
mechanisms for PI's persistent shortfall (simulated 1.42 vs. target 2.15;
see waveform_diagnostics.py -- the core issue is TAMX ~1.67x too high, i.e.
velocity stays too high through too much of the cycle, not PS or ED
specifically). Each factor swept ONE AT A TIME from the current best
(literature-sourced, non-Doppler-fitted) baseline, per the reviewer's
explicit sequence:
  1. DA inertance scale (0 to 2x theoretical)
  2. PA/Ao compliances (joint and independent)
  3. Pulmonary/systemic resistance baseline (preserving the independently-
     sourced flow SPLIT -- shunt fraction/RV:LV ratio unchanged, only the
     absolute P0_BASELINE anchor varies)
  4. Systolic duration / ejection-waveform sharpness
  5. Different RV/LV waveform shapes or relative timing (not identical
     scaled waveforms)

Physics note (reviewer round 3): inertance cannot sustain a persistent MEAN
pressure difference over a period (<L*dQ/dt>=0) -- it can only reshape the
waveform and, through the nonlinear R_da loss's dependence on that shape,
affect the cycle-mean pressure loss indirectly. So inertance is evaluated
here purely for its effect on PI/waveform shape, not framed as a gradient
mechanism.
"""
import csv
import numpy as np

from da_rlc_coupled_model import (
    simulate_coupled, compute_indices_0d, T_PERIOD,
    R_PULM, R_SYS, C_PA, C_AO, Q_RV_MEAN, Q_LV_MEAN, DA_SHUNT_FRACTION,
    P0_BASELINE_MMHG, MMHG,
)
from waveform_diagnostics import characterize_waveform

TARGET = dict(PS=41.32, ED=13.05, SD=3.85, PI=2.15)
N_CYCLES = 8


def score(idx):
    return sum(abs(idx[k] - TARGET[k]) / TARGET[k] for k in TARGET)


def run_point(label, steps_per_cycle=4000, **kwargs):
    # low L_da_scale shrinks the DA's L/R time constant, making the ODE
    # numerically stiffer -- scale up resolution accordingly to avoid the
    # RK4 instability seen at l_da_scale<0.1 with the default resolution.
    l_scale = kwargs.get("l_da_scale", 1.0)
    if l_scale < 0.5:
        steps_per_cycle = max(steps_per_cycle, min(int(4000 / max(l_scale, 0.01)), 40000))
    res = simulate_coupled(n_cycles=N_CYCLES, steps_per_cycle=steps_per_cycle, **kwargs)
    idx = compute_indices_0d(res)
    shape = characterize_waveform(res)
    s = score(idx)
    return dict(label=label, PS=idx["PS"], ED=idx["ED"], SD=idx["SD"], PI=idx["PI"],
                TAMX=shape["TAMX"], frac_above_half=shape["frac_cycle_above_half_PS"],
                score=s)


def resistances_at_baseline(p0_mmhg):
    """Re-derive R_pulm/R_sys at a different shared baseline pressure,
    preserving the independently-sourced flow split (shunt fraction,
    RV:LV ratio) -- reviewer's factor 3."""
    q_da_est = DA_SHUNT_FRACTION * Q_RV_MEAN
    q_pulm_est = Q_RV_MEAN - q_da_est
    q_sys_est = Q_LV_MEAN + q_da_est
    r_pulm = (p0_mmhg * MMHG) / q_pulm_est
    r_sys = (p0_mmhg * MMHG) / q_sys_est
    return r_pulm, r_sys


if __name__ == "__main__":
    rows = []

    # baseline
    rows.append(run_point("baseline"))

    # --- 1. DA inertance scale ---
    for l_scale in (0.1, 0.25, 0.5, 1.0, 1.5, 2.0):
        rows.append(run_point(f"L_da_scale={l_scale}", l_da_scale=l_scale))

    # --- 2. compliances: joint scale, then independent ---
    for c_scale in (0.1, 0.5, 1.0, 2.0, 5.0, 10.0):
        rows.append(run_point(f"C_joint_scale={c_scale}", c_pa=C_PA * c_scale, c_ao=C_AO * c_scale))
    for c_pa_scale in (0.1, 0.5, 2.0, 10.0):
        rows.append(run_point(f"C_pa_scale={c_pa_scale}_only", c_pa=C_PA * c_pa_scale, c_ao=C_AO))
    for c_ao_scale in (0.1, 0.5, 2.0, 10.0):
        rows.append(run_point(f"C_ao_scale={c_ao_scale}_only", c_pa=C_PA, c_ao=C_AO * c_ao_scale))

    # --- 3. resistance baseline (preserving flow split) ---
    for p0 in (15.0, 20.0, 25.0, 30.0, 40.0, 50.0):
        r_pulm, r_sys = resistances_at_baseline(p0)
        rows.append(run_point(f"P0_baseline={p0}mmHg", r_pulm=r_pulm, r_sys=r_sys))

    # --- 4. systolic duration / ejection sharpness (both ventricles together) ---
    for sf in (0.20, 0.25, 0.30, 0.35, 0.45):
        rows.append(run_point(f"systolic_frac={sf}", systolic_frac_rv=sf, systolic_frac_lv=sf))
    for p in (1.0, 2.0, 4.0, 8.0):
        rows.append(run_point(f"ejection_power={p}", ejection_power_rv=p, ejection_power_lv=p))

    # --- 5. RV/LV timing/shape differences ---
    for offset in (0.0, 0.05, 0.10, 0.15, 0.20):
        rows.append(run_point(f"rv_lv_phase_offset={offset}", rv_lv_phase_offset=offset))
    # RV shorter/sharper than LV (physiologically plausible asymmetry, untested before)
    rows.append(run_point("RV_shorter_sharper", systolic_frac_rv=0.25, ejection_power_rv=4.0,
                           systolic_frac_lv=0.35, ejection_power_lv=2.0))
    rows.append(run_point("RV_longer_flatter", systolic_frac_rv=0.45, ejection_power_rv=1.0,
                           systolic_frac_lv=0.35, ejection_power_lv=2.0))

    with open("pi_factorial_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "PS", "ED", "SD", "PI", "TAMX", "frac_above_half", "score"])
        for r in rows:
            writer.writerow([r["label"], r["PS"], r["ED"], r["SD"], r["PI"],
                              r["TAMX"], r["frac_above_half"], r["score"]])
            print(f"{r['label']:35s} PS={r['PS']:6.1f} ED={r['ED']:6.1f} SD={r['SD']:5.2f} "
                  f"PI={r['PI']:5.2f} TAMX={r['TAMX']:6.1f} frac>half={r['frac_above_half']:.1%} "
                  f"score={r['score']:.2f}", flush=True)

    print(f"\ntarget: PS=41.32 ED=13.05 SD=3.85 PI=2.15 (TAMX_target~14.5-15)")
    print("Done -- see pi_factorial_results.csv")
