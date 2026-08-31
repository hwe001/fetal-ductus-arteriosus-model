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
*** SUPERSEDED (reviewer round 6) -- DO NOT USE THIS FILE'S NUMBERS ***
This script fits Ledoit-Wolf shrinkage directly to UNSTANDARDIZED, mixed-unit
variables (PS/ED in cm/s alongside dimensionless S/D/PI). Shrinkage toward a
scaled-identity target is NOT invariant to variable scaling, so the
large-variance velocity variables dominate the regularization -- this
produces the OBSOLETE D^2=0.32 / 27th-percentile / "73% of patients farther"
result, which does NOT match the manuscript. The manuscript reports the
CORRECTED, standardized analysis in `multivariate_comparison_v3.py`
(D^2=1.99, 41st percentile, 59% of patients farther, LOO median=2.52) --
run that script, not this one, to reproduce the manuscript's numbers. This
file is retained only as a record of the error found and fixed; see
model_plan_and_literature_data.md Section 23 for the full account.
***

Reviewer round 5 correction: the original multivariate_comparison.py compared
two NON-COMPARABLE quantities and called them "statistically indistinguishable"
-- (a) the model's Mahalanobis distance from the cohort centroid, and (b) the
medoid patient's own MEAN distance to all other patients. No hypothesis test
or uncertainty interval was reported. This script redoes the analysis
properly:

  1. Leave-one-out (LOO) squared Mahalanobis distance for every complete-case
     patient: for patient i, estimate the mean/covariance from the OTHER 21
     patients only, then compute patient i's D^2 against that out-of-sample
     estimate. This gives a proper empirical reference DISTRIBUTION of
     "how far a genuine cohort member typically sits from an independent
     estimate of the cohort," which the model's distance can be compared to
     on a like-for-like basis.
  2. The model's squared Mahalanobis distance, using the FULL n=22 cohort's
     mean/covariance (the model is not a cohort member, so no leave-one-out
     is needed for it).
  3. The model's EMPIRICAL PERCENTILE within the LOO reference distribution
     (what fraction of real patients have a LOO distance at least as large
     as the model's) -- this, not a distance-to-distance comparison, is the
     correct way to ask "is the model typical of this cohort."
  4. Shrinkage (Ledoit-Wolf) covariance estimation throughout, given n=22 is
     small relative to 4 correlated variables (raw sample covariance is
     poorly conditioned at this n/p ratio).
  5. Squared Mahalanobis distance (D^2) reported consistently, not D --
     D^2 is the natural quantity (chi-squared-distributed under
     multivariate normality with p=4 df, for reference/context only, since
     we primarily rely on the empirical LOO distribution instead).
"""
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

CSV_PATH = "anonymized_doppler_data.csv"


def load_complete_cases():
    df = pd.read_csv(CSV_PATH)
    return df.dropna(subset=["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]).copy()


def shrinkage_mean_cov(X):
    lw = LedoitWolf().fit(X)
    return X.mean(axis=0), lw.covariance_, lw.shrinkage_


def mahalanobis_sq(x, mean, cov):
    diff = x - mean
    return float(diff @ np.linalg.inv(cov) @ diff)


def analyze(simulated_vector, label="simulated"):
    df = load_complete_cases()
    X = df[["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]].values
    n = X.shape[0]
    labels = ["PS", "ED", "S/D", "PI"]

    # full-cohort shrinkage mean/cov (used for the model's distance)
    full_mean, full_cov, full_shrinkage = shrinkage_mean_cov(X)
    print(f"=== Complete-case cohort (n={n}) ===")
    print("mean vector:", np.round(full_mean, 3))
    print(f"Ledoit-Wolf shrinkage intensity (full cohort): {full_shrinkage:.3f} "
          f"(0=no shrinkage/raw sample cov, 1=fully shrunk to diagonal)")

    # --- LOO reference distribution ---
    loo_d2 = np.zeros(n)
    for i in range(n):
        mask = np.arange(n) != i
        loo_mean, loo_cov, _ = shrinkage_mean_cov(X[mask])
        loo_d2[i] = mahalanobis_sq(X[i], loo_mean, loo_cov)

    print(f"\nLOO squared Mahalanobis distance across {n} patients: "
          f"min={loo_d2.min():.2f} median={np.median(loo_d2):.2f} max={loo_d2.max():.2f}")

    # --- model's distance (full-cohort shrinkage estimate, model is not a cohort member) ---
    v = np.array(simulated_vector)
    model_d2 = mahalanobis_sq(v, full_mean, full_cov)
    percentile = (loo_d2 < model_d2).mean() * 100

    print(f"\n=== {label}: {np.round(v, 3)} ===")
    print(f"Model's squared Mahalanobis distance from full-cohort (shrinkage) estimate: {model_d2:.2f}")
    print(f"Empirical percentile within the LOO patient-distance distribution: "
          f"{percentile:.0f}% (i.e. {100-percentile:.0f}% of real patients sit FARTHER "
          f"from an independent estimate of their own cohort than the model does)")

    # chi-squared reference (context only, not the primary claim -- multivariate
    # normality of n=22 real clinical measurements is not itself verified)
    from scipy import stats
    chi2_p = 1 - stats.chi2.cdf(model_d2, df=4)
    print(f"(for context only, assuming approx. multivariate normality: chi-sq(4) "
          f"upper-tail p={chi2_p:.3f} for the model's D^2 -- NOT the primary claim, "
          f"since normality of this small clinical sample is unverified)")

    print("\nunivariate z-scores (simulated vs. full-cohort mean, raw SD for interpretability):")
    sds = X.std(axis=0, ddof=1)
    for i, l in enumerate(labels):
        z = (v[i] - full_mean[i]) / sds[i]
        print(f"  {l}: z={z:+.2f}")

    return dict(n=n, loo_d2=loo_d2, model_d2=model_d2, percentile=percentile, full_shrinkage=full_shrinkage)


if __name__ == "__main__":
    raise SystemExit(
        "This script is SUPERSEDED and produces numbers that do NOT match the "
        "published manuscript. Run ../multivariate_comparison.py instead -- see this "
        "file's module docstring and model_plan_and_literature_data.md for why."
    )

    analyze([41.58, 10.53, 3.95, 1.42], label="zero-fitting simulated (Leao geometry, Cd=0.7)")
