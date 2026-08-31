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
Reviewer round 4, item 4: a figure showing PI, ED, and S/D TOGETHER across
RV/LV relative timing offset -- presented explicitly as a SENSITIVITY
finding, not a claimed mechanism/explanation for the PI discrepancy. At
HR=150bpm, a 10-15% cycle-fraction offset corresponds to ~40-60ms of
interventricular mechanical delay -- there is no fetal evidence located in
this project's literature search supporting a delay of this specific
magnitude, so this must not be presented as "the explanation" for PI, only
as a demonstration that the trade-off (PI improves, ED/S-D degrade) is a
real, reproducible feature of the model's response to this one factor.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from da_rlc_coupled_model import simulate_coupled, compute_indices_0d

TARGET = dict(PS=41.32, ED=13.05, SD=3.85, PI=2.15)

offsets = np.linspace(0.0, 0.20, 11)
results = {"PS": [], "ED": [], "SD": [], "PI": []}

for off in offsets:
    res = simulate_coupled(n_cycles=8, steps_per_cycle=4000, rv_lv_phase_offset=off)
    idx = compute_indices_0d(res)
    for k in results:
        results[k].append(idx[k])
    print(f"offset={off:.2f} ({off*400:.0f}ms at 150bpm): "
          f"PS={idx['PS']:.1f} ED={idx['ED']:.1f} SD={idx['SD']:.2f} PI={idx['PI']:.2f}")

offsets_ms = offsets * (60.0 / 150.0) * 1000  # cycle fraction -> ms at 150bpm

fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))

for ax, key, ylabel in zip(axes, ["ED", "SD", "PI"], ["End-diastolic velocity (cm/s)", "S/D ratio", "PI"]):
    ax.plot(offsets_ms, results[key], "o-", color="#2166ac", linewidth=2, markersize=5)
    ax.axhline(TARGET[key], color="#b2182b", linestyle="--", linewidth=1.5, label=f"cohort target ({TARGET[key]})")
    ax.set_xlabel("RV/LV timing offset (ms, at HR=150bpm)")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

axes[2].set_title("PI improves toward target...", fontsize=10)
axes[0].set_title("...while ED moves away...", fontsize=10)
axes[1].set_title("...and S/D overshoots", fontsize=10)

fig.suptitle("RV/LV ejection timing offset: a sensitivity finding, not a claimed mechanism\n"
             "(10-15% cycle offset = ~40-60ms interventricular delay -- no supporting fetal evidence located)",
             fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("Figure_RVLV_timing_offset_sensitivity.png", dpi=200)
print("\nSaved Figure_RVLV_timing_offset_sensitivity.png")
