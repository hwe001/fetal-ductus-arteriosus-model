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
Step 5 (reviewer round 1): propagate uncertainty in the most consequential
ASSUMED/EXTRAPOLATED parameters (model_plan_and_literature_data.md Section 9)
through the two-compartment + 1D model, rather than presenting single point
values (e.g. STIFFNESS_SCALE=0.01) as if precisely known.

Plausible ranges (see plan doc Section 9 for each parameter's source/
confidence level):
  - combined_co_ml_min: baseline ~18.5, +-30% for the log-interpolation
    extrapolation to 13.5wk (Vimpeli et al. 2009's own anchor points are at
    11 and 20wk, not this GA).
  - rv_lv_ratio: baseline 1.32 +-0.28 -- THIS range is the literature's own
    reported uncertainty (Vimpeli et al. 2009), not an assumption.
  - shunt_fraction: 0.75-0.90 (near-term "~10-15% of RV output perfuses the
    lungs" bounds, extrapolated to 13.5wk).
  - pa_ao_gradient_mmhg: 3-7mmHg (Rudolph 1979's ~5mmHg is itself a
    representative, not precisely-bounded, value).
  - stiffness_scale: 0.005-0.02 (this project's own v2 grid-search bounds).

NOT propagated in this pass (scope limitation, disclosed): blood rho/mu and
the DA taper ratio (da_geometry.py's taper_ratio=1.15) are held at their
point-estimate values -- a further extension, not yet done.

N samples drawn independently (uniform) from each range; checkpointed to CSV.
"""
import csv
import os
import numpy as np

from two_compartment_model import derive_parameters
from pda_model_v3_twocompartment import run, compute_indices

CSV_PATH = "uncertainty_results.csv"
N_STEPS = 60000
N_SAMPLES = 40
SEED = 7

RANGES = dict(
    combined_co_ml_min=(18.5 * 0.7, 18.5 * 1.3),
    rv_lv_ratio=(1.32 - 0.28, 1.32 + 0.28),
    shunt_fraction=(0.75, 0.90),
    pa_ao_gradient_mmhg=(3.0, 7.0),
    stiffness_scale=(0.005, 0.02),
)


def sample_params(rng):
    s = {k: rng.uniform(lo, hi) for k, (lo, hi) in RANGES.items()}
    p_mid = 30.0  # keep the mean of P_pa/P_ao fixed, vary only the gradient
    s["p_pa_mean_mmhg"] = p_mid + s["pa_ao_gradient_mmhg"] / 2
    s["p_ao_mean_mmhg"] = p_mid - s["pa_ao_gradient_mmhg"] / 2
    return s


def eval_sample(s):
    params = derive_parameters(combined_co_ml_min=s["combined_co_ml_min"], rv_lv_ratio=s["rv_lv_ratio"],
                                shunt_fraction=s["shunt_fraction"], p_pa_mean_mmhg=s["p_pa_mean_mmhg"],
                                p_ao_mean_mmhg=s["p_ao_mean_mmhg"])
    geom, res, tc = run(params["k_da"], s["stiffness_scale"], kappa=0.0, N=N_STEPS,
                         q_rv_mean=params["q_rv_mean"], q_lv_mean=params["q_lv_mean"],
                         r_pulm=params["r_pulm"], r_sys=params["r_sys"],
                         p_pa_init_mmhg=s["p_pa_mean_mmhg"], p_ao_init_mmhg=s["p_ao_mean_mmhg"])
    idx = compute_indices(geom, res, "ao")
    t0 = tc["t"]
    mask0 = t0 > t0[-1] - (t0[-1] / 15)
    gradient = (tc["P_pa_mmHg"][mask0] - tc["P_ao_mmHg"][mask0]).mean()
    return dict(PS=idx["PS"], ED=idx["ED"], SD=idx["SD"], PI=idx["PI"], gradient=gradient)


if __name__ == "__main__":
    rng = np.random.RandomState(SEED)
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["sample_i"] + list(RANGES.keys()) + ["PS", "ED", "SD", "PI", "gradient"])
            f.flush()

        for i in range(N_SAMPLES):
            s = sample_params(rng)
            out = eval_sample(s)
            row = [i] + [s[k] for k in RANGES.keys()] + [out["PS"], out["ED"], out["SD"], out["PI"], out["gradient"]]
            writer.writerow(row)
            f.flush()
            print(f"[{i+1}/{N_SAMPLES}] " + " ".join(f"{k}={s[k]:.4g}" for k in RANGES.keys()) +
                  f" -> PS={out['PS']:.1f} ED={out['ED']:.1f} SD={out['SD']:.2f} PI={out['PI']:.2f} "
                  f"grad={out['gradient']:.2f}", flush=True)

    print("\nDone. See uncertainty_results.csv for the full sample table "
          "(compute percentile bands per output column).", flush=True)
