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

"""Model schematic: the coupled nonlinear-RL lumped-parameter circuit,
alongside the anatomical geometry sources, for the manuscript's Methods
section (Figure 1)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.patches import ConnectionStyle

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.1)
ax.axis("off")

def box(x, y, w, h, text, fc="#eef3fb", ec="#2166ac", fontsize=10.5, weight="normal"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.08",
                        fc=fc, ec=ec, lw=1.6)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            weight=weight)

def arrow(xy1, xy2, text=None, color="#333333", style="-|>", rad=0.0, text_dy=0.18):
    a = FancyArrowPatch(xy1, xy2, arrowstyle=style, mutation_scale=16, color=color,
                         lw=1.6, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if text:
        mx, my = (xy1[0] + xy2[0]) / 2, (xy1[1] + xy2[1]) / 2
        ax.text(mx, my + text_dy, text, ha="center", va="bottom", fontsize=9, color=color)

# --- Top row: ventricular sources ---
box(0.3, 4.6, 1.6, 0.9, "RV", fc="#fde0dc", ec="#b2182b", weight="bold")
box(8.1, 4.6, 1.6, 0.9, "LV", fc="#fde0dc", ec="#b2182b", weight="bold")

# --- Compartments ---
box(0.1, 2.5, 2.6, 1.3, "Pulmonary\ncompartment\n$P_{pa}(t)$, $C_{pa}$", fc="#eef3fb", ec="#2166ac")
box(7.3, 2.5, 2.6, 1.3, "Aortic\ncompartment\n$P_{ao}(t)$, $C_{ao}$", fc="#eef3fb", ec="#2166ac")

# --- DA element (center) ---
box(3.6, 2.55, 2.8, 1.2, "Ductus arteriosus\nnonlinear R + L\n$Q_{da}(t)$", fc="#fff4d6", ec="#b8860b", weight="bold")

# --- Drains ---
box(0.1, 0.9, 2.6, 0.8, "Pulmonary vascular bed\n$R_{pulm}$", fc="#f5f5f5", ec="#666666", fontsize=9.5)
box(7.3, 0.9, 2.6, 0.8, "Systemic vascular bed\n$R_{sys}$", fc="#f5f5f5", ec="#666666", fontsize=9.5)

# --- Arrows: RV -> PA compartment, LV -> Ao compartment ---
arrow((1.1, 4.6), (1.4, 3.8), r"$Q_{RV}(t)$")
arrow((8.9, 4.6), (8.6, 3.8), r"$Q_{LV}(t)$")

# --- Arrows: compartments -> DA (both directions conceptually, draw one bidirectional-look) ---
arrow((2.7, 3.15), (3.6, 3.15), color="#b8860b")
arrow((6.4, 3.15), (7.3, 3.15), color="#b8860b")

# --- Arrows: compartments -> vascular beds ---
arrow((1.4, 2.5), (1.4, 1.7), color="#666666")
arrow((8.6, 2.5), (8.6, 1.7), color="#666666")

# --- ODE box at bottom center ---
ax.text(5.0, 0.35,
        r"$C_{pa}\dot P_{pa} = Q_{RV} - Q_{da} - P_{pa}/R_{pulm}$"
        "\n"
        r"$C_{ao}\dot P_{ao} = Q_{LV} + Q_{da} - P_{ao}/R_{sys}$"
        "\n"
        r"$L_{da}\dot Q_{da} = (P_{pa}-P_{ao}) - R_{da}Q_{da}|Q_{da}|$",
        ha="center", va="center", fontsize=9.5, family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#999999"))

ax.text(5.0, 5.85, "Coupled nonlinear-RL model of the fetal ductus arteriosus",
        ha="center", va="center", fontsize=13, weight="bold")

fig.tight_layout()
fig.savefig("paper_figures/Figure_model_schematic.png", dpi=200)
print("Saved paper_figures/Figure_model_schematic.png")
