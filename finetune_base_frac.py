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

"""Fine-tune step: re-bisect Q_MEAN for PS match at higher BASE_FRAC values,
holding kappa=-0.3, stiffness_scale=0.01 (the best v2 grid combo)."""
import csv
from pda_model import run, compute_indices

TARGET = dict(PS=41.32, ED=13.05, SD=3.85, PI=2.15)
KAPPA, STIFF = -0.3, 0.01
N = 60000


def score(idx):
    return sum(abs(idx[k] - TARGET[k]) / TARGET[k] for k in TARGET)


def bisect_q_mean(base_frac, lo=0.15, hi=0.45, steps=6):
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        geom, res = run(q_mean=mid, base_frac=base_frac, kappa=KAPPA, stiffness_scale=STIFF, N=N)
        idx = compute_indices(geom, res, "ao")
        print(f"  base_frac={base_frac:.2f} q_mean={mid:.4f} -> PS={idx['PS']:.2f}", flush=True)
        if idx["PS"] < TARGET["PS"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    with open("finetune_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["base_frac", "q_mean", "PS", "ED", "SD", "PI", "score"])
        for base_frac in (0.65, 0.75, 0.8, 0.85):
            q_cal = bisect_q_mean(base_frac)
            geom, res = run(q_mean=q_cal, base_frac=base_frac, kappa=KAPPA, stiffness_scale=STIFF, N=N)
            idx = compute_indices(geom, res, "ao")
            s = score(idx)
            writer.writerow([base_frac, q_cal, idx["PS"], idx["ED"], idx["SD"], idx["PI"], s])
            f.flush()
            print(f"==> base_frac={base_frac:.2f} q_mean_cal={q_cal:.4f} -> "
                  f"PS={idx['PS']:.1f} ED={idx['ED']:.1f} SD={idx['SD']:.2f} PI={idx['PI']:.2f} score={s:.2f}",
                  flush=True)
