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
Lumped-parameter (0D) two-compartment pulmonary/systemic circulation model,
built to address a reviewer-flagged weakness in the 1D DA model
(model_plan_and_literature_data.md Section 8/reviewer round 1): the previous
version PRESCRIBED the DA inlet flow directly, so its simulated PA-Ao pressure
difference (0.09mmHg) had no real connection to the ~5mmHg literature value --
"a prescribed-flow inlet plus one reflection coefficient cannot independently
represent pulmonary and systemic circulations" (reviewer's words).

This module does NOT modify baker_1d_solver.py (kept unchanged -- it
underpins the already-published CoA paper/repo). Instead, it wraps it: two
lumped compartments (PA, fed by RV ejection; Ao/systemic, fed by LV ejection,
each draining to its own vascular bed) are coupled through an orifice/
Bernoulli-type DA connection and solved to a periodic steady state. The
resulting Q_DA(t) waveform -- now a genuine CONSEQUENCE of the PA-Ao pressure
difference, not an assumed shape -- is then used as the 1D tube's prescribed
inlet flow (the 1D tube itself still resolves the detailed wave propagation
along the DA's own length/compliance, which the 0D layer does not capture).

Governing equations (compartment pressures P_pa, P_ao, dyn/cm^2):
    C_pa * dP_pa/dt = Q_RV(t) - Q_DA(P_pa,P_ao) - P_pa/R_pulm
    C_ao * dP_ao/dt = Q_LV(t) + Q_DA(P_pa,P_ao) - P_ao/R_sys
    Q_DA(P_pa,P_ao) = K_DA * sign(P_pa-P_ao) * sqrt(|P_pa-P_ao|)   (orifice/
        Bernoulli form -- consistent with the review draft's own emphasis on
        Bernoulli's equation at the DA constriction, and standard in lumped
        cardiac-shunt models, e.g. Setchi et al. 2013's DA connection, though
        parameter VALUES there are for the postnatal, not fetal, scenario)

See model_plan_and_literature_data.md Section 9 for every parameter's source/
confidence level (well-sourced / extrapolated from later gestation / assumed
plausible range) -- most fetal circulation literature is mid-to-late
gestation, not this cohort's ~13.5 weeks, so several values here are
explicitly flagged as extrapolations or bounded assumptions, not precise
citations.
"""
import numpy as np

MMHG = 1333.22  # dyn/cm^2 per mmHg

# --- fetal heart rate, shared with the 1D DA model ---
HR_BPM = 150.0
T_PERIOD = 60.0 / HR_BPM
SYSTOLIC_FRAC = 0.35  # ventricular ejection fraction of the cycle

# === parameters -- see plan doc Section 9 for sourcing/confidence ===
# Combined fetal cardiac output (CCO): Vimpeli et al. (2009), Ultrasound
# Obstet Gynecol 33:265-271 (n=143, directly measured, 11-20 weeks GA):
# CCO=9mL/min at 11wk, 121mL/min at 20wk. No single 13.5wk value reported --
# log-interpolated between these two WELL-SOURCED anchor points (EXTRAPOLATED,
# not itself a direct measurement at this GA).
import numpy as _np
_ga_anchors = _np.array([11.0, 20.0])
_cco_anchors_ml_min = _np.array([9.0, 121.0])
COMBINED_CO_ML_MIN = float(_np.exp(_np.interp(13.5, _ga_anchors, _np.log(_cco_anchors_ml_min))))

# RV:LV output ratio: SAME literature family, WELL-SOURCED and close to this
# GA: 1.34+-0.28 at 15wk, declining to 1.08+-0.28 at 40wk -- use ~1.32 at 13.5wk.
RV_LV_RATIO = 1.32
RV_FRACTION = RV_LV_RATIO / (1 + RV_LV_RATIO)

Q_RV_MEAN = COMBINED_CO_ML_MIN * RV_FRACTION / 60.0        # cm^3/s
Q_LV_MEAN = COMBINED_CO_ML_MIN * (1 - RV_FRACTION) / 60.0  # cm^3/s

# Vascular resistances: PVR >> SVR, and the MAJORITY of RV output bypasses the
# lungs via the DA rather than perfusing them, is QUALITATIVELY well-
# established fetal physiology (only ~10-15% of RV output perfuses the fetal
# lungs near term) -- but that specific split is sourced from NEAR-TERM
# physiology, not verified at 13.5 weeks specifically (EXTRAPOLATED). No
# absolute fetal PA/Ao pressure at 13.5wk was found in the literature search
# (a gap already flagged in Section 4/pda_model.py) -- P_PA_MEAN_MMHG/
# P_AO_MEAN_MMHG below are ASSUMED (chosen only so the mean gradient matches
# Rudolph 1979's ~5mmHg), and R_pulm/R_sys are back-calculated from those
# assumed pressures plus the assumed ~85% DA-shunt fraction, NOT independently
# sourced magnitudes.
P_PA_MEAN_MMHG = 32.5   # ASSUMED (see plan doc Section 4 gap)
P_AO_MEAN_MMHG = 27.5   # ASSUMED, s.t. mean gradient = 5.0mmHg (Rudolph 1979)
DA_SHUNT_FRACTION = 0.85  # ASSUMED (near-term physiology, extrapolated to 13.5wk)

_Q_DA_MEAN_EST = DA_SHUNT_FRACTION * Q_RV_MEAN
_Q_PULM_MEAN_EST = Q_RV_MEAN - _Q_DA_MEAN_EST
_Q_SYS_MEAN_EST = Q_LV_MEAN + _Q_DA_MEAN_EST

R_PULM = (P_PA_MEAN_MMHG * MMHG) / _Q_PULM_MEAN_EST  # dyn.s/cm^5, back-calculated
R_SYS = (P_AO_MEAN_MMHG * MMHG) / _Q_SYS_MEAN_EST    # dyn.s/cm^5, back-calculated

# Compartment compliances: NOT independently sourced for the fetal PA/Ao at
# this GA -- placeholder magnitudes chosen only to give a plausible RC time
# constant (a few x T_PERIOD), flagged as assumed, see plan doc Section 9.
C_PA = 1.0e-6  # cm^5/dyn
C_AO = 1.0e-6  # cm^5/dyn

# DA orifice coefficient: free/calibrated (this project's actual unknown of
# interest), NOT independently sourced. Initial estimate from
# Q_DA_mean ~= K_DA*sqrt(mean(P_pa-P_ao)) -- refined in
# calibrate_two_compartment.py against the mean-gradient and shunt-fraction
# targets simultaneously (this mean-based estimate ignores the pulsatile
# nonlinearity of the sqrt() relation, so is a starting point, not final).
K_DA = _Q_DA_MEAN_EST / _np.sqrt((P_PA_MEAN_MMHG - P_AO_MEAN_MMHG) * MMHG)


def derive_parameters(combined_co_ml_min=COMBINED_CO_ML_MIN, rv_lv_ratio=RV_LV_RATIO,
                       shunt_fraction=DA_SHUNT_FRACTION, p_pa_mean_mmhg=P_PA_MEAN_MMHG,
                       p_ao_mean_mmhg=P_AO_MEAN_MMHG):
    """Re-derive (q_rv_mean, q_lv_mean, r_pulm, r_sys, k_da) consistently from
    the high-level, literature-adjacent inputs -- used by sensitivity_analysis.py
    and uncertainty_propagation.py to vary ONE high-level assumption at a time
    while keeping everything downstream of it self-consistent (rather than
    varying R_pulm/R_sys/K_DA directly, which would be varying already-derived
    quantities in a way disconnected from the actual physiological assumption)."""
    rv_fraction = rv_lv_ratio / (1 + rv_lv_ratio)
    q_rv_mean = combined_co_ml_min * rv_fraction / 60.0
    q_lv_mean = combined_co_ml_min * (1 - rv_fraction) / 60.0
    q_da_mean_est = shunt_fraction * q_rv_mean
    q_pulm_mean_est = q_rv_mean - q_da_mean_est
    q_sys_mean_est = q_lv_mean + q_da_mean_est
    r_pulm = (p_pa_mean_mmhg * MMHG) / q_pulm_mean_est
    r_sys = (p_ao_mean_mmhg * MMHG) / q_sys_mean_est
    dp = (p_pa_mean_mmhg - p_ao_mean_mmhg) * MMHG
    k_da = q_da_mean_est / np.sqrt(dp) if dp > 0 else 0.0
    return dict(q_rv_mean=q_rv_mean, q_lv_mean=q_lv_mean, r_pulm=r_pulm, r_sys=r_sys, k_da=k_da,
                p_pa_mean_mmhg=p_pa_mean_mmhg, p_ao_mean_mmhg=p_ao_mean_mmhg)


def _ventricular_ejection_shape(phase, ts, p=2.0):
    return np.where(phase < ts, np.sin(np.pi * phase / ts) ** p, 0.0)


_ejection_mean = _ventricular_ejection_shape(np.linspace(0, 1, 4000, endpoint=False), SYSTOLIC_FRAC).mean()


def make_ventricular_flow(q_mean):
    def q(t):
        phase = (t % T_PERIOD) / T_PERIOD
        return q_mean * _ventricular_ejection_shape(phase, SYSTOLIC_FRAC) / _ejection_mean
    return q


def q_da(p_pa, p_ao, k_da):
    dp = p_pa - p_ao
    return k_da * np.sign(dp) * np.sqrt(np.abs(dp))


def simulate_two_compartment(
    q_rv_mean=Q_RV_MEAN, q_lv_mean=Q_LV_MEAN,
    r_pulm=R_PULM, r_sys=R_SYS, c_pa=C_PA, c_ao=C_AO, k_da=K_DA,
    p_pa_init_mmhg=P_PA_MEAN_MMHG, p_ao_init_mmhg=P_AO_MEAN_MMHG,
    n_cycles=15, steps_per_cycle=2000,
):
    """RK4 integration of the coupled 0D system to a periodic steady state.
    Returns t, P_pa, P_ao, Q_DA arrays (last full cycle is the periodic
    result if n_cycles is enough for convergence -- check by comparing the
    last two cycles' Q_DA before trusting the output)."""
    q_rv = make_ventricular_flow(q_rv_mean)
    q_lv = make_ventricular_flow(q_lv_mean)
    dt = T_PERIOD / steps_per_cycle
    n_steps = n_cycles * steps_per_cycle

    def deriv(t, state):
        p_pa, p_ao = state
        qda = q_da(p_pa, p_ao, k_da)
        dp_pa = (q_rv(t) - qda - p_pa / r_pulm) / c_pa
        dp_ao = (q_lv(t) + qda - p_ao / r_sys) / c_ao
        return np.array([dp_pa, dp_ao])

    state = np.array([p_pa_init_mmhg * MMHG, p_ao_init_mmhg * MMHG])
    t_arr = np.zeros(n_steps + 1)
    p_pa_arr = np.zeros(n_steps + 1)
    p_ao_arr = np.zeros(n_steps + 1)
    p_pa_arr[0], p_ao_arr[0] = state

    t = 0.0
    for i in range(n_steps):
        k1 = deriv(t, state)
        k2 = deriv(t + dt / 2, state + dt / 2 * k1)
        k3 = deriv(t + dt / 2, state + dt / 2 * k2)
        k4 = deriv(t + dt, state + dt * k3)
        state = state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        t_arr[i + 1] = t
        p_pa_arr[i + 1], p_ao_arr[i + 1] = state

    qda_arr = q_da(p_pa_arr, p_ao_arr, k_da)
    return dict(t=t_arr, P_pa=p_pa_arr, P_ao=p_ao_arr, Q_DA=qda_arr,
                P_pa_mmHg=p_pa_arr / MMHG, P_ao_mmHg=p_ao_arr / MMHG)


if __name__ == "__main__":
    res = simulate_two_compartment()
    t = res["t"]
    mask_last = t > t[-1] - T_PERIOD
    mask_prev = (t > t[-1] - 2 * T_PERIOD) & (t <= t[-1] - T_PERIOD)
    qda_last = res["Q_DA"][mask_last]
    qda_prev = res["Q_DA"][mask_prev]
    print(f"P_pa mean (last cycle): {res['P_pa_mmHg'][mask_last].mean():.2f} mmHg")
    print(f"P_ao mean (last cycle): {res['P_ao_mmHg'][mask_last].mean():.2f} mmHg")
    print(f"mean pressure gradient (Pa-Ao): {(res['P_pa_mmHg'][mask_last]-res['P_ao_mmHg'][mask_last]).mean():.2f} mmHg")
    print(f"Q_DA range (last cycle): {qda_last.min():.4f} .. {qda_last.max():.4f} cm^3/s")
    print(f"convergence check (last vs prev cycle Q_DA max): "
          f"{qda_last.max():.4f} vs {qda_prev.max():.4f}")
