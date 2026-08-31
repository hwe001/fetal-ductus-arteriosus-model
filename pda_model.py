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
Fetal ductus arteriosus (DA) hemodynamic model at end-of-first-trimester
gestation (~13.5 weeks GA), built on the ported Baker transmission-line/
MacCormack solver (baker_1d_solver.py, reused UNCHANGED from the CoA project).

This completes the stub study design in
`../blood flow simulation for the DA.docx` ("Quantifying the blood flow and
shear stress for the ductus arteriosus", Tang/Zhang/Ran/Ho): 24 first-trimester
fetuses, CHCWC, transmission-line method. See model_plan_and_literature_data.md
for full derivation of every parameter below.

Physiology (NOT the postnatal PDA-of-prematurity scenario -- see that doc's
Section 1): normal fetal circulation, continuous PA-to-Ao (right-to-left)
forward flow through the DA, driven by a ~5mmHg PA-over-Ao pressure excess
(Rudolph 1979) from elevated fetal pulmonary vascular resistance.

NOTE (reviewer feedback): this module/folder is named "pda_*" for historical
reasons only. The eventual paper's title/aims/discussion must make explicit
this is a FETAL ductus arteriosus flow study, not patent ductus arteriosus
(PDA) -- see model_plan_and_literature_data.md's top-of-file naming note.
"""
import numpy as np
from da_geometry import da_geometry_cm

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "coarctation_aorta", "coa_1d_model"))
from baker_1d_solver import build_geometry_general, simulate

# --- blood properties: carried over from the CoA project (no DA- or first-
# trimester-fetal-specific value found in the literature search -- see plan
# doc Section 4).
RHO = 1.05      # g/cm^3
MU = 0.035      # poise
NU = MU / RHO   # cm^2/s

# --- Olufsen systemic-artery stiffness constants (Baker's/Olufsen 1999's
# original large-artery values) as the base law; STIFFNESS_SCALE is a free,
# calibrated multiplier -- NOT assumed to transfer directly, since the DA
# wall is actively muscular (not a passive elastic systemic artery).
K1, K2, K3 = 2.00e7, -22.53, 8.65e5
STIFFNESS_SCALE = 0.01  # CALIBRATED (see calibrate_pda.py + plan doc Section 7).
# Unscaled adult systemic-artery stiffness applied to a ~0.07cm-radius vessel gives an
# implausible wave speed ~1800cm/s and an impractically small CFL timestep -- same
# finding as the CoA project's need for a stiffness rescale, only more extreme here
# given the DA's much smaller caliber.

MMHG = 1333.22  # dyn/cm^2 per mmHg

# --- geometry: Szpinda (2007) regression at GA=13.5 weeks (end of first
# trimester, matching the cohort), cross-checked against the cmgui
# reconstruction (see plan doc Section 2.2).
GA_WEEKS = 13.5
L, R_PA, R_AO = da_geometry_cm(GA_WEEKS)
M = 100


def r0_func(x):
    """Linear taper: r_pa at the inlet (x=0, PA end) to r_ao at the true
    outlet (x=L, aortic-junction end) -- see da_geometry.da_geometry_cm."""
    frac = np.clip(x / L, 0.0, 1.0)
    return R_PA + (R_AO - R_PA) * frac


# --- inlet: pulsatile PA-side flow. Fetal HR ~150bpm at 14 weeks
# (Montenegro et al. 1998) for this end-of-first-trimester cohort.
HR_BPM = 150.0
T_PERIOD = 60.0 / HR_BPM
SYSTOLIC_FRAC = 0.30  # narrow systolic window (fraction of cycle) for a sharp spike

# --- waveform shape v2: a sustained diastolic BASELINE with a short, sharp
# systolic spike added on top -- replacing the v1 quarter-sine+exponential-
# decay shape borrowed from the CoA/adult-aortic project, which structurally
# couples "how high systole goes" to "how deep diastole decays" and so could
# not simultaneously match this cohort's PS/ED and S/D/PI targets (see plan
# doc Section 6). Real fetal DA flow is continuous, PA-to-Ao, driven by a
# pressure excess that persists through diastole (Rudolph 1979) -- confirmed
# in the real clinical Doppler waveform in ../images/ (redacted patient ID),
# which shows sharp systolic peaks over a much less-decayed diastolic shelf.
# BASE_FRAC = fraction of the cycle mean flow that is the flat diastolic
# floor; the remaining (1-BASE_FRAC) is carried by the systolic spike. This
# decouples the diastolic floor from the systolic peak amplitude, which the
# old single-parameter (Q_PULSE_FRAC) shape could not do.
SPIKE_POWER = 2.0  # systolic spike sharpness (higher = narrower/peakier)

# --- CALIBRATED (see calibrate_pda.py + finetune_base_frac.py, and plan doc
# Section 7): joint sweep over Q_MEAN (bisected against PS), BASE_FRAC, KAPPA,
# STIFFNESS_SCALE against all 4 cohort targets. Best-scoring point found:
Q_MEAN = 0.232031  # cm^3/s
BASE_FRAC = 0.65


def _spike_shape(phase, ts, p):
    return np.where(phase < ts, np.sin(np.pi * phase / ts) ** p, 0.0)


_spike_mean = _spike_shape(np.linspace(0, 1, 4000, endpoint=False), SYSTOLIC_FRAC, SPIKE_POWER).mean()


def make_inlet_flow(q_mean, base_frac, spike_power=SPIKE_POWER):
    q_base = base_frac * q_mean
    q_spike = (q_mean - q_base) / _spike_mean if _spike_mean > 0 else 0.0

    def inlet_flow(t):
        phase = (t % T_PERIOD) / T_PERIOD
        return q_base + q_spike * _spike_shape(phase, SYSTOLIC_FRAC, spike_power)
    return inlet_flow


# --- baseline pressure: NOT independently sourced for GA=13.5wk specifically
# (see plan doc Section 4 gap) -- a representative low fetal arterial pressure,
# flagged as an assumption, not a citation.
P0_MMHG = 30.0
P0 = P0_MMHG * MMHG

DELTA = 0.1   # cm, boundary-layer thickness -- Baker's original assumption, unchanged
KAPPA = -0.3  # CALIBRATED, see above


def make_f_func(k1, k2, k3, stiffness_scale):
    def f_func(x, r0):
        Eh_r0 = stiffness_scale * (k1 * np.exp(k2 * r0) + k3)
        return (4.0 / 3.0) * Eh_r0
    return f_func


def run(q_mean=Q_MEAN, base_frac=BASE_FRAC, kappa=KAPPA,
        stiffness_scale=STIFFNESS_SCALE, spike_power=SPIKE_POWER, N=40000, CFL=0.9, verbose=False):
    geom = build_geometry_general(L, M, r0_func, make_f_func(K1, K2, K3, stiffness_scale), K1, K2, K3)
    inlet_flow = make_inlet_flow(q_mean, base_frac, spike_power)
    res = simulate(geom, RHO, NU, DELTA, P0, inlet_flow, kappa, N, CFL=CFL, verbose=verbose)
    return geom, res


def compute_indices(geom, res, node="pa", n_cycles=3):
    """PS, ED, S/D, PI, RI from the last n_cycles simulated cardiac cycles at
    the given end of the vessel ('pa' = inlet/PA end, 'ao' = outlet/aortic-
    junction end), matching the standard clinical obstetric-Doppler formulas
    (verified against a real machine readout -- see
    model_plan_and_literature_data.md Section 8 -- GA=24w0d exemplar:
    PS=-59.06, ED=-9.99, TAmax=-21.53 cm/s gives S/D=PS/ED=5.91,
    RI=(PS-ED)/PS=0.83, PI=(PS-ED)/TAmax=2.28, all matching the machine's own
    displayed values to 2 decimal places):
        S/D = PS/ED
        RI  = (PS-ED)/PS
        PI  = (PS-ED)/TAMX   -- TAMX = time-averaged MAXIMUM velocity, i.e.
                                 the time-average of the velocity envelope,
                                 NOT an intensity-weighted time-averaged mean.
    Our 1D model outputs a single bulk (cross-sectional-mean) velocity per
    timestep, not a full spectral velocity distribution, so mean(u(t)) over
    whole cycles is the model's best available proxy for TAMX (there being no
    separate "envelope" trace to average in a bulk 1D solve) -- this is the
    correct formula STRUCTURE, but see Section 8's discussion of a separate,
    more consequential unresolved issue: clinical PS/ED are near-centerline
    (profile-peak) velocities, while this model's u=q/A is a cross-sectional
    MEAN velocity, related by a (possibly phase-dependent) profile-shape
    correction factor this model does not currently apply.

    The window is aligned to an exact whole number of cycles ending at the
    last simulated timestep (not just "t > t[-1] - n_cycles*T_PERIOD", which
    could clip a partial cycle and bias the TAMX/PI estimate)."""
    x = geom["x"]
    idx = int(np.argmin(np.abs(x - 0.0))) if node == "pa" else int(np.argmin(np.abs(x - L)))
    t = res["t"]
    n_whole_cycles = int(t[-1] / T_PERIOD)
    n_use = min(n_cycles, max(n_whole_cycles, 1))
    t_start = t[-1] - n_use * T_PERIOD
    mask = t >= t_start
    u = res["u"][idx, mask]
    ps = u.max()
    # end-diastolic: value at the end of each cycle (just before next systolic upstroke)
    tt = t[mask]
    phase = ((tt - t_start) % T_PERIOD) / T_PERIOD
    diastolic_mask = phase > 0.85  # late-diastolic window
    ed = u[diastolic_mask].mean() if diastolic_mask.any() else u.min()
    sd = ps / ed if ed != 0 else np.nan
    ri = (ps - ed) / ps if ps != 0 else np.nan
    pi = (ps - ed) / u.mean()
    return dict(PS=ps, ED=ed, SD=sd, PI=pi, RI=ri, u_mean=u.mean())


if __name__ == "__main__":
    print(f"GA={GA_WEEKS}wk: L={L*10:.2f}mm, r_pa={R_PA*10:.3f}mm, r_ao={R_AO*10:.3f}mm")
    print(f"HR={HR_BPM}bpm, T_period={T_PERIOD:.3f}s")

    N = 150000
    geom, res = run(N=N, verbose=True)
    print("\nany NaN in A:", np.isnan(res["A"]).any(), " any NaN in q:", np.isnan(res["q"]).any())
    print(f"total simulated time: {res['t'][-1]:.3f}s => {res['t'][-1]/T_PERIOD:.1f} cycles")

    idx_pa = compute_indices(geom, res, "pa")
    idx_ao = compute_indices(geom, res, "ao")
    print("\nPA end (inlet):", {k: round(v, 2) for k, v in idx_pa.items()})
    print("Ao end (outlet):", {k: round(v, 2) for k, v in idx_ao.items()})
    print("\ntarget (anonymized cohort): PS=41.32 ED=13.05 SD=3.85 PI=2.15")
