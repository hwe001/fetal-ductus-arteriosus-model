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
*** CANONICAL SCRIPT for the multivariate/Mahalanobis result (Sections 2.6,
3.3, and the Abstract) -- this IS the single entry point (previously
developed as multivariate_comparison_v3.py; renamed here for clarity). Its
output reproduces the manuscript's D^2=1.99 / 41st-percentile / "59% of
patients farther" / LOO-median=2.52 result. Two earlier, flawed analyses
are kept in superseded/ for transparency only -- do not run them expecting
the manuscript's numbers; see model_plan_and_literature_data.md Sections
21/23 for the full correction history. ***

Reviewer round 6 correction: Ledoit-Wolf shrinkage toward a SCALED IDENTITY
target is not invariant to variable scaling -- PS/ED (cm/s, large variance)
were shrunk differently than dimensionless S/D/PI in v2, biasing the
covariance estimate. Fixed: standardize (z-score) using TRAINING-SET
statistics only, at every step, before fitting shrinkage covariance.

Leave-one-out (LOO) procedure, corrected:
  1. For patient i, estimate mean/SD from the OTHER 21 patients only.
  2. Standardize those 21 patients using that training-set mean/SD.
  3. Fit Ledoit-Wolf shrinkage covariance on the STANDARDIZED training data.
  4. Standardize patient i using the SAME training-set mean/SD (not its own).
  5. Compute patient i's squared Mahalanobis distance in standardized space.
Model's distance: standardize using the FULL (n=22) cohort's mean/SD, fit
Ledoit-Wolf on the full standardized cohort, compute the model's D^2 in that
same standardized space.

The chi-squared(4) reference is REMOVED per the reviewer -- not reliable
after shrinkage + small-sample LOO construction; the empirical percentile
is the sole reported statistic.
"""
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

import os as _os
CSV_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "anonymized_doppler_data.csv")


def load_complete_cases():
    df = pd.read_csv(CSV_PATH)
    return df.dropna(subset=["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]).copy()


def standardize(X, mean, sd):
    return (X - mean) / sd


def shrinkage_cov_standardized(X_std):
    lw = LedoitWolf().fit(X_std)
    return lw.covariance_, lw.shrinkage_


def mahalanobis_sq(x, cov):
    # x already standardized (mean 0 by construction of training stats);
    # distance is computed directly against the (standardized-space) covariance
    return float(x @ np.linalg.inv(cov) @ x)


def analyze(simulated_vector, label="simulated"):
    df = load_complete_cases()
    X = df[["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]].values
    n = X.shape[0]
    labels = ["PS", "ED", "S/D", "PI"]

    # --- full-cohort standardization + shrinkage (for the model's distance) ---
    full_mean = X.mean(axis=0)
    full_sd = X.std(axis=0, ddof=1)
    X_full_std = standardize(X, full_mean, full_sd)
    full_cov, full_shrinkage = shrinkage_cov_standardized(X_full_std)
    print(f"=== Complete-case cohort (n={n}), STANDARDIZED before shrinkage ===")
    print(f"Ledoit-Wolf shrinkage intensity (full cohort, standardized): {full_shrinkage:.3f}")

    # --- LOO reference distribution, standardized within each fold ---
    loo_d2 = np.zeros(n)
    for i in range(n):
        mask = np.arange(n) != i
        train_mean = X[mask].mean(axis=0)
        train_sd = X[mask].std(axis=0, ddof=1)
        X_train_std = standardize(X[mask], train_mean, train_sd)
        cov_i, _ = shrinkage_cov_standardized(X_train_std)
        x_i_std = standardize(X[i], train_mean, train_sd)
        loo_d2[i] = mahalanobis_sq(x_i_std, cov_i)

    print(f"\nLOO squared Mahalanobis distance (standardized) across {n} patients: "
          f"min={loo_d2.min():.2f} median={np.median(loo_d2):.2f} max={loo_d2.max():.2f}")

    # --- model's distance, full-cohort standardization ---
    v = np.array(simulated_vector)
    v_std = standardize(v, full_mean, full_sd)
    model_d2 = mahalanobis_sq(v_std, full_cov)
    percentile = (loo_d2 < model_d2).mean() * 100

    print(f"\n=== {label}: {np.round(v, 3)} ===")
    print(f"Model's squared Mahalanobis distance (standardized, full-cohort shrinkage): {model_d2:.2f}")
    print(f"Empirical percentile within the LOO patient-distance distribution: "
          f"{percentile:.0f}% (i.e. {100-percentile:.0f}% of real patients sit FARTHER "
          f"from an independent estimate of their own cohort than the model does)")

    print("\nunivariate z-scores (simulated vs. full-cohort mean, raw SD for interpretability):")
    for i, l in enumerate(labels):
        print(f"  {l}: z={v_std[i]:+.2f}")

    return dict(n=n, loo_d2=loo_d2, model_d2=model_d2, percentile=percentile, full_shrinkage=full_shrinkage)


def paired_fold_sensitivity(simulated_vector):
    """Reviewer round 6 (minor wording point): the PRIMARY reported result
    computes the model's D^2 once, from the full-cohort standardization
    (`analyze()` above), then places it within the LOO distribution of
    patients' own out-of-sample distances (each patient standardized against
    the OTHER 21, not against the full n=22). As an optional SECONDARY
    sensitivity check, this function instead recomputes the model's D^2
    WITHIN each of the 22 LOO folds (i.e. using that fold's own training-set
    standardization for both the model and the held-out patient), to check
    the primary result isn't an artifact of using full-cohort vs. leave-one-
    out standardization for the model specifically."""
    df = load_complete_cases()
    X = df[["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]].values
    n = X.shape[0]
    v = np.array(simulated_vector)

    paired_model_d2 = np.zeros(n)
    paired_patient_d2 = np.zeros(n)
    for i in range(n):
        mask = np.arange(n) != i
        train_mean = X[mask].mean(axis=0)
        train_sd = X[mask].std(axis=0, ddof=1)
        X_train_std = standardize(X[mask], train_mean, train_sd)
        cov_i, _ = shrinkage_cov_standardized(X_train_std)
        v_std = standardize(v, train_mean, train_sd)
        paired_model_d2[i] = mahalanobis_sq(v_std, cov_i)
        x_i_std = standardize(X[i], train_mean, train_sd)
        paired_patient_d2[i] = mahalanobis_sq(x_i_std, cov_i)

    frac_patient_farther = (paired_patient_d2 > paired_model_d2).mean() * 100
    print(f"\n=== paired-fold sensitivity check ===")
    print(f"model's D^2 across the 22 folds: min={paired_model_d2.min():.2f} "
          f"max={paired_model_d2.max():.2f} mean={paired_model_d2.mean():.2f}")
    print(f"fraction of folds where the held-out patient is farther than the model: "
          f"{frac_patient_farther:.0f}%")
    return dict(paired_model_d2=paired_model_d2, paired_patient_d2=paired_patient_d2,
                frac_patient_farther=frac_patient_farther)


if __name__ == "__main__":
    analyze([41.58, 10.53, 3.95, 1.42], label="zero-fitting simulated (Leao geometry, Cd=0.7)")
    paired_fold_sensitivity([41.58, 10.53, 3.95, 1.42])
