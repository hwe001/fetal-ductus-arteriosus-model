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
Step 4 (reviewer round 1): k-fold cross-validation of the v2 single-tube
model (pda_model.py), instead of reporting the in-sample fit to the full
cohort's own mean as "validation" (the reviewer's flagged conflation).

Simplification, disclosed rather than hidden: a full grid re-search of all
4 free parameters (Q_MEAN, BASE_FRAC, KAPPA, STIFFNESS_SCALE) per fold would
cost ~4x the original ~50-run sweep. Instead, BASE_FRAC/KAPPA/STIFFNESS_SCALE
are held at their globally-calibrated values (fit once on the full cohort --
NOT re-validated out-of-sample here), and only Q_MEAN (the flow-amplitude
parameter, bisected against peak-systolic velocity) is refit per fold. This
tests whether the most directly data-driven parameter generalizes to held-out
patients; it is NOT a full nested cross-validation of every free parameter --
noted as a limitation of this analysis, not overstated as more than it is.

For each fold: calibrate Q_MEAN on the OTHER folds' (training) mean PS,
evaluate the resulting simulated PS/ED/S-D/PI against the HELD-OUT fold's own
mean targets. Reports predicted-vs-observed and out-of-sample error stats.
"""
import csv
import os
import numpy as np
import pandas as pd

from pda_model import run, compute_indices, BASE_FRAC, KAPPA, STIFFNESS_SCALE

CSV_PATH = "cross_validation_results.csv"
N = 60000
K_FOLDS = 4
SEED = 42


def bisect_q_mean(target_ps, lo=0.10, hi=0.45, steps=5):
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        geom, res = run(q_mean=mid, base_frac=BASE_FRAC, kappa=KAPPA,
                         stiffness_scale=STIFFNESS_SCALE, N=N)
        idx = compute_indices(geom, res, "ao")
        if idx["PS"] < target_ps:
            lo = mid
        else:
            hi = mid
    mid = 0.5 * (lo + hi)
    geom, res = run(q_mean=mid, base_frac=BASE_FRAC, kappa=KAPPA,
                     stiffness_scale=STIFFNESS_SCALE, N=N)
    idx = compute_indices(geom, res, "ao")
    return mid, idx


if __name__ == "__main__":
    df = pd.read_csv("anonymized_doppler_data.csv").dropna(subset=["PS_mean_cms"]).reset_index(drop=True)
    n = len(df)
    rng = np.random.RandomState(SEED)
    fold_assignment = rng.permutation(n) % K_FOLDS

    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["fold", "n_train", "n_test", "q_mean_cal",
                              "train_PS_target", "test_PS_obs", "test_ED_obs", "test_SD_obs", "test_PI_obs",
                              "sim_PS", "sim_ED", "sim_SD", "sim_PI"])
            f.flush()

        for k in range(K_FOLDS):
            test_mask = fold_assignment == k
            train_df = df[~test_mask]
            test_df = df[test_mask]

            train_ps_target = train_df["PS_mean_cms"].mean()
            q_cal, sim_idx = bisect_q_mean(train_ps_target)

            row = [k, len(train_df), len(test_df), q_cal, train_ps_target,
                   test_df["PS_mean_cms"].mean(), test_df["ED_mean_cms"].mean(),
                   test_df["SD_ratio_mean"].mean(), test_df["PI_mean"].mean(),
                   sim_idx["PS"], sim_idx["ED"], sim_idx["SD"], sim_idx["PI"]]
            writer.writerow(row)
            f.flush()
            print(f"fold {k}: n_train={len(train_df)} n_test={len(test_df)} "
                  f"q_mean_cal={q_cal:.4f} (train PS target={train_ps_target:.1f}) -> "
                  f"sim PS={sim_idx['PS']:.1f} ED={sim_idx['ED']:.1f} SD={sim_idx['SD']:.2f} PI={sim_idx['PI']:.2f} "
                  f"| held-out obs PS={test_df['PS_mean_cms'].mean():.1f} "
                  f"ED={test_df['ED_mean_cms'].mean():.1f} "
                  f"SD={test_df['SD_ratio_mean'].mean():.2f} PI={test_df['PI_mean'].mean():.2f}",
                  flush=True)

    print("\nDone. See cross_validation_results.csv.", flush=True)
