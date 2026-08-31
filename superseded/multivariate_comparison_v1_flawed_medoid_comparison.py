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
*** SUPERSEDED -- DO NOT USE THIS FILE'S NUMBERS ***
This first version claimed the model was "statistically indistinguishable"
from the cohort's medoid patient by comparing two non-comparable quantities
with no hypothesis test attached (reviewer round 5 correction). The
CANONICAL, currently-correct script is `multivariate_comparison_v3.py`
(D^2=1.99, 41st percentile) -- see that file and
model_plan_and_literature_data.md Sections 21/23 for the full correction
history. Retained here only as a record of the original error.
***

Reviewer round 4: the four Doppler targets (PS_mean=41.32, ED_mean=13.05,
S/D_mean=3.85, PI_mean=2.15) are SEPARATELY-AVERAGED marginal statistics.
Since S/D and PI are per-patient NONLINEAR ratios (S/D=PS/ED by definition
for any single waveform), mean(S/D) != mean(PS)/mean(ED) in general (Jensen's
inequality) -- confirmed numerically: 41.32/13.05=3.17 vs. the reported
mean(S/D)=3.85. No single "representative waveform" can simultaneously have
PS=41.32, ED=13.05, AND S/D=3.85 -- these three numbers are mutually
over-determined and cannot all be exactly satisfied by one internally-
consistent (PS,ED) pair, since S/D is fully determined by PS/ED once those
two are fixed.

This script builds the internally-consistent alternative the reviewer
requested: patient-level (PS,ED,S/D,PI) vectors (complete cases only, n=22
-- excludes Patient12, who lacks an S/D value), their covariance/
correlation structure, the simulated model's Mahalanobis distance from that
multivariate distribution, and a medoid-patient alternative target that is,
by construction, internally consistent (a REAL patient's own actual vector,
not a blend of marginal statistics).
"""
import numpy as np
import pandas as pd

CSV_PATH = "anonymized_doppler_data.csv"


def load_complete_cases():
    df = pd.read_csv(CSV_PATH)
    complete = df.dropna(subset=["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]).copy()
    return complete


def analyze(simulated_vector, label="simulated"):
    df = load_complete_cases()
    X = df[["PS_mean_cms", "ED_mean_cms", "SD_ratio_mean", "PI_mean"]].values
    n = X.shape[0]

    mean_vec = X.mean(axis=0)
    cov = np.cov(X, rowvar=False)
    corr = np.corrcoef(X, rowvar=False)

    print(f"=== Patient-level complete-case data (n={n}) ===")
    print("mean vector (PS, ED, S/D, PI):", np.round(mean_vec, 3))
    print("\ncorrelation matrix (PS, ED, S/D, PI):")
    labels = ["PS", "ED", "S/D", "PI"]
    print("        " + "  ".join(f"{l:>7s}" for l in labels))
    for i, l in enumerate(labels):
        print(f"{l:>7s} " + "  ".join(f"{corr[i,j]:7.3f}" for j in range(4)))

    # sanity check: mean(S/D) vs mean(PS)/mean(ED)
    ratio_of_means = mean_vec[0] / mean_vec[1]
    mean_of_ratios = mean_vec[2]
    print(f"\nratio of means PS/ED = {ratio_of_means:.3f}  vs.  mean of per-patient S/D = {mean_of_ratios:.3f}")
    print(f"(difference confirms Jensen's-inequality-type averaging artifact -- "
          f"NOT an error, both numbers are individually correct)")

    # Mahalanobis distance of the simulated vector
    v = np.array(simulated_vector)
    diff = v - mean_vec
    inv_cov = np.linalg.inv(cov)
    maha = np.sqrt(diff @ inv_cov @ diff)
    print(f"\n=== {label} vector: {np.round(v,3)} ===")
    print(f"Mahalanobis distance from patient-level distribution: {maha:.3f}")

    # empirical percentile: what fraction of patients are FARTHER (in
    # Mahalanobis distance from the same mean/cov) than the simulated point?
    patient_dists = np.array([np.sqrt((x - mean_vec) @ inv_cov @ (x - mean_vec)) for x in X])
    pct_closer = (patient_dists < maha).mean() * 100
    print(f"empirical percentile: simulated point is farther from the cohort mean than "
          f"{pct_closer:.0f}% of the real patients themselves")

    # univariate z-scores/percentiles for context
    sds = X.std(axis=0, ddof=1)
    print("\nunivariate z-scores (simulated vs. patient-level mean/SD):")
    for i, l in enumerate(labels):
        z = (v[i] - mean_vec[i]) / sds[i]
        print(f"  {l}: z={z:+.2f}")

    # medoid patient: the real patient whose own vector minimizes total
    # Mahalanobis distance to all others -- an internally-consistent
    # alternative "representative" target (a REAL waveform, not a blend)
    dists_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            d = X[i] - X[j]
            dists_matrix[i, j] = np.sqrt(d @ inv_cov @ d)
    medoid_idx = np.argmin(dists_matrix.sum(axis=1))
    medoid_row = df.iloc[medoid_idx]
    print(f"\nmedoid patient ({medoid_row['patient_id']}): "
          f"PS={medoid_row['PS_mean_cms']:.2f} ED={medoid_row['ED_mean_cms']:.2f} "
          f"S/D={medoid_row['SD_ratio_mean']:.2f} PI={medoid_row['PI_mean']:.2f}")
    medoid_dist = dists_matrix[medoid_idx].mean()
    print(f"(mean Mahalanobis distance from medoid to all other patients: {medoid_dist:.3f}, "
          f"for comparison to the simulated point's distance of {maha:.3f})")

    return dict(n=n, mean_vec=mean_vec, cov=cov, corr=corr, maha=maha,
                pct_closer=pct_closer, medoid=medoid_row)


if __name__ == "__main__":
    raise SystemExit(
        "This script is SUPERSEDED and produces numbers that do NOT match the "
        "published manuscript. Run ../multivariate_comparison.py instead -- see this "
        "file's module docstring and model_plan_and_literature_data.md for why."
    )

    # current best (literature-sourced, zero-Doppler-fitting) simulated vector,
    # post ED-definition fix (Section 15/17): PS=41.6, ED=10.5, S/D=3.95, PI=1.42
    analyze([41.58, 10.53, 3.95, 1.42], label="zero-fitting simulated (Leao geometry, Cd=0.7)")
