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
Reviewer round 3, Step 3 (uncertainty analysis) -- Monte Carlo propagation
of genuine parameter uncertainty through the CORRECTED, de-circularized
coupled-RL model (da_rlc_coupled_model.py + the Leao-throat-diameter
geometry fix, Section 13.3prime). This SUPERSEDES the old Section 10.3
Monte Carlo, which ran on the now-withdrawn circular two-compartment
architecture (v3) and is no longer valid.

Sampled distributions (see model_plan_and_literature_data.md Sections 4, 9,
13.3prime for each parameter's source/confidence level):
  - combined_co_ml_min: Vimpeli et al. (2009) log-interpolation to 13.5wk
    has no explicit CI reported -- using a +-25% engineering-judgment range
    for the extrapolation uncertainty (NOT a reported statistic).
  - rv_lv_ratio: Normal(1.32, 0.28) -- THIS is Vimpeli et al.'s own reported
    SD, a real statistic, not an assumed range.
  - leao_diameter_mm: Normal(0.93, SEM=0.174) -- Leao et al. (2015)'s
    reported mean=0.93, SD=0.55 for the 9-14wk bin (n=10) is the BETWEEN-
    SPECIMEN variability, not the uncertainty in the estimated population
    mean. This model represents one "representative" fetus at this GA (not
    per-patient variation, out of scope throughout this project) -- so the
    correct quantity to propagate is the standard error of the mean,
    SEM=SD/sqrt(n)=0.55/sqrt(10)=0.174mm, not the raw SD. An earlier version
    of this script used the raw SD directly, producing physically
    implausible tail samples (diameter down to a floored 0.2mm) that drove
    numerically extreme, non-physical outputs (PS into the hundreds) --
    caught and corrected before reporting any results from that run.
  - discharge_coeff: Uniform(0.6, 0.8) -- standard sharp-edged/constricted-
    orifice engineering range, not derived from this project's own data.
  - shunt_fraction: Uniform(0.75, 0.90) -- bounds from the qualitative
    "~10-15% of RV output perfuses the fetal lungs" near-term physiology,
    extrapolated to 13.5wk (Section 9).
  - p0_baseline_mmhg: Uniform(20, 40) -- UNSOURCED (no fetal MAP value found
    at this GA, Section 4's flagged gap); a plausible engineering-judgment
    range, not a citation.
  - c_pa_scale, c_ao_scale (independent): Uniform(0.5, 2.0) each -- the
    factorial study (Section 17) showed compliance has large, destabilizing
    effects at extreme (0.1x/10x) values; this range avoids those extremes
    while still capturing meaningful, genuine uncertainty in these
    completely unsourced placeholder parameters.

NOT varied (deliberately, with reason): DA inertance (L_da) -- the
factorial study found it has essentially no effect on any of the four
indices (Section 17.2), so propagating its uncertainty would not
meaningfully widen the output bands; RV/LV phase offset -- this is an
untested MODELLING hypothesis (Section 17.2's most consequential finding),
not a parameter with a known distribution to sample from, so it is held at
its default (zero, i.e. synchronized) rather than treated as a nuisance
parameter here.
"""
import csv
import numpy as np

from two_compartment_model import derive_parameters as _unused  # not used; kept for reference only
from da_rlc_coupled_model import simulate_coupled, compute_indices_0d, T_PERIOD, R_AO_RADIUS_CM
from da_rlc_coupled_model import Q_RV_MEAN as _BASE_Q_RV, Q_LV_MEAN as _BASE_Q_LV

N_SAMPLES = 150
SEED = 11
LEAO_MEAN_DIAM_MM = 0.93

RANGES = dict(
    co_frac=(0.75, 1.25),          # multiplicative factor on combined CO
    discharge_coeff=(0.6, 0.8),
    shunt_fraction=(0.75, 0.90),
    p0_baseline_mmhg=(20.0, 40.0),
    c_pa_scale=(0.5, 2.0),
    c_ao_scale=(0.5, 2.0),
)


LEAO_SEM_DIAM_MM = 0.55 / (10 ** 0.5)     # SEM = SD/sqrt(n), n=10
RV_LV_SEM = 0.28 / (143 ** 0.5)             # SEM = SD/sqrt(n), Vimpeli et al. n=143

# Reviewer round 4 correction: EPISTEMIC uncertainty (uncertainty in the
# ESTIMATED POPULATION-MEAN parameter, appropriate when this model represents
# one "representative" fetus) uses the STANDARD ERROR OF THE MEAN for both
# diameter AND rv_lv_ratio -- the first version of this script inconsistently
# used the raw between-subject SD for rv_lv_ratio (0.28) while (after the
# earlier fix) using SEM for diameter. Both are literature-reported
# between-subject SDs (Leao n=10, Vimpeli n=143) -- fixed to use SEM
# consistently for both in the epistemic analysis below.
#
# BIOLOGICAL VARIABILITY (variation AMONG INDIVIDUAL FETUSES, appropriate if
# asking "how much would the prediction vary if built for a randomly-drawn
# individual fetus rather than the population-representative one") instead
# uses the raw reported SD for diameter, but via a LOG-NORMAL distribution
# (matched to the same mean/SD) rather than a Normal -- diameter is a
# strictly-positive physical quantity, and a Normal with SD=0.55 on a mean of
# 0.93 (CV=59%) allows physically-implausible near-zero/negative samples in
# its left tail, which is what drove the non-physical outliers in the FIRST
# (uncorrected) attempt at this analysis, not something inherent to using the
# full reported SD -- the fix is distribution SHAPE, not just shrinking the
# spread. See uncertainty_propagation_v4_biological.py for this analysis.


def sample_params(rng, mode="epistemic"):
    s = {k: rng.uniform(lo, hi) for k, (lo, hi) in RANGES.items()}
    if mode == "epistemic":
        s["rv_lv_ratio"] = max(rng.normal(1.32, RV_LV_SEM), 0.5)
        s["leao_diameter_mm"] = max(rng.normal(LEAO_MEAN_DIAM_MM, LEAO_SEM_DIAM_MM), 0.3)
    elif mode == "biological":
        s["rv_lv_ratio"] = max(rng.normal(1.32, 0.28), 0.5)  # raw between-subject SD
        # log-normal matched to mean=0.93, SD=0.55 (Leao's own reported stats)
        sigma2 = np.log(1 + (0.55 / LEAO_MEAN_DIAM_MM) ** 2)
        mu = np.log(LEAO_MEAN_DIAM_MM) - sigma2 / 2
        s["leao_diameter_mm"] = rng.lognormal(mu, np.sqrt(sigma2))
    else:
        raise ValueError(mode)
    return s


def eval_sample(s):
    rv_fraction = s["rv_lv_ratio"] / (1 + s["rv_lv_ratio"])
    # combined CO scaled by co_frac around the module's baseline combined CO,
    # recovered from the baseline Q_RV/Q_LV means (RV_LV_RATIO=1.32 baseline)
    base_combined = _BASE_Q_RV + _BASE_Q_LV
    combined = base_combined * s["co_frac"]
    q_rv_mean = combined * rv_fraction
    q_lv_mean = combined * (1 - rv_fraction)

    q_da_est = s["shunt_fraction"] * q_rv_mean
    q_pulm_est = q_rv_mean - q_da_est
    q_sys_est = q_lv_mean + q_da_est
    MMHG = 1333.22
    r_pulm = (s["p0_baseline_mmhg"] * MMHG) / q_pulm_est
    r_sys = (s["p0_baseline_mmhg"] * MMHG) / q_sys_est

    area_scale = (s["leao_diameter_mm"] / LEAO_MEAN_DIAM_MM) ** 2

    res = simulate_coupled(
        q_rv_mean=q_rv_mean, q_lv_mean=q_lv_mean, r_pulm=r_pulm, r_sys=r_sys,
        c_pa=1.0e-6 * s["c_pa_scale"], c_ao=1.0e-6 * s["c_ao_scale"],
        area_scale=area_scale, discharge_coeff=s["discharge_coeff"],
        n_cycles=8, steps_per_cycle=4000,
    )
    idx = compute_indices_0d(res)
    t = res["t"]
    mask = t > t[-1] - T_PERIOD
    grad = (res["P_pa_mmHg"][mask] - res["P_ao_mmHg"][mask]).mean()
    return dict(PS=idx["PS"], ED=idx["ED"], SD=idx["SD"], PI=idx["PI"], gradient=grad)


def run(mode, out_path, seed):
    rng = np.random.RandomState(seed)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_i"] + list(RANGES.keys()) + ["rv_lv_ratio", "leao_diameter_mm",
                                                                "PS", "ED", "SD", "PI", "gradient"])
        for i in range(N_SAMPLES):
            s = sample_params(rng, mode=mode)
            out = eval_sample(s)
            row = ([i] + [s[k] for k in RANGES.keys()] + [s["rv_lv_ratio"], s["leao_diameter_mm"]] +
                   [out["PS"], out["ED"], out["SD"], out["PI"], out["gradient"]])
            writer.writerow(row)
            f.flush()
            if (i + 1) % 25 == 0:
                print(f"[{mode} {i+1}/{N_SAMPLES}] PS={out['PS']:.1f} ED={out['ED']:.1f} "
                      f"SD={out['SD']:.2f} PI={out['PI']:.2f} grad={out['gradient']:.2f}", flush=True)
    print(f"\nDone ({mode}) -- see {out_path}")


if __name__ == "__main__":
    run("epistemic", "uncertainty_v4_epistemic_results.csv", seed=11)
    run("biological", "uncertainty_v4_biological_results.csv", seed=23)
