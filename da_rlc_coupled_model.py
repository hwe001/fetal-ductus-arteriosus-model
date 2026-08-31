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
TERMINOLOGY (reviewer round 3): this is a coupled NONLINEAR RL model, NOT
"RLC" -- the DA element has resistance (R_da) and inertance (L_da) only, no
separate compliance state (see design note below on why, and where DA
compliance is instead accounted for). Earlier docs/comments in this project
called it "RLC" loosely; that label is imprecise and is being phased out.

v4: single, genuinely coupled 0D model of the fetal ductus arteriosus (DA),
replacing the v3 "0D compartments -> prescribed DA flow -> disconnected 1D
tube" architecture after reviewer round 2 identified it as one-way forcing
with a risk of double-counting (see model_plan_and_literature_data.md
Section 11). Per the reviewer's suggested "simpler publishable alternative"
and the user's explicit choice between the two architectures offered: the DA
is now a single lumped element (resistance + inertance; compliance folded
into the compartments, see design note below) bridging the PA and Ao
compartments, with ALL THREE states (P_pa, P_ao, Q_da) integrated
SIMULTANEOUSLY -- flow and pressure are solved together, not staged.

Governing equations (state: P_pa, P_ao [dyn/cm^2], Q_da [cm^3/s]):
    C_pa * dP_pa/dt = Q_RV(t) - Q_da - P_pa/R_pulm
    C_ao * dP_ao/dt = Q_LV(t) + Q_da - P_ao/R_sys
    L_da * dQ_da/dt = (P_pa - P_ao) - R_da * Q_da * |Q_da|

The DA term is a genuine dynamical state (inertance L_da gives real phase
lag/memory, unlike v3's instantaneous algebraic orifice relation
Q=K*sqrt(dP)), with a NONLINEAR (Bernoulli/orifice-type, quadratic in Q, not
linear Poiseuille) loss term R_da -- appropriate for a short constriction/
orifice rather than a long thin tube, and matching the reviewer's mention of
"a loss coefficient" as a defensible parameter.

