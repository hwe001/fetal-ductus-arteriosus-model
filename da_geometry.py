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
Ductus arteriosus geometry vs. gestational age, from Szpinda et al. (2007),
Ann Anat 189:47-52 (n=131 human fetuses, spontaneous abortion/stillbirth
specimens; regressions valid for GA=15-34 weeks). See
model_plan_and_literature_data.md Section 2.2 for the cross-check against the
independent cmgui_model reconstruction, and Section 14 for the geometry/
measurement audit (reviewer round 2, Step 2) that added the Leao et al.
(2015) "diameter of the ductus base at the aorta" below.

IMPORTANT CAVEAT (Section 14 audit finding): Szpinda (2007) explicitly
measured EXTERNAL diameter on postmortem, formalin-fixed, dissected
specimens under a stereoscope -- NOT the internal/luminal diameter that
determines flow velocity via cross-sectional area. `da_diameter_mm()` below
was, until this audit, used directly as if it were the internal/functional
diameter with NO wall-thickness correction -- a real, previously
undocumented modeling gap (the plan doc's Section 2.2 text describing an
"internal radius after a wall-thickness allowance" was descriptive only;
the code never implemented it). No DA-specific wall-thickness value was
found in either Szpinda (2007) or Leao et al. (2015) -- both are presumably
external/postmortem measurements. Leao's diameter is at least measured
SPECIFICALLY at the narrowest point (the aortic-junction "base," where the
DA's known constriction is located, and where Doppler PS/ED are also
clinically sampled), not an along-length average like Szpinda's -- see
`da_diameter_base_at_aorta_mm()`.
"""
import numpy as np

GA_FIT_RANGE_WEEKS = (15.0, 34.0)


def da_length_mm(ga_weeks):
    """Szpinda regression: length(mm) = -3.0726 + 0.4381*GA(weeks), r=0.98."""
    return -3.0726 + 0.4381 * ga_weeks


def da_diameter_mm(ga_weeks):
    """Szpinda regression: EXTERNAL diameter(mm) = 0.2072 + 0.0935*GA(weeks),
    r=0.90 -- an along-length AVERAGE, not specific to the narrowest point."""
    return 0.2072 + 0.0935 * ga_weeks


def da_diameter_base_at_aorta_mm(ga_weeks, use_binned_value_below_ga=20.0):
    """
    Leao et al. (2015), J Morphol Sci 32(3):170-175 (n=44 human fetuses,
    9-26 weeks GA, postmortem dissection) -- diameter of the ductus SPECIFICALLY
    at its base/junction with the aorta (the narrowest point, parameter "G" in
    their Table 2), NOT an along-length average like Szpinda's. Regression
    (all ages): G(mm) = -0.2658 + 0.1011*GA(weeks), R=0.48, p<0.0001 (noisier
    fit than Szpinda's general diameter, R=0.90 -- a single narrow-point
    measurement is less reproducible across specimens than an average).

    For GA<20wk (covering this project's 13.5wk cohort), the DIRECTLY-MEASURED
    age-binned value is used instead of the regression line by default (more
    representative for a narrow GA window than an extrapolated fit spanning
    9-26 weeks): 9-14wk bin (n=10): 0.93+-0.55mm; 15-20wk bin (n=27):
    1.49+-0.71mm. Both are still presumably EXTERNAL/postmortem measurements
    like Szpinda's (no internal/luminal distinction stated) -- so this value
    is a better-located, not necessarily wall-thickness-corrected, estimate.
    """
    if use_binned_value_below_ga is not None and ga_weeks < use_binned_value_below_ga:
        if 9.0 <= ga_weeks < 14.0:
            return 0.93
        elif 14.0 <= ga_weeks < 20.0:
            return 1.49
    return max(-0.2658 + 0.1011 * ga_weeks, 0.05)


def da_geometry_cm(ga_weeks, taper_ratio=1.15):
    """
    Returns (L_cm, r_pa_cm, r_ao_cm): vessel length and radii at the two ends.
    Szpinda's diameter regression gives a single (mean) calibre per GA, not a
    taper profile. The taper here (wider at the PA end, narrower at the
    aortic-junction end) is a qualitative feature confirmed independently by
    the cmgui_model reconstruction (radius ratio ~1.4mm:1.0mm, i.e. ~1.4x,
    across the DA -- see model_plan_and_literature_data.md) and by both
    Szpinda's and Setchi's descriptions of a constriction where the DA joins
    the aorta. taper_ratio=1.15 is a DAMPENED version of that schematic ratio
    (not fit to it directly, since the cmgui model is topological/schematic,
    not metrically calibrated) -- r_pa/r_ao = taper_ratio, geometric mean
    equal to Szpinda's regression value, so the regression's literature-
    averaged calibre is preserved as the vessel's characteristic radius.
    """
    if ga_weeks is not None and not (GA_FIT_RANGE_WEEKS[0] - 2 <= ga_weeks <= GA_FIT_RANGE_WEEKS[1]):
        raise ValueError(
            f"GA={ga_weeks} weeks is far outside Szpinda's fitted range "
            f"{GA_FIT_RANGE_WEEKS} -- regression not validated there."
        )
    L_mm = da_length_mm(ga_weeks)
    d_mm = da_diameter_mm(ga_weeks)
    r_mean_mm = d_mm / 2.0
    r_pa_mm = r_mean_mm * np.sqrt(taper_ratio)
    r_ao_mm = r_mean_mm / np.sqrt(taper_ratio)
    return L_mm / 10.0, r_pa_mm / 10.0, r_ao_mm / 10.0


if __name__ == "__main__":
    for ga in (13.5, 15, 20, 24, 34):
        try:
            L_cm, r_pa, r_ao = da_geometry_cm(ga)
            print(f"GA={ga:5.1f}wk: L={L_cm*10:.2f}mm  r_pa={r_pa*10:.3f}mm  r_ao={r_ao*10:.3f}mm "
                  f"(diam_pa={2*r_pa*10:.2f}mm, diam_ao={2*r_ao*10:.2f}mm)")
        except ValueError as e:
            print(ga, "->", e)
