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
Calibration sweep for the PDA model. Target (anonymized cohort, n=24):
PS=41.32 cm/s, ED=13.05 cm/s, S/D=3.85, PI=2.15 (see validation_targets.json).

Strategy (see model_plan_and_literature_data.md Section 5):
  1. bisect Q_MEAN to hit the PS target at the Ao (outlet) end, holding
     KAPPA/STIFFNESS_SCALE/Q_PULSE_FRAC fixed.
  2. grid-sweep KAPPA and STIFFNESS_SCALE (which shape wave reflection and
     tube compliance, i.e. the ED/S-D/PI dynamics) at that Q_MEAN.
  3. report the best combination and re-run it for longer to confirm.

Every result is appended to calibration_results_v2.csv immediately (flushed
after each run) so progress survives even if this process is killed partway.

v2: uses the decoupled baseline+spike inlet waveform (BASE_FRAC), replacing
v1's Q_PULSE_FRAC shape which could not simultaneously match PS/ED and S/D/PI
(see model_plan_and_literature_data.md Section 6).
"""
import csv
import os
import numpy as np
from pda_model import run, compute_indices

TARGET = dict(PS=41.32, ED=13.05, SD=3.85, PI=2.15)
N_SWEEP = 60000   # ~2 cycles at T=0.4s
CSV_PATH = "calibration_results_v2.csv"


def score(idx):
    return sum(abs(idx[k] - TARGET[k]) / TARGET[k] for k in TARGET)


def eval_params(q_mean, base_frac, kappa, stiffness_scale, N=N_SWEEP):
    geom, res = run(q_mean=q_mean, base_frac=base_frac, kappa=kappa,
                     stiffness_scale=stiffness_scale, N=N)
    idx = compute_indices(geom, res, "ao")
    return idx


def log(writer, f, stage, q_mean, base_frac, kappa, stiffness_scale, idx):
    s = score(idx)
    writer.writerow([stage, q_mean, base_frac, kappa, stiffness_scale,
                      idx["PS"], idx["ED"], idx["SD"], idx["PI"], s])
    f.flush()
    print(f"[{stage}] q_mean={q_mean:.4f} base_frac={base_frac:.2f} kappa={kappa:+.2f} "
          f"stiff={stiffness_scale:.4f} -> PS={idx['PS']:.1f} ED={idx['ED']:.1f} "
          f"SD={idx['SD']:.2f} PI={idx['PI']:.2f} score={s:.2f}", flush=True)
    return s


if __name__ == "__main__":
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["stage", "q_mean", "base_frac", "kappa", "stiffness_scale",
                              "PS", "ED", "SD", "PI", "score"])
            f.flush()

        # --- step 1: bisect Q_MEAN for PS match, other params at first-pass values ---
        KAPPA0, STIFF0, BASE0 = 0.0, 0.01, 0.5
        lo, hi = 0.10, 0.40
        for _ in range(5):
            mid = 0.5 * (lo + hi)
            idx = eval_params(mid, BASE0, KAPPA0, STIFF0)
            log(writer, f, "bisect", mid, BASE0, KAPPA0, STIFF0, idx)
            if idx["PS"] < TARGET["PS"]:
                lo = mid
            else:
                hi = mid
        Q_CAL = 0.5 * (lo + hi)
        print(f"\n==> calibrated Q_MEAN = {Q_CAL:.4f} cm^3/s\n", flush=True)

        # --- step 2: grid sweep KAPPA x STIFFNESS_SCALE x BASE_FRAC ---
        best = None
        for kappa in (-0.3, 0.0, 0.3, 0.6):
            for stiff in (0.005, 0.01, 0.02):
                for base_frac in (0.2, 0.35, 0.5, 0.65):
                    idx = eval_params(Q_CAL, base_frac, kappa, stiff)
                    s = log(writer, f, "grid", Q_CAL, base_frac, kappa, stiff, idx)
                    if best is None or s < best[0]:
                        best = (s, kappa, stiff, base_frac, idx)

        print("\n==> BEST:", best, flush=True)