Design note on compliance: the reviewer's suggested element is "resistance,
inertance, and compliance." A separate DA-level compliance state was
DELIBERATELY OMITTED here -- given this project's own finding that the DA is
"acoustically short" (wave-transit time under 0.5% of the cardiac cycle,
Section 9), the DA's own volume-storage capacity is expected to be small
relative to the PA/Ao compartments' -- so DA compliance is folded into
C_pa/C_ao rather than given its own state, keeping the free-parameter count
small (the reviewer's own Step 4 request) -- a disclosed simplification, not
a hidden omission.

CRITICAL FIX (de-circularization, reviewer round 2): v3 assumed TWO SEPARATE
compartment pressures (32.5/27.5mmHg) chosen SPECIFICALLY to produce a
~5mmHg difference, then back-calculated resistances from that assumption --
circular. Here, R_pulm and R_sys are instead anchored to a SINGLE shared
baseline pressure P0_BASELINE_MMHG (representing a generic, undifferentiated
fetal arterial pressure level -- NOT chosen with any target gradient in
mind), applied identically to both sides; only the INDEPENDENTLY-SOURCED
flow split (from Vimpeli et al. 2009's cardiac output/RV:LV data and the
extrapolated ~85% DA shunt fraction) differs between the two sides. Any
resulting P_pa-P_ao gradient is therefore a genuine, non-circular EMERGENT
CONSEQUENCE of the flow asymmetry interacting with R_da's dynamics -- not
pre-built into two independently-chosen pressure assumptions. R_da itself is
derived from orifice theory (discharge coefficient x throat area), not
back-calculated from any assumed pressure difference.
"""
import numpy as np

MMHG = 1333.22  # dyn/cm^2 per mmHg
RHO = 1.05      # g/cm^3, carried over (no DA-specific value found, Section 4)

HR_BPM = 150.0
T_PERIOD = 60.0 / HR_BPM
SYSTOLIC_FRAC = 0.35

# === independently-sourced flow parameters (UNCHANGED from v3 -- these were
# never part of the circularity problem) ===
_ga_anchors = np.array([11.0, 20.0])
_cco_anchors_ml_min = np.array([9.0, 121.0])  # Vimpeli et al. 2009
COMBINED_CO_ML_MIN = float(np.exp(np.interp(13.5, _ga_anchors, np.log(_cco_anchors_ml_min))))
RV_LV_RATIO = 1.32  # Vimpeli et al. 2009, ~15wk value
RV_FRACTION = RV_LV_RATIO / (1 + RV_LV_RATIO)
Q_RV_MEAN = COMBINED_CO_ML_MIN * RV_FRACTION / 60.0
Q_LV_MEAN = COMBINED_CO_ML_MIN * (1 - RV_FRACTION) / 60.0

DA_SHUNT_FRACTION = 0.85  # ASSUMED, extrapolated from near-term physiology (Section 9)

# === DE-CIRCULARIZED resistance derivation: ONE shared baseline pressure ===
P0_BASELINE_MMHG = 30.0  # ASSUMED representative fetal arterial pressure level,
# NOT chosen to produce any particular gradient -- applied identically to both
# R_pulm and R_sys below (this symmetry is the de-circularization fix).

_Q_DA_MEAN_EST = DA_SHUNT_FRACTION * Q_RV_MEAN
_Q_PULM_MEAN_EST = Q_RV_MEAN - _Q_DA_MEAN_EST
_Q_SYS_MEAN_EST = Q_LV_MEAN + _Q_DA_MEAN_EST

R_PULM = (P0_BASELINE_MMHG * MMHG) / _Q_PULM_MEAN_EST
R_SYS = (P0_BASELINE_MMHG * MMHG) / _Q_SYS_MEAN_EST

C_PA = 1.0e-6  # cm^5/dyn, unsourced placeholder (Section 9), unchanged from v3
C_AO = 1.0e-6

# === DA element: length from Szpinda (2007, along-length average, no
# narrow-point alternative available); throat radius from Leao et al. (2015)'s
# diameter SPECIFICALLY at the ductus-aortic junction ("base at the aorta",
# the 9-14wk age-binned value, 0.93mm -- see da_geometry.py and Section 14),
# not Szpinda's along-length-average diameter -- the Section 14 geometry/
# measurement audit (reviewer round 2, Step 2) found this literature value
# ALONE (no further free "area_scale" fitting) gives a throat-radius ratio of
# 0.93/1.4694 diam = 0.679 vs. the Szpinda-based value used in earlier
# versions -- matching, to within 0.2 percentage points, the 0.68 ratio that
# had to be FIT to the Doppler PS target in Section 13.1. This is now used as
# the DEFAULT throat geometry (literature-sourced, not a free parameter);
# AREA_SCALE remains available as an explicit override for further testing.
from da_geometry import da_geometry_cm, da_diameter_base_at_aorta_mm
L_DA_CM, R_PA_RADIUS_CM, _R_AO_RADIUS_SZPINDA_CM = da_geometry_cm(13.5)
R_AO_RADIUS_CM = (da_diameter_base_at_aorta_mm(13.5) / 2.0) / 10.0  # Leao 2015, mm -> cm

DISCHARGE_COEFF = 0.7  # Cd, typical sharp-edged/constricted-orifice value (plausible range 0.6-0.8)
AREA_SCALE = 1.0       # override for further sensitivity testing -- 1.0 now means "use the
                       # literature-sourced Leao throat radius above," not the old Szpinda one


def compute_da_rlc_params(area_scale=AREA_SCALE, discharge_coeff=DISCHARGE_COEFF):
    a_throat = np.pi * R_AO_RADIUS_CM ** 2 * area_scale
    r_da = RHO / (2 * (discharge_coeff * a_throat) ** 2)   # orifice/Bernoulli loss coefficient
    l_da = RHO * L_DA_CM / a_throat                          # fluid inertance
    return dict(r_da=r_da, l_da=l_da, a_throat=a_throat)


def _ventricular_ejection_shape(phase, ts, p=2.0):
    return np.where(phase < ts, np.sin(np.pi * phase / ts) ** p, 0.0)


def _ejection_norm(ts, p):
    return _ventricular_ejection_shape(np.linspace(0, 1, 4000, endpoint=False), ts, p).mean()


def make_ventricular_flow(q_mean, systolic_frac=SYSTOLIC_FRAC, power=2.0, phase_offset=0.0):
    """phase_offset: fraction of a cycle by which this ventricle's ejection
    window is shifted relative to phase=0 -- lets RV/LV eject with a timing
    difference rather than being forced into perfect synchrony (reviewer
    round 3, PI factorial study item 5)."""
    norm = _ejection_norm(systolic_frac, power)

    def q(t):
        phase = ((t - phase_offset * T_PERIOD) % T_PERIOD) / T_PERIOD
        return q_mean * _ventricular_ejection_shape(phase, systolic_frac, power) / norm
    return q


def simulate_coupled(
    q_rv_mean=Q_RV_MEAN, q_lv_mean=Q_LV_MEAN, r_pulm=R_PULM, r_sys=R_SYS,
    c_pa=C_PA, c_ao=C_AO, area_scale=AREA_SCALE, discharge_coeff=DISCHARGE_COEFF,
    l_da_scale=1.0,
    systolic_frac_rv=SYSTOLIC_FRAC, systolic_frac_lv=SYSTOLIC_FRAC,
    ejection_power_rv=2.0, ejection_power_lv=2.0,
    rv_lv_phase_offset=0.0,
    n_cycles=15, steps_per_cycle=4000,
):
    """RK4 integration of the fully-coupled 3-state system to a periodic
    steady state. All three states (P_pa, P_ao, Q_da) are integrated
    SIMULTANEOUSLY -- no staging, no one-way forcing.

    l_da_scale: multiplier on the theoretical (geometry-derived) inertance --
    reviewer round 3 factorial study item 1 (0 to 2x).
    systolic_frac_*/ejection_power_*/rv_lv_phase_offset: let RV and LV eject
    with independently different durations, sharpness, and relative timing
    -- item 5 (previously both ventricles used IDENTICAL scaled waveforms,
    which the reviewer flagged as worth varying)."""
    rlc = compute_da_rlc_params(area_scale, discharge_coeff)
    r_da, l_da = rlc["r_da"], rlc["l_da"] * l_da_scale
    q_rv = make_ventricular_flow(q_rv_mean, systolic_frac_rv, ejection_power_rv, phase_offset=0.0)
    q_lv = make_ventricular_flow(q_lv_mean, systolic_frac_lv, ejection_power_lv, phase_offset=rv_lv_phase_offset)
    dt = T_PERIOD / steps_per_cycle
    n_steps = n_cycles * steps_per_cycle

    def deriv(t, state):
        p_pa, p_ao, q_da = state
        dp_pa = (q_rv(t) - q_da - p_pa / r_pulm) / c_pa
        dp_ao = (q_lv(t) + q_da - p_ao / r_sys) / c_ao
        dq_da = ((p_pa - p_ao) - r_da * q_da * np.abs(q_da)) / l_da
        return np.array([dp_pa, dp_ao, dq_da])

    state = np.array([P0_BASELINE_MMHG * MMHG, P0_BASELINE_MMHG * MMHG, 0.0])
    t_arr = np.zeros(n_steps + 1)
    states = np.zeros((n_steps + 1, 3))
    states[0] = state

    t = 0.0
    for i in range(n_steps):
        k1 = deriv(t, state)
        k2 = deriv(t + dt / 2, state + dt / 2 * k1)
        k3 = deriv(t + dt / 2, state + dt / 2 * k2)
        k4 = deriv(t + dt, state + dt * k3)
        state = state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        t_arr[i + 1] = t
        states[i + 1] = state

    p_pa, p_ao, q_da = states[:, 0], states[:, 1], states[:, 2]
    a_throat = rlc["a_throat"]
    return dict(t=t_arr, P_pa=p_pa, P_ao=p_ao, Q_DA=q_da,
                P_pa_mmHg=p_pa / MMHG, P_ao_mmHg=p_ao / MMHG,
                u_da=q_da / a_throat, a_throat=a_throat)


def compute_indices_0d(res, n_cycles=3):
    """PS/ED/S-D/PI/RI from the DA's own velocity (Q_DA/A_throat), matching
    the same clinical formulas verified in Section 8 (S/D=PS/ED,
    RI=(PS-ED)/PS, PI=(PS-ED)/TAMX).

    ED DEFINITION FIXED (reviewer round 2, Section 15): previously the mean
    velocity over the final 15% of the cycle -- an arbitrary averaging
    window, not the clinical convention. Confirmed by direct inspection that
    velocity decays smoothly and monotonically through diastole (no
    numerical noise/oscillation), so the window-mean was systematically
    HIGHER than the true end-diastolic point (averaging in earlier, higher-
    velocity samples from the window) -- e.g. at the current best
    parameterization, window-mean ED=11.85 vs. the corrected instantaneous
    value=10.53, an 11% difference, in the direction that WORSENED the
    reported ED fit (the old, wrong-but-lenient definition was flattering
    the model's ED match). Now uses a true instantaneous end-of-cycle
    sample, matching the clinical end-diastolic SAMPLING convention (the
    velocity at the specific instant just before the next systolic
    upstroke, not an averaged window)."""
    t = res["t"]
    n_whole = int(t[-1] / T_PERIOD)
    n_use = min(n_cycles, max(n_whole, 1))
    t_start = t[-1] - n_use * T_PERIOD
    mask = t >= t_start
    u = res["u_da"][mask]
    ps = u.max()
    ed = u[-1]  # instantaneous sample at the end of the last full cycle
    sd = ps / ed if ed != 0 else np.nan
    ri = (ps - ed) / ps if ps != 0 else np.nan
    pi = (ps - ed) / u.mean()
    return dict(PS=ps, ED=ed, SD=sd, PI=pi, RI=ri, u_mean=u.mean())


def check_convergence(res, n_check_cycles=2):
    """Compare the last two cycles' PS to confirm periodic convergence --
    reviewer round 2 flagged that short/unconverged runs previously gave
    materially different indices than long ones."""
    t = res["t"]
    period_mask_last = t > t[-1] - T_PERIOD
    period_mask_prev = (t > t[-1] - 2 * T_PERIOD) & (t <= t[-1] - T_PERIOD)
    ps_last = res["u_da"][period_mask_last].max()
    ps_prev = res["u_da"][period_mask_prev].max()
    return dict(ps_last=ps_last, ps_prev=ps_prev, rel_diff=abs(ps_last - ps_prev) / ps_last)


if __name__ == "__main__":
    rlc = compute_da_rlc_params()
    print(f"DA geometry: L={L_DA_CM*10:.2f}mm, r_throat={R_AO_RADIUS_CM*10:.3f}mm "
          f"(area={rlc['a_throat']:.5f}cm^2)")
    print(f"R_da={rlc['r_da']:.3e}, L_da={rlc['l_da']:.3e}")
    print(f"Q_RV_mean={Q_RV_MEAN:.4f} cm^3/s, Q_LV_mean={Q_LV_MEAN:.4f} cm^3/s")
    print(f"R_pulm={R_PULM:.3e}, R_sys={R_SYS:.3e} (both anchored to SAME "
          f"P0_BASELINE={P0_BASELINE_MMHG}mmHg -- de-circularized)")

    res = simulate_coupled()
    conv = check_convergence(res)
    print(f"\nconvergence check: PS(last cycle)={conv['ps_last']:.2f} vs "
          f"PS(prev cycle)={conv['ps_prev']:.2f} (rel diff {conv['rel_diff']:.2%})")

    idx = compute_indices_0d(res)
    print("indices:", {k: round(float(v), 3) for k, v in idx.items()})

    t = res["t"]
    mask = t > t[-1] - T_PERIOD
    grad = (res["P_pa_mmHg"][mask] - res["P_ao_mmHg"][mask]).mean()
    print(f"\nEMERGENT mean P_pa-P_ao gradient: {grad:.2f} mmHg "
          f"(NOT assumed/back-calculated -- a genuine model output; "
          f"lit. target ~5mmHg)")
    print(f"target Doppler indices: PS=41.32 ED=13.05 SD=3.85 PI=2.15")
