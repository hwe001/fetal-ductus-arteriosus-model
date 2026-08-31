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
Renders every equation in the fetal-DA manuscript as real LaTeX (matplotlib
text.usetex + local MiKTeX), one tightly-cropped transparent PNG per key,
for embedding in build_da_paper_docx.py. Mirrors the CoA project's
render_equations.py pattern.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["text.usetex"] = True
plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}\usepackage{amssymb}"
plt.rcParams["font.family"] = "serif"

OUT_DIR = "paper_figures/equations"
os.makedirs(OUT_DIR, exist_ok=True)

EQUATIONS = {
    "sd_ratio": (r"S/D = PS/ED", 11),
    "ri_formula": (r"RI = (PS-ED)/PS", 11),
    "pi_formula": (r"PI = (PS-ED)/\mathrm{TAMX}", 11),
    "bernoulli_simple": (r"\Delta P \approx 4v^2", 11),

    "compartment_pa": (r"C_{pa}\,\frac{dP_{pa}}{dt} = Q_{RV}(t) - Q_{da} - \frac{P_{pa}}{R_{pulm}}", 15),
    "compartment_ao": (r"C_{ao}\,\frac{dP_{ao}}{dt} = Q_{LV}(t) + Q_{da} - \frac{P_{ao}}{R_{sys}}", 15),
    "da_momentum": (r"L_{da}\,\frac{dQ_{da}}{dt} = (P_{pa}-P_{ao}) - R_{da}\,Q_{da}\left|Q_{da}\right|", 15),
    "r_da_formula": (r"R_{da} = \frac{\rho}{2\,(C_d\,A_{throat})^2}", 15),
    "l_da_formula": (r"L_{da} = \frac{\rho\,\ell_{DA}}{A_{throat}}", 15),
    "ejection_shape": (r"Q_{V}(t) = \bar{Q}_V\cdot\frac{\sin^{p}\!\left(\pi\,\phi/\tau_s\right)}{\left\langle\sin^{p}\!\left(\pi\,\phi/\tau_s\right)\right\rangle},\quad \phi<\tau_s", 14),
    "mahalanobis": (r"D_M(\mathbf{x}) = \sqrt{(\mathbf{x}-\bar{\mathbf{x}})^{\top}\Sigma^{-1}(\mathbf{x}-\bar{\mathbf{x}})}", 15),
}


def render(key, latex, fontsize):
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0, 0, f"${latex}$", fontsize=fontsize)
    path = f"{OUT_DIR}/{key}.png"
    plt.savefig(path, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    return path


if __name__ == "__main__":
    from PIL import Image
    for key, (latex, fontsize) in EQUATIONS.items():
        path = render(key, latex, fontsize)
        with Image.open(path) as im:
            w, h = im.size
        print(f"{key}: {path}  {w}x{h}px  aspect={w/h:.2f}")
    print(f"\nRendered {len(EQUATIONS)} equations to {OUT_DIR}/")
