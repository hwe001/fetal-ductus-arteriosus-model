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
Step 3 (reviewer round 1): local one-at-a-time (OAT) sensitivity analysis of
the two-compartment + 1D DA model (pda_model_v3_twocompartment.py). For each
high-level, literature-adjacent parameter, vary it +-20% and +-40% from
baseline (holding everything else fixed), re-run the full coupled 0D+1D
model, and record the resulting PS/ED/S-D/PI (Ao end) and the 0D layer's own
PA-Ao pressure gradient. Reports normalized elasticities
    E = (dOutput/Output_baseline) / (dParam/Param_baseline)
so parameters can be ranked by how strongly each output responds to them --
directly answering the reviewer's request to "show whether these parameters
are uniquely recoverable" / "report parameter profiles."

Checkpointed to CSV (flushed after every run) -- earlier long sweeps in this
project were killed by the environment mid-run with fully-buffered output.
"""
import csv
import os
import numpy as np

from two_compartment_model import derive_parameters
from pda_model_v3_twocompartment import run, compute_indices

CSV_PATH = "sensitivity_results.csv"
N = 60000  # ~2 cycles, consistent with earlier calibration sweeps' speed/accuracy tradeoff

BASELINE = dict(
    combined_co_ml_min=None,  # None => use module default (derive_parameters() default)
    rv_lv_ratio=None,
    shunt_fraction=None,
    p_pa_mean_mmhg=None,
    p_ao_mean_mmhg=None,
    stiffness_scale=0.01,
)


def eval_point(combined_co_ml_min=None, rv_lv_ratio=None, shunt_fraction=None,
               p_pa_mean_mmhg=None, p_ao_mean_mmhg=None, stiffness_scale=0.01):
    kwargs = {}
    if combined_co_ml_min is not None:
        kwargs["combined_co_ml_min"] = combined_co_ml_min
    if rv_lv_ratio is not None:
        kwargs["rv_lv_ratio"] = rv_lv_ratio
    if shunt_fraction is not None:
        kwargs["shunt_fraction"] = shunt_fraction
    if p_pa_mean_mmhg is not None:
        kwargs["p_pa_mean_mmhg"] = p_pa_mean_mmhg
    if p_ao_mean_mmhg is not None:
        kwargs["p_ao_mean_mmhg"] = p_ao_mean_mmhg
    params = derive_parameters(**kwargs)

    geom, res, tc = run(params["k_da"], stiffness_scale, kappa=0.0, N=N,
                         q_rv_mean=params["q_rv_mean"], q_lv_mean=params["q_lv_mean"],
                         r_pulm=params["r_pulm"], r_sys=params["r_sys"],
                         p_pa_init_mmhg=params["p_pa_mean_mmhg"], p_ao_init_mmhg=params["p_ao_mean_mmhg"])
    idx = compute_indices(geom, res, "ao")

    t0 = tc["t"]
    mask0 = t0 > t0[-1] - (t0[-1] / 15)  # last cycle, matches n_cycles=15 default
    gradient = (tc["P_pa_mmHg"][mask0] - tc["P_ao_mmHg"][mask0]).mean()

    return dict(PS=idx["PS"], ED=idx["ED"], SD=idx["SD"], PI=idx["PI"], gradient=gradient)


def log(writer, f, param_name, param_value, param_frac_change, out):
    writer.writerow([param_name, param_value, param_frac_change,
                      out["PS"], out["ED"], out["SD"], out["PI"], out["gradient"]])
    f.flush()
    print(f"[{param_name}={param_value:.4g} ({param_frac_change:+.0%})] "
          f"PS={out['PS']:.2f} ED={out['ED']:.2f} SD={out['SD']:.2f} PI={out['PI']:.2f} "
          f"grad={out['gradient']:.2f}mmHg", flush=True)


if __name__ == "__main__":
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["param_name", "param_value", "frac_change", "PS", "ED", "SD", "PI", "gradient"])
            f.flush()

        print("=== baseline ===", flush=True)
        base = eval_point()
        log(writer, f, "baseline", 0.0, 0.0, base)

        from two_compartment_model import COMBINED_CO_ML_MIN, RV_LV_RATIO, DA_SHUNT_FRACTION, \
            P_PA_MEAN_MMHG, P_AO_MEAN_MMHG

        param_baselines = dict(
            combined_co_ml_min=COMBINED_CO_ML_MIN,
            rv_lv_ratio=RV_LV_RATIO,
            shunt_fraction=DA_SHUNT_FRACTION,
            p_pa_mean_mmhg=P_PA_MEAN_MMHG,
            p_ao_mean_mmhg=P_AO_MEAN_MMHG,
            stiffness_scale=0.01,
        )

        for pname, pbase in param_baselines.items():
            for frac in (-0.4, -0.2, 0.2, 0.4):
                pval = pbase * (1 + frac)
                kwargs = {pname: pval}
                out = eval_point(**kwargs)
                log(writer, f, pname, pval, frac, out)

        print("\nDone. See sensitivity_results.csv for full table; "
              "compute elasticities as (out/base_out - 1) / frac_change.", flush=True)
