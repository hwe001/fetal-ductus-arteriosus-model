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

"""3-panel graphical abstract: model schematic -> simulated waveform ->
the independent diameter-convergence result (the paper's strongest single
finding), connected by arrows, mirroring the sibling CoA project's
graphical-abstract composition style."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

fig = plt.figure(figsize=(15, 5.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1], wspace=0.12, top=0.78, bottom=0.06, left=0.03, right=0.98)

# --- Panel 1: model schematic (cropped/scaled) ---
ax1 = fig.add_subplot(gs[0])
img1 = mpimg.imread("paper_figures/Figure_model_schematic.png")
ax1.imshow(img1)
ax1.axis("off")
ax1.set_title("1. Coupled nonlinear-RL model\n(independently sourced parameters)", fontsize=11, weight="bold")

# --- Panel 2: simulated waveform ---
ax2 = fig.add_subplot(gs[1])
img2 = mpimg.imread("paper_figures/Figure_simulated_waveform.png")
ax2.imshow(img2)
ax2.axis("off")
ax2.set_title("2. Zero-fitting simulation\nPS within 0.6% of cohort", fontsize=11, weight="bold")

# --- Panel 3: diameter convergence bar chart ---
ax3 = fig.add_subplot(gs[2])
labels = ["Doppler-fit\n(velocity-derived)", "Leao et al. 2015\n(independent anatomy)"]
values = [0.68, 0.679]
colors = ["#2166ac", "#b8860b"]
bars = ax3.bar(labels, values, color=colors, width=0.55)
for b, v in zip(bars, values):
    ax3.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=12, weight="bold")
ax3.set_ylim(0, 0.85)
ax3.set_ylabel("Junctional-diameter ratio\n(vs. along-length-average external diameter)", fontsize=9.5)
ax3.set_title("3. Independent convergence\n(0.2 percentage points apart)", fontsize=11, weight="bold")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.grid(axis="y", alpha=0.3)

# --- connecting arrows between panels ---
for x in (0.365, 0.665):
    fig.text(x, 0.42, "→", fontsize=28, ha="center", va="center", weight="bold", color="#444444")

fig.suptitle("A Coupled Reduced-Order Model of Fetal Ductus Arteriosus Flow", fontsize=15, weight="bold", y=0.96)
fig.savefig("paper_figures/Graphical_Abstract.png", dpi=200, bbox_inches="tight")
print("Saved paper_figures/Graphical_Abstract.png")
