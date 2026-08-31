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

"""Generates the simulated DA velocity waveform figure (one cardiac cycle,
zero-fitting default parameters) for the manuscript's Results section."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from da_rlc_coupled_model import simulate_coupled, compute_indices_0d, T_PERIOD

res = simulate_coupled(n_cycles=8, steps_per_cycle=4000)
idx = compute_indices_0d(res)

t = res["t"]
mask = t > t[-1] - T_PERIOD
tt = (t[mask] - (t[-1] - T_PERIOD)) * 1000  # ms
u = res["u_da"][mask]

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(tt, u, color="#2166ac", linewidth=2)
ax.axhline(idx["PS"], color="#b2182b", linestyle=":", linewidth=1, alpha=0.7)
ax.axhline(idx["ED"], color="#4393c3", linestyle=":", linewidth=1, alpha=0.7)
ymax = idx["PS"] * 1.18
ymin = -idx["PS"] * 0.03
ax.set_ylim(ymin, ymax)
ax.annotate(f"PS = {idx['PS']:.1f} cm/s", xy=(tt[np.argmax(u)], idx["PS"]),
            xytext=(tt[np.argmax(u)] + 15, idx["PS"] + ymax * 0.06), fontsize=9, color="#b2182b",
            ha="left", va="bottom")
ax.annotate(f"ED = {idx['ED']:.1f} cm/s", xy=(tt[-1], idx["ED"]),
            xytext=(tt[-1] - 155, idx["ED"] + ymax * 0.05), fontsize=9, color="#4393c3",
            ha="left", va="bottom")
ax.set_xlabel("Time within cardiac cycle (ms)")
ax.set_ylabel("DA velocity, $Q_{da}/A_{throat}$ (cm/s)")
ax.set_title("Simulated fetal DA velocity waveform\n(literature-sourced parameters, zero Doppler fitting)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("paper_figures/Figure_simulated_waveform.png", dpi=200)
print("Saved paper_figures/Figure_simulated_waveform.png")
print("PS", idx["PS"], "ED", idx["ED"], "SD", idx["SD"], "PI", idx["PI"])
