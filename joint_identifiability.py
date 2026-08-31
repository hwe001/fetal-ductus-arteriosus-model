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
TERMINOLOGY (reviewer round 3): this is a joint SENSITIVITY / response-
surface scan, NOT a complete identifiability analysis -- true identifiability
needs uncertainty quantification, parameter correlations, and ideally a
likelihood-based or Bayesian treatment, none of which this script does. Kept
the filename for continuity with earlier project history; do not describe
its output as "identifiability" in write-ups.

Step 4 (reviewer round 2): a genuine JOINT (not one-at-a-time) sensitivity
scan, now cheap and fast because the de-circularized coupled 0D model
(da_rlc_coupled_model.py) runs in ~3s at full periodic convergence (vs. the
old 1D PDE's ~20-30s per run at only ~2-cycle convergence -- see Section
10.1's correction). 2D grid over the two parameters most directly tied to
the reviewer's own "effective diameter" hypothesis and the DA's loss
character: AREA_SCALE (effective/anatomical throat-area ratio) and
DISCHARGE_COEFF (orifice discharge coefficient) -- both physically
interpretable, both currently unconstrained by independent data for this
specific structure/gestational age.
"""
import csv
import numpy as np

from da_rlc_coupled_model import simulate_coupled, compute_indices_0d, check_convergence, T_PERIOD

TARGET = dict(PS=41.32, ED=13.05, SD=3.85, PI=2.15)
N_CYCLES = 8  # confirmed <0.001% cycle-to-cycle difference -- fully converged


def score(idx):
    return sum(abs(idx[k] - TARGET[k]) / TARGET[k] for k in TARGET)


if __name__ == "__main__":
    area_scales = np.linspace(0.15, 1.0, 8)
    discharge_coeffs = np.linspace(0.5, 0.9, 5)

    rows = []
    with open("joint_identifiability_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["area_scale", "discharge_coeff", "PS", "ED", "SD", "PI", "gradient", "score", "conv_reldiff"])
        for a in area_scales:
            for cd in discharge_coeffs:
                res = simulate_coupled(area_scale=a, discharge_coeff=cd, n_cycles=N_CYCLES, steps_per_cycle=4000)
                idx = compute_indices_0d(res)
                conv = check_convergence(res)
                t = res["t"]
                mask = t > t[-1] - T_PERIOD
                grad = (res["P_pa_mmHg"][mask] - res["P_ao_mmHg"][mask]).mean()
                s = score(idx)
                row = [a, cd, idx["PS"], idx["ED"], idx["SD"], idx["PI"], grad, s, conv["rel_diff"]]
                rows.append(row)
                writer.writerow(row)
                f.flush()
                print(f"area_scale={a:.3f} Cd={cd:.2f} -> PS={idx['PS']:.1f} ED={idx['ED']:.1f} "
                      f"SD={idx['SD']:.2f} PI={idx['PI']:.2f} grad={grad:.2f} score={s:.2f} "
                      f"conv={conv['rel_diff']:.2%}", flush=True)

    print("\nDone -- see joint_identifiability_results.csv")
