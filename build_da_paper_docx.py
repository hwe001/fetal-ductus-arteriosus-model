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
Builds the manuscript draft for the fetal ductus arteriosus (DA) coupled
reduced-order hemodynamic model. Mirrors the sibling CoA project's build
script (build_coa_paper_docx.py): numbered in-text citations in order of
first appearance, a matching numbered reference list, a Graphical Abstract
section, a Novelty File (<=100 words), an unstructured abstract with no
citations, and numbered display equations in Methods (unnumbered inline
equations in the Introduction, per journal convention).

This is a FETAL ductus arteriosus study -- NOT "PDA" (patent ductus
arteriosus, the postnatal pathological condition). Never use that phrase
unqualified anywhere in this document.
"""
import os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT

OUT_DIR = "paper"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "A Coupled Reduced-Order Model of Fetal Ductus Arteriosus Flow.docx")

doc = docx.Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(11)

# ---------------------------------------------------------------------------
# Numbered-citation bookkeeping
# ---------------------------------------------------------------------------
_citation_order = []
_citation_map = {}


def cite(*keys):
    nums = []
    for key in keys:
        if key not in _citation_map:
            _citation_order.append(key)
            _citation_map[key] = len(_citation_order)
        nums.append(_citation_map[key])
    nums = sorted(set(nums))
    return "[" + ",".join(str(n) for n in nums) + "]"


refs = {
    "tangstub": "Tang J, Zhang S, Ran S, Ho H. Quantifying the blood flow and shear stress "
                "for the ductus arteriosus. Unpublished study protocol / draft.",
    "vimpeli2009": "Vimpeli T, Chaoui R, Hartung J, Kohl T. Fetal cardiac output and its "
                   "distribution to the placenta at 11-20 weeks of gestation. Ultrasound "
                   "Obstet Gynecol. 2009;33(3):265-271.",
    "szpinda2007": "Szpinda M, Szwesta A, Szpinda E. Morphometric study of the ductus "
                    "arteriosus during human development. Ann Anat. 2007;189(1):47-52.",
    "leao2015": "Leao SC, Queiroz AAF, Souto MJS, Almeida RO, Maciel DC, Rodrigues TMA. "
                "A morphometric study of ductus arteriosus and its implications for "
                "implant of occlusive devices. J Morphol Sci. 2015;32(3):170-175.",
    "montenegro1998": "Montenegro N, Matias A, Areias JC, Castedo S, Barros H. Variation "
                       "of embryonic/fetal heart rate at 6-13 weeks' gestation. Ultrasound "
                       "Obstet Gynecol. 1998 [volume/pages NOT independently verified in "
                       "this project -- PMID 9618852 only; VERIFY BEFORE SUBMISSION].",
    "rudolph1979": "Rudolph AM. Fetal and neonatal pulmonary circulation. Annu Rev "
                    "Physiol. 1979;41:383-395.",
    "crossley2009": "Crossley KJ, Allison BJ, Polglase GR, Morley CJ, Davis PG, Hooper "
                     "SB. Dynamic changes in the direction of blood flow through the "
                     "ductus arteriosus at birth. J Physiol. 2009;587(19):4695-4704.",
    "mielke2000": "Mielke G, Benda N. Blood flow velocity waveforms of the fetal "
                  "pulmonary artery and the ductus arteriosus: reference ranges from 13 "
                  "weeks to term. Ultrasound Obstet Gynecol. 2000 [volume/pages NOT "
                  "independently verified in this project -- VERIFY BEFORE SUBMISSION].",
    "setchi2013": "Setchi A, Mestel AJ, Siggers JH, Parker KH, Tan MW, Wong K. "
                  "Mathematical model of flow through the patent ductus arteriosus. "
                  "J Math Biol. 2013;67(6-7):1487-1506.",
    "muller2017": "Muller LO, Clarke R, Ho H. Fast blood-flow simulation for large "
                  "arterial trees containing thousands of vessels. Comput Methods "
                  "Biomech Biomed Engin. 2017;20(2):160-170.",
    "baker2020": "Baker N, Clarke R, Ho H. A coupled one dimension and transmission line "
                 "model for arterial flow simulation. Int J Numer Methods Biomed Eng. "
                 "2020;36(4):e3327.",
}


def h(text, level=1):
    doc.add_heading(text, level=level)


def p(text, bold=False, italic=False, align=None):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    if align:
        para.alignment = align
    return para


def bib(number, text):
    para = doc.add_paragraph(f"[{number}] {text}")
    para.paragraph_format.left_indent = Inches(0.3)


_eq_counter = [0]
EQ_IMG_DIR = "paper_figures/equations"
DISPLAY_EQ_HEIGHT = Inches(0.26)
INLINE_EQ_HEIGHT = Pt(11.5)


def eq(key):
    _eq_counter[0] += 1
    n = _eq_counter[0]
    para = doc.add_paragraph()
    para.paragraph_format.tab_stops.add_tab_stop(Inches(6.3), WD_TAB_ALIGNMENT.RIGHT)
    para.add_run().add_picture(f"{EQ_IMG_DIR}/{key}.png", height=DISPLAY_EQ_HEIGHT)
    para.add_run(f"\t({n})")
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return n


def p_inline_eq(before, key, after):
    para = doc.add_paragraph()
    para.add_run(before)
    para.add_run().add_picture(f"{EQ_IMG_DIR}/{key}.png", height=INLINE_EQ_HEIGHT)
    para.add_run(after)
    return para


# ---------------------------------------------------------------------------
# Title / authors
# ---------------------------------------------------------------------------
title = doc.add_paragraph()
title_run = title.add_run(
    "A Coupled Reduced-Order Model of Fetal Ductus Arteriosus Flow: Anatomical "
    "Convergence on Junctional Diameter and the Limits of Population-Averaged "
    "Doppler Validation"
)
title_run.bold = True
title_run.font.size = Pt(15)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

p("J. Tang¹, S. Zhang², S. Ran¹, H. Ho²", align=WD_ALIGN_PARAGRAPH.CENTER)
p("¹Department of Ultrasound, Chongqing Health Center for Women and Children, "
  "Chongqing, China", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
p("²Auckland Bioengineering Institute, The University of Auckland, Auckland, "
  "New Zealand", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

# ---------------------------------------------------------------------------
# Abstract
# ---------------------------------------------------------------------------
h("Abstract")
p(
    "The fetal ductus arteriosus (DA) shunts right ventricular output past the "
    "high-resistance pulmonary bed into the descending aorta, and its Doppler "
    "velocity indices are measured routinely in obstetric ultrasound -- yet no "
    "prior computational hemodynamic model has reproduced these indices from "
    "independently sourced anatomy and flow, as distinct from the "
    "well-studied postnatal condition of a persistently patent DA. We built a "
    "coupled reduced-order (lumped-parameter) model of the fetal DA at "
    "end-of-first-trimester gestation (~13.5 weeks): three simultaneously "
    "integrated ordinary differential equations represent the pulmonary and "
    "aortic compartments and a nonlinear resistance-inertance (RL) element "
    "for the DA itself, driven by literature-sourced fetal cardiac output and "
    "right-to-left-ventricular output ratio, and by ductal geometry taken "
    "directly from published human fetal morphometry -- with no parameter "
    "fitted to this study's own Doppler measurements. Peak systolic velocity "
    "was reproduced to within 1% of a 23-fetus cohort's measured value using "
    "this zero-fitting parameterization. The diameter at the ductal-aortic "
    "junction required to match this velocity (a ratio of 0.68 relative to a "
    "commonly used along-length-average external diameter regression) agreed, "
    "to within 0.2 percentage points, with an independent published "
    "measurement taken specifically at that narrowest junctional point -- "
    "external, fixed-specimen anatomy distinct from, and not previously "
    "cross-checked against, in vivo Doppler-implied caliber. Because the "
    "cohort's pulsatility index (PI) and systolic/diastolic (S/D) ratio are "
    "per-patient nonlinear ratios, we show that comparing one representative "
    "simulated waveform against separately averaged marginal targets is "
    "statistically inconsistent by construction (mean(PS)/mean(ED) does not "
    "equal mean(S/D)), and instead compare the simulated index vector against "
    "the cohort's multivariate distribution: its Mahalanobis distance from "
    "the patient population is statistically indistinguishable from that of "
    "the cohort's own most representative patient. The pulsatility index "
    "alone remains a specific, unresolved discrepancy; a systematic "
    "mechanism study rules out ductal inertance and shows that no tested "
    "single mechanism (compliance, resistance baseline, ejection duration, "
    "or right/left-ventricular relative timing) corrects it without "
    "degrading the other indices, indicating that representing a "
    "heterogeneous patient population with one synchronized-ventricle "
    "input is an incomplete description of the boundary physiology. We "
    "further found no applicable human first-trimester reference for local "
    "ductal pressure gradients -- the commonly cited ~5 mmHg figure derives "
    "from late-gestation fetal lamb instrumentation -- and withdraw it as a "
    "quantitative target rather than fit the model to it. This study "
    "demonstrates that independently sourced cardiac output and junctional "
    "anatomy reproduce fetal DA peak systolic velocity without Doppler "
    "calibration, identifies narrowest-junction diameter as the principal "
    "determinant of velocity magnitude, and identifies the specific respect "
    "in which representing patient-level waveform heterogeneity with a "
    "single synchronized-ventricle model remains incomplete."
)

# ---------------------------------------------------------------------------
# Graphical Abstract / Novelty File
# ---------------------------------------------------------------------------
h("Graphical Abstract")
p("[Insert three-panel figure: (1) coupled compartment/DA schematic; "
  "(2) simulated velocity waveform vs. cohort Doppler target; "
  "(3) independent anatomical (Leao et al.) vs. Doppler-fit diameter-ratio "
  "convergence.]", italic=True)

h("Novelty File")
p(
    "This is the first computational hemodynamic model of the normal fetal "
    "ductus arteriosus parameterized entirely from independent literature "
    "(cardiac output, ventricular output ratio, junctional anatomy) rather "
    "than fitted to the Doppler data it is compared against. It reproduces "
    "peak systolic velocity to within 1%, and its Doppler-fit junctional "
    "diameter independently converges with a published anatomical "
    "measurement. It also demonstrates that clinically reported cohort mean "
    "indices (S/D, PI) cannot all be reproduced by one representative "
    "waveform, a statistical constraint not previously articulated for "
    "Doppler index validation, and resolves it with a multivariate "
    "comparison against the patient-level distribution."
)

doc.add_page_break()

# ---------------------------------------------------------------------------
# Introduction
# ---------------------------------------------------------------------------
h("1. Introduction")

p(
    f"During fetal life, the ductus arteriosus (DA) connects the main "
    f"pulmonary artery to the descending aorta, shunting right ventricular "
    f"output away from the fluid-filled, high-resistance pulmonary "
    f"vascular bed and into the systemic circulation "
    f"{cite('rudolph1979')}. This right-to-left flow is continuous, not "
    f"only systolic, and reverses only after birth as pulmonary vascular "
    f"resistance falls {cite('crossley2009')}. Doppler ultrasound of the "
    f"DA -- peak systolic velocity (PS), end-diastolic velocity (ED), the "
    f"systolic/diastolic ratio (S/D), and the pulsatility index (PI) -- is "
    f"measured routinely in obstetric practice and has published reference "
    f"ranges from as early as 13 weeks' gestation {cite('mielke2000')}. "
    f"These four indices are related by definition for any single measured "
    f"waveform: "
)
p_inline_eq("", "sd_ratio", ",  ")
p_inline_eq("", "ri_formula", ",  and  ")
p_inline_eq("", "pi_formula",
            ", where TAMX is the time-averaged maximum velocity over the "
            "cardiac cycle.")

p(
    f"Despite this clinical familiarity, computational hemodynamic "
    f"modelling of the DA is sparse and has focused almost entirely on the "
    f"postnatal condition in which the duct pathologically fails to close "
    f"-- patent ductus arteriosus (PDA) of prematurity -- where pressure "
    f"reverses after birth and the modelling questions concern shunt "
    f"volume and its hemodynamic consequences for the neonate "
    f"{cite('setchi2013')}. The single prior DA-specific hemodynamic model "
    f"we are aware of {cite('setchi2013')} is built for this postnatal, "
    f"reversed-pressure regime and its parameterization does not transfer "
    f"to the fetal case. We are not aware of a prior computational model of "
    f"the normal FETAL DA -- the physiologically distinct, continuous "
    f"right-to-left shunting state -- parameterized against real Doppler "
    f"measurements. This is an important and unqualified distinction: this "
    f"study is not about patent ductus arteriosus of prematurity, and its "
    f"findings should not be applied to that postnatal, pathological "
    f"context."
)

p(
    f"This study completes a previously initiated protocol {cite('tangstub')} "
    f"whose stated aim was \"the first computational simulations for the "
    f"blood flow in [fetal ductus arteriosi], in conjunction with blood "
    f"flow measurements from ultrasound,\" using a retrospective cohort of "
    f"anonymous ultrasound scans from fetuses at the end of the first "
    f"trimester. Rather than fit a model's free parameters to reproduce "
    f"this cohort's Doppler indices -- the approach taken in earlier, "
    f"unpublished iterations of this work, and a design that cannot "
    f"distinguish a genuine physiological finding from an overfit one -- we "
    f"instead parameterize the model entirely from independent literature "
    f"on fetal cardiac output, right/left-ventricular output distribution, "
    f"and ductal anatomy, and report how well this zero-fitting model "
    f"reproduces the cohort's own measured indices. We further show that "
    f"comparing a single representative simulated waveform against this "
    f"cohort's separately averaged S/D and PI targets is not statistically "
    f"well posed, because both are per-patient nonlinear ratios, and "
    f"develop a multivariate comparison that resolves this."
)

doc.add_page_break()

# ---------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------
h("2. Methods")

h("2.1 Cohort and Doppler measurements", level=2)
p(
    f"Retrospective, anonymized ultrasound scans of fetuses at the end of "
    f"the first trimester (~13.5 weeks gestational age) were reviewed at "
    f"the Chongqing Health Center for Women and Children. Of 29 identified "
    f"records, 23 had a recorded peak systolic velocity, end-diastolic "
    f"velocity, and pulsatility index; 22 additionally had a recorded S/D "
    f"ratio (one record lacked this specific derived value). Triplicate "
    f"measurements per patient were averaged by the original clinical team, "
    f"with flagged outlier measurements corrected prior to our analysis. "
    f"No patient-identifying information is used or reported in this study. "
    f"Cohort means (±SD) were: PS 41.3±12.5 cm/s (n=23), ED "
    f"13.0±8.0 cm/s (n=23), S/D 3.85±1.00 (n=22), PI "
    f"2.15±0.63 (n=23)."
)
p(
    f"We verified the clinical index formulas above against a single "
    f"real machine-displayed exemplar available to us (a separate scan, "
    f"gestational age 24 weeks 0 days, not part of the validation cohort): "
    f"machine-reported PS, ED, and TAMX values reproduced the "
    f"machine's own displayed S/D, RI, and PI to 2-3 significant figures, "
    f"confirming that PI's denominator is TAMX (the time-averaged maximum, "
    f"or envelope, velocity) rather than an intensity-weighted mean -- "
    f"consistent with equation 3 above."
)

h("2.2 Model structure", level=2)
p(
    f"The DA is modelled as a lumped nonlinear resistance-inertance (RL) "
    f"element bridging two lumped compartments representing the main "
    f"pulmonary artery (fed by right-ventricular ejection) and the "
    f"descending aorta (fed by left-ventricular ejection). We deliberately "
    f"do not use a distributed one-dimensional wave-propagation "
    f"formulation, of the kind previously developed for large systemic "
    f"arterial trees using transmission-line theory {cite('muller2017', 'baker2020')}: "
    f"at this vessel's length (~2.8 mm at 13.5 weeks, see Section 2.3) and "
    f"the calibrated wave speed of the coupled system, the pressure-wave "
    f"transit time across the DA is under 0.5% of the cardiac cycle "
    f"period -- the vessel is acoustically short, and a full "
    f"wave-propagation treatment is not expected to capture physics that a "
    f"properly coupled lumped element does not. The three state variables "
    f"-- pulmonary arterial pressure P_pa, aortic pressure P_ao, and ductal "
    f"flow Q_da -- are integrated simultaneously (fourth-order Runge-Kutta, "
    f"RK4), so flow and pressure continuity are enforced together at both "
    f"ductal interfaces rather than solved in stages:"
)
eq("compartment_pa")
eq("compartment_ao")
eq("da_momentum")
p(
    f"Q_RV(t) and Q_LV(t) are prescribed right- and left-ventricular "
    f"ejection waveforms (Section 2.4); R_pulm and R_sys are the "
    f"pulmonary- and systemic-bed drainage resistances; C_pa and C_ao are "
    f"compartment compliances. The ductal term (equation 3) is a genuine "
    f"dynamical state with inertance L_da (giving physical phase lag, "
    f"unlike an instantaneous algebraic flow-pressure relation) and a "
    f"nonlinear orifice/Bernoulli-type loss R_da*Q_da*|Q_da|, appropriate "
    f"for a short constriction rather than a long thin (Poiseuille) tube. "
    f"We refer to this as a coupled nonlinear RL model: the DA element has "
    f"resistance and inertance only, with ductal compliance folded into "
    f"C_pa and C_ao rather than given its own state, keeping the number of "
    f"free parameters small. R_da and L_da are derived from orifice theory "
    f"and standard fluid inertance, not fitted:"
)
eq("r_da_formula")
eq("l_da_formula")
p(
    f"where C_d is the discharge coefficient (0.6-0.8, standard for a "
    f"sharp-edged constriction, not fitted), A_throat is the ductal "
    f"cross-sectional area at its narrowest (aortic-junctional) point "
    f"(Section 2.3), rho is blood density, and ell_DA is ductal length."
)
p(
    f"R_pulm and R_sys are both anchored to a single shared baseline "
    f"pressure (30 mmHg, an assumed representative fetal arterial "
    f"pressure level not chosen with reference to any target gradient), "
    f"with only the independently sourced flow split between the two "
    f"sides differing between them (Section 2.4). This is a deliberate "
    f"design choice: an earlier iteration of this model instead assumed "
    f"two independently chosen compartment pressures whose difference was "
    f"set to equal an assumed pressure-gradient target, which we found on "
    f"review to be circular -- any resulting \"gradient\" was a "
    f"restatement of the assumption, not an independent prediction. Under "
    f"the present, symmetric anchoring, any P_pa-P_ao difference that "
    f"emerges is a genuine consequence of the flow asymmetry (Section 2.4) "
    f"interacting with the ductal resistance, not a built-in result."
)

h("2.3 Ductal anatomy", level=2)
p(
    f"Ductal length was taken from a published regression against "
    f"gestational age (GA, weeks) from n=131 postmortem human fetal "
    f"specimens {cite('szpinda2007')}: length (mm) = -3.0726 + 0.4381*GA "
    f"(r=0.98), giving 2.84 mm at 13.5 weeks. The same source reports an "
    f"along-length-average external diameter regression (0.2072 + "
    f"0.0935*GA, r=0.90, giving 1.47 mm at 13.5 weeks); we found on review "
    f"that this project had, in an earlier iteration, used this value "
    f"directly as the internal (luminal) diameter governing flow velocity, "
    f"with no wall-thickness correction, despite {cite('szpinda2007')}'s "
    f"explicit methodology (formalin-fixed, dissected, externally "
    f"measured specimens) -- a modelling error we correct here."
)
p(
    f"A second, independent source {cite('leao2015')} (n=44 human fetuses, "
    f"9-26 weeks GA) reports diameter measured specifically at the "
    f"\"ductus base at the aorta\" -- the narrowest point at the "
    f"ductal-aortic junction, consistent with the constriction both "
    f"sources describe anatomically, and with where Doppler peak velocity "
    f"is clinically sampled. This source's directly measured (not "
    f"regression-extrapolated) value for its 9-14-week age bin (n=10) is "
    f"0.93±0.55 mm, and we use this as A_throat's diameter -- again an "
    f"external, fixed-specimen measurement, not a resolution of the "
    f"external-versus-internal-lumen distinction, but a better-located "
    f"one. The resulting throat-to-along-length-average diameter ratio "
    f"(0.679) was not chosen or tuned; see Section 3.2 for its independent "
    f"agreement with a value obtained by an entirely different route."
)

h("2.4 Flow and heart-rate parameterization", level=2)
p(
    f"Combined fetal cardiac output at 13.5 weeks was log-interpolated "
    f"between directly measured anchor points at 11 and 20 weeks "
    f"(9 and 121 mL/min respectively) from a directly measured cohort of "
    f"143 fetuses {cite('vimpeli2009')}, giving ~18.5 mL/min (an "
    f"interpolation between two real measurements, not itself a directly "
    f"measured value at 13.5 weeks). The right-to-left ventricular output "
    f"ratio at a comparable gestational age (~15 weeks) from the same "
    f"source is 1.32±0.28, used to split combined output into "
    f"Q_RV and Q_LV. Right ventricular output was further split between "
    f"the pulmonary bed and the ductal shunt using an 85% ductal-shunt "
    f"fraction, extrapolated from the qualitative near-term physiological "
    f"finding that only ~10-15% of right ventricular output perfuses the "
    f"fetal lungs {cite('rudolph1979')}; this specific fraction has not "
    f"been independently verified at 13.5 weeks. Fetal heart rate was set "
    f"to 150 beats per minute, following a directly measured decline from "
    f"145-175 bpm at 11-13 weeks toward ~150 bpm by 14 weeks in a cohort "
    f"of 143 fetuses {cite('montenegro1998')}. Ventricular ejection is "
    f"prescribed as a shaped pulse confined to a fraction of the cycle "
    f"(the systolic duration):"
)
eq("ejection_shape")
p(
    f"where phi is phase within the cycle, tau_s is systolic duration "
    f"(baseline 0.35), and p is a sharpness exponent (baseline 2); "
    f"angle brackets denote the cycle-average used for normalization so "
    f"that the prescribed mean flow equals the target Q_RV or Q_LV."
)

h("2.5 The pressure-gradient reference: investigated and withdrawn", level=2)
p(
    f"Fetal main pulmonary arterial pressure is commonly stated to exceed "
    f"aortic pressure by approximately 5 mmHg, a figure usually attributed "
    f"to {cite('rudolph1979')} and repeated in later fetal-circulation "
    f"physiology literature {cite('crossley2009')}. Applying a simplified "
    f"Bernoulli relation, "
)
p_inline_eq("", "bernoulli_simple",
            " (v in m/s, ΔP in mmHg), to this cohort's own peak velocity "
            "(~0.42 m/s) implies a locally compatible pressure difference "
            "of well under 1 mmHg, whereas a genuine 5 mmHg local gradient "
            "implies a velocity approximately 3-fold higher than observed "
            "in this cohort. These two figures cannot both be locally "
            "correct for the same structure.")
p(
    f"We traced the ~5 mmHg figure to its origin: {cite('rudolph1979')} is "
    f"a review article synthesizing a research program built on "
    f"chronically instrumented fetal LAMB preparations -- direct human "
    f"fetal cardiac catheterization is not ethically or technically "
    f"feasible at any gestational age -- and such preparations are "
    f"performed near-universally in the last third of gestation, "
    f"physiologically comparable to human late second or third trimester, "
    f"not to this study's first-trimester cohort. Secondary sources "
    f"present the figure as a general statement about relative pressure "
    f"levels between the two circulations rather than an isolated local "
    f"measurement across the DA specifically. We found no applicable human "
    f"first-trimester reference for a local ductal pressure gradient, and "
    f"note that the ethical and technical infeasibility of the "
    f"measurement makes this a durable evidence gap rather than a "
    f"correctable search failure. We therefore withdraw the ~5 mmHg figure "
    f"as a quantitative validation target for this model: it is presented "
    f"in Section 3 as context for the lamb/late-gestation literature only, "
    f"and the model's own emergent pressure difference is reported as an "
    f"unvalidated model output, not scored against it."
)

h("2.6 Multivariate comparison against the patient-level distribution", level=2)
p(
    f"S/D and PI are per-patient nonlinear ratios (equations 1 and 3): for "
    f"any single measured or simulated waveform, S/D is fully determined "
    f"once PS and ED are fixed. Consequently, the mean of S/D across "
    f"patients is not equal to the ratio of the patients' mean PS to mean "
    f"ED -- in this cohort's complete cases (n=22), the ratio of means is "
    f"3.02, while the mean of the per-patient S/D values is 3.85. No "
    f"single representative simulated waveform can simultaneously equal "
    f"three independently averaged marginal targets (mean PS, mean ED, "
    f"and mean S/D) that are themselves mutually inconsistent with one "
    f"waveform's own algebra. We therefore report, in addition to the "
    f"conventional marginal percentage errors, a multivariate comparison: "
    f"the four-dimensional (PS, ED, S/D, PI) vector from each of the 22 "
    f"complete-case patients defines a patient-level mean, covariance, "
    f"and correlation structure, against which the simulated vector's "
    f"Mahalanobis distance is computed,"
)
eq("mahalanobis")
p(
    f"where x-bar and Sigma are the patient-level sample mean and "
    f"covariance. We compare this to the same distance computed from the "
    f"cohort's own medoid patient (the single real patient whose vector "
    f"minimizes total Mahalanobis distance to all others) to all other "
    f"patients, giving an internally consistent benchmark for how "
    f"\"typical\" a distance of this size is within the real population."
)

h("2.7 Numerical methods, sensitivity, and uncertainty", level=2)
p(
    f"The coupled system was integrated by fourth-order Runge-Kutta to a "
    f"periodic steady state (default 4000 steps per cycle, 8 cycles). "
    f"Temporal resolution was confirmed converged across a 16-fold range "
    f"of step counts (500-8000 steps/cycle, results agreeing to the "
    f"fourth decimal place), and periodic (cycle-to-cycle) convergence was "
    f"under 0.001% by the eighth cycle; because this architecture has no "
    f"spatial mesh, spatial convergence does not apply. A one-at-a-time "
    f"factorial sensitivity study varied ductal inertance (0.1-2x its "
    f"theoretical value), pulmonary/aortic compliance (0.1-10x, jointly "
    f"and independently), the shared resistance baseline (15-50 mmHg, "
    f"preserving the independently sourced flow split), systolic duration "
    f"and ejection sharpness, and right/left-ventricular relative ejection "
    f"timing. A subsequent joint (two-parameter) sensitivity/response-"
    f"surface scan varied throat area and discharge coefficient together "
    f"(40 points); this and the one-at-a-time study are sensitivity "
    f"analyses, not a complete identifiability analysis, which would "
    f"additionally require parameter correlation or a likelihood-based "
    f"treatment. Uncertainty was propagated by Monte Carlo (150 samples "
    f"per analysis) in two distinct senses: epistemic uncertainty in the "
    f"population-mean parameter estimates (sampling each literature-"
    f"derived parameter from its own reported standard error of the mean), "
    f"and biological variability among individual fetuses (sampling from "
    f"the reported between-subject standard deviation, using a log-normal "
    f"rather than normal distribution for the strictly positive ductal "
    f"diameter to avoid permitting non-physical near-zero values in the "
    f"tail)."
)

doc.add_page_break()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
h("3. Results")

h("3.1 Zero-fitting reproduction of cohort Doppler indices", level=2)
p(
    f"With every parameter sourced independently as described in Section "
    f"2 -- no parameter fitted to this cohort's own Doppler measurements "
    f"-- the model's simulated DA velocity waveform (Figure 1) gave:"
)
table1 = doc.add_table(rows=5, cols=4)
table1.style = "Light Grid Accent 1"
hdr = table1.rows[0].cells
for i, txt in enumerate(["Index", "Simulated", "Cohort target", "Relative error"]):
    hdr[i].text = txt
rows_data = [
    ["PS (cm/s)", "41.6", "41.3", "+0.6%"],
    ["ED (cm/s)", "10.5", "13.1", "-19%"],
    ["S/D", "3.95", "3.85", "+2.6%"],
    ["PI", "1.42", "2.15", "-34%"],
]
for i, row in enumerate(rows_data):
    cells = table1.rows[i + 1].cells
    for j, val in enumerate(row):
        cells[j].text = val

fig1 = doc.add_paragraph()
fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
fig1.add_run().add_picture("paper_figures/Figure_simulated_waveform.png", width=Inches(4.8))
fig1_cap = doc.add_paragraph()
fig1_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_run = fig1_cap.add_run(
    "Figure 1. Simulated fetal DA velocity waveform over one cardiac cycle, "
    "using literature-sourced parameters with no fitting to this cohort's "
    "own Doppler data."
)
cap_run.italic = True
cap_run.font.size = Pt(9.5)

p(
    f"Peak systolic velocity and the S/D ratio are reproduced within 3%; "
    f"end-diastolic velocity is 19% low; PI is 34% low. The model's own "
    f"emergent mean pressure difference between the pulmonary and aortic "
    f"compartments was 0.46 mmHg -- not scored against any target "
    f"(Section 2.5), but of the same order of magnitude implied by the "
    f"Bernoulli relation applied to this cohort's own observed velocity."
)

h("3.2 Independent anatomical convergence on junctional diameter", level=2)
p(
    f"Bisecting the ductal throat area to match peak systolic velocity "
    f"exactly (holding all other parameters at their independently "
    f"sourced values) requires a throat diameter equal to 0.68 times the "
    f"along-length-average external diameter regression of "
    f"{cite('szpinda2007')}. This ratio was obtained purely from fitting "
    f"this cohort's own Doppler velocity, with no anatomical information "
    f"used in its derivation. Independently, the ratio between "
    f"{cite('leao2015')}'s directly measured narrowest-junction diameter "
    f"(0.93 mm, 9-14-week bin) and {cite('szpinda2007')}'s along-length-"
    f"average diameter at 13.5 weeks (1.47 mm) is 0.679 -- obtained purely "
    f"from anatomical morphometry, with no Doppler information used in its "
    f"derivation. These two ratios, from entirely independent routes, "
    f"agree to within 0.2 percentage points. We regard this as the "
    f"strongest single finding of this study: an anatomically motivated, "
    f"independently sourced correction (using the narrowest-junction "
    f"measurement rather than an along-length average) closely predicts "
    f"the diameter this cohort's own Doppler velocity requires, without "
    f"having been fitted to it. We note that both diameter sources are "
    f"external, fixed-specimen measurements from formalin-fixed "
    f"postmortem material; neither resolves the distinct question of "
    f"external-versus-internal (luminal) diameter, for which we found no "
    f"ductus-specific wall-thickness measurement in the literature "
    f"searched."
)

h("3.3 Multivariate comparison against the patient population", level=2)
p(
    f"Among the 22 complete-case patients, the correlation structure "
    f"among the four indices was: PS-ED +0.70, PS-S/D -0.27, PS-PI -0.42, "
    f"ED-S/D -0.60, ED-PI -0.47, and S/D-PI +0.11 -- notably, S/D and PI, "
    f"both described clinically as pulsatility measures, are only weakly "
    f"correlated with each other even within the real patient population. "
    f"The simulated index vector (PS=41.6, ED=10.5, S/D=3.95, PI=1.42) has "
    f"a Mahalanobis distance of 1.80 from this patient-level distribution. "
    f"The cohort's medoid patient -- the single real patient whose own "
    f"vector is most central within the population -- has a mean distance "
    f"of 1.81 to all other patients: statistically indistinguishable from "
    f"the simulated model's distance. Equivalently, the simulated point is "
    f"farther from the cohort centroid than only 55% of the real patients "
    f"themselves are. Univariate z-scores against the patient-level "
    f"distribution were PS +0.03, S/D +0.10, ED -0.41, and PI -1.23: the "
    f"pulsatility index is the only index more than one standard deviation "
    f"from the patient-level mean, and even this is not an extreme "
    f"deviation relative to the spread among real patients."
)

h("3.4 The pulsatility-index discrepancy: a systematic mechanism study", level=2)
p(
    f"PI's shortfall reflects a specific, quantifiable waveform-shape "
    f"property. The target PI, together with the simulated PS and ED, "
    f"implies a time-averaged maximum velocity (TAMX) of ~14.5 cm/s; the "
    f"simulated waveform's actual TAMX is 21.9 cm/s -- the simulated "
    f"velocity remains too high through too much of the cycle, spending "
    f"46% of the cycle above half of peak systolic velocity, rather than "
    f"showing a sharper systolic peak over a lower sustained diastolic "
    f"level."
)
p(
    f"A systematic, one-factor-at-a-time study (Section 2.7) tested five "
    f"candidate mechanisms. Ductal inertance, varied across a 20-fold "
    f"range, changed PI by less than 0.05 and left TAMX unchanged -- "
    f"direct confirmation that inertance cannot sustain a persistent "
    f"mean-level effect over a periodic cycle (its cycle-average "
    f"contribution is exactly zero by construction), and this mechanism "
    f"is excluded. Pulmonary/aortic compliance produced large effects but "
    f"none that improved PI without substantially degrading ED and S/D "
    f"(e.g. halving both compliances brought PI to 2.16 while S/D rose to "
    f"10.6 and ED fell to 4.9). The shared resistance baseline, systolic "
    f"duration, and ejection sharpness each showed a similar pattern: PI "
    f"could be brought toward target, but only by moving PS and/or ED "
    f"substantially away from their own targets. The single largest-effect "
    f"factor was right/left-ventricular relative ejection timing -- "
    f"previously assumed, but never tested, to be perfectly synchronized. "
    f"A timing offset of 10-15% of the cardiac cycle (approximately 40-60 "
    f"ms at 150 beats per minute) moved PI from 1.42 through 2.71 to 3.23 "
    f"(Figure 2), the largest effect of any factor tested; end-diastolic "
    f"velocity and S/D moved away from target over the same range."
)

fig2 = doc.add_paragraph()
fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
fig2.add_run().add_picture("paper_figures/Figure_RVLV_timing_offset_sensitivity.png", width=Inches(6.2))
fig2_cap = doc.add_paragraph()
fig2_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_run2 = fig2_cap.add_run(
    "Figure 2. End-diastolic velocity, S/D ratio, and PI as a function of "
    "right/left-ventricular relative ejection timing offset -- a "
    "sensitivity finding, not a proposed mechanism (Section 3.4)."
)
cap_run2.italic = True
cap_run2.font.size = Pt(9.5)

p(
    f"We "
    f"present this strictly as a sensitivity finding, not as an "
    f"explanation: we are not aware of fetal evidence supporting an "
    f"interventricular mechanical delay of this specific magnitude, and a "
    f"delay large enough to correct PI simultaneously degrades the other "
    f"indices. Across every mechanism tested, including combined "
    f"shape-and-amplitude adjustments re-scaled to restore the peak-"
    f"systolic-velocity target, no configuration improved PI without a "
    f"comparable cost to end-diastolic velocity or S/D."
)

h("3.5 Uncertainty propagation", level=2)
p(
    f"Monte Carlo propagation (150 samples per analysis) of epistemic "
    f"uncertainty (in the estimated population-mean parameters) and "
    f"biological variability (among individual fetuses) gave:"
)
table2 = doc.add_table(rows=6, cols=4)
table2.style = "Light Grid Accent 1"
hdr2 = table2.rows[0].cells
for i, txt in enumerate(["Index", "Epistemic 5th-95th (median)", "Biological 5th-95th (median)", "Target"]):
    hdr2[i].text = txt
rows2 = [
    ["PS (cm/s)", "20.9-99.8 (46.0)", "9.4-180.2 (60.5)", "41.3"],
    ["ED (cm/s)", "3.7-26.1 (11.7)", "2.2-124.9 (14.4)", "13.1"],
    ["S/D", "1.82-15.2 (3.28)", "1.24-13.5 (2.85)", "3.85"],
    ["PI", "0.64-3.36 (1.29)", "0.23-3.15 (1.16)", "2.15"],
    ["Pressure gradient (mmHg)", "0.14-2.21 (0.52)", "0.02-16.8 (0.91)", "withdrawn (2.5)"],
]
for i, row in enumerate(rows2):
    cells = table2.rows[i + 1].cells
    for j, val in enumerate(row):
        cells[j].text = val
p(
    f"Biological variability gave meaningfully wider intervals than "
    f"epistemic uncertainty for PS, ED, and the (unscored) pressure "
    f"gradient, as physically expected -- not knowing the true "
    f"population-mean parameter precisely is a smaller source of "
    f"variation than the parameter genuinely differing between fetuses. "
    f"Peak systolic velocity's median and interval bracket its target "
    f"under both uncertainty framings, consistent with the zero-fitting "
    f"point estimate (Section 3.1) not being an isolated favorable value. "
    f"Both analyses' PI intervals span the target value, but the samples "
    f"reaching it do so only by substantially degrading S/D -- the same "
    f"trade-off identified in Section 3.4, now independently reconfirmed "
    f"under random sampling rather than deliberate search, and under both "
    f"uncertainty framings."
)

doc.add_page_break()

# ---------------------------------------------------------------------------
# Discussion
# ---------------------------------------------------------------------------
h("4. Discussion")

p(
    f"A coupled reduced-order fetal DA model using independently sourced "
    f"cardiac output and junctional anatomy reproduced this cohort's peak "
    f"systolic velocity without Doppler calibration. The model identified "
    f"narrowest-junction diameter as the principal determinant of "
    f"velocity magnitude, while discrepancies in the pulsatility index "
    f"exposed limitations of representing heterogeneous patient-level "
    f"waveform indices with a single synchronized ventricular input. We "
    f"do not claim that all four Doppler indices were validated: PS and "
    f"S/D reproduction, and the independent anatomical convergence of "
    f"Section 3.2, are genuine results obtained without fitting to this "
    f"study's own data; end-diastolic velocity and, specifically, the "
    f"pulsatility index remain incompletely explained."
)

p(
    f"The independent convergence between a Doppler-fit diameter ratio "
    f"and a directly measured anatomical diameter ratio (Section 3.2) is, "
    f"in our view, this study's strongest evidence of genuine mechanistic "
    f"content, precisely because it was not sought: the anatomical source "
    f"{cite('leao2015')} was identified only after the Doppler-fit ratio "
    f"had already been obtained by an unrelated calibration exercise. We "
    f"emphasize the distinction, not yet resolved in this study, between "
    f"external (fixed-specimen), internal (luminal), and narrowest-"
    f"junction diameter -- both anatomical sources used here are external "
    f"and postmortem, so this convergence corroborates the LOCATION (the "
    f"narrowest junctional point, not an along-length average) more than "
    f"it resolves the external-versus-internal magnitude question."
)

p(
    f"The pulsatility-index discrepancy is not, on the evidence of "
    f"Section 3.4, a matter of an untested parameter. Inertance is "
    f"excluded on direct mechanistic grounds; compliance, resistance "
    f"baseline, and ejection-waveform shape all show the same qualitative "
    f"pattern -- PI can be moved toward target, but only by moving other "
    f"indices away from theirs. The most informative single finding is "
    f"that ventricular timing, an assumption (perfect right/left "
    f"synchrony) never previously examined in this or, to our knowledge, "
    f"comparable models, has the largest effect of any factor tested. We "
    f"present this explicitly as a sensitivity finding, not a mechanism: "
    f"correcting PI by this route requires an interventricular delay for "
    f"which we have no supporting fetal evidence, and which itself "
    f"degrades end-diastolic velocity and S/D. We interpret the overall "
    f"pattern as evidence that a single synchronized-ventricle input is a "
    f"structurally incomplete description of the boundary physiology "
    f"needed to reproduce all patient-level waveform indices "
    f"simultaneously -- a specific, disclosed, and in our view "
    f"scientifically informative limitation, rather than a fitting "
    f"failure to be closed by further parameter search."
)

p(
    f"The withdrawal of the ~5 mmHg pressure-gradient reference (Section "
    f"2.5) reflects a genuine, permanent evidence gap for this specific "
    f"population: direct human fetal cardiac catheterization at any "
    f"gestational age is not ethically or technically feasible, and the "
    f"figure in question derives from late-gestation fetal lamb "
    f"instrumentation, a different species and developmental stage. We "
    f"regard reporting this gap, rather than fitting the model to a "
    f"reference that a basic consistency check shows is incompatible with "
    f"this cohort's own measured velocity scale, as itself a contribution "
    f"of this study."
)

h("4.1 Limitations", level=2)
p(
    f"Several limitations should be considered when interpreting these "
    f"results. Compartment compliances (C_pa, C_ao) are unsourced "
    f"placeholder values, chosen only to give a plausible time constant; "
    f"the sensitivity study (Section 3.4) shows these have substantial "
    f"effects on all four indices. The junctional-diameter measurement "
    f"{cite('leao2015')} is drawn from a small (n=10 in the relevant age "
    f"bin), noisy anatomical sample, not a large gestational-age-matched "
    f"cohort. This model represents one population-representative fetus, "
    f"not per-patient variation; no per-patient or cross-validated fit was "
    f"attempted, and the multivariate comparison (Section 3.3) compares a "
    f"single simulated waveform against a population distribution rather "
    f"than predicting individual outcomes. The right/left-ventricular "
    f"synchrony assumption (Section 3.4) is untested against direct fetal "
    f"evidence. The ductal shunt fraction (85% of right ventricular "
    f"output) is extrapolated from near-term, not first-trimester, "
    f"physiology. Finally, this study's Doppler measurements are "
    f"pre-computed triplicate-averaged indices, not raw digitized "
    f"waveforms; we could not independently confirm the original Doppler "
    f"sample-gate placement or insonation-angle correction for this "
    f"specific cohort."
)

h("4.2 Future work", level=2)
p(
    f"A joint, rather than one-at-a-time, sensitivity/response-surface "
    f"exploration of compliance, resistance baseline, and waveform shape "
    f"together may reveal combinations not visible in the factorial study "
    f"reported here. If fetal evidence for asynchronous right/left-"
    f"ventricular ejection timing emerges, incorporating it as a "
    f"physiologically grounded (not fitted) parameter would be a natural "
    f"extension. A per-patient or cross-validated extension of this "
    f"model, using individual anatomical measurements where available, "
    f"would test whether the population-representative model's "
    f"multivariate agreement (Section 3.3) extends to individual "
    f"prediction."
)

h("5. Conclusion", level=1)
p(
    f"A coupled reduced-order fetal ductus arteriosus model, parameterized "
    f"entirely from independently sourced cardiac output and junctional "
    f"anatomy, reproduced a 23-fetus cohort's peak systolic velocity "
    f"without Doppler calibration, and its Doppler-fit junctional-"
    f"diameter ratio independently converged with a directly measured "
    f"anatomical value. Discrepancies in the pulsatility index -- shown by "
    f"systematic mechanism testing not to be explained by ductal "
    f"inertance, and not correctable by any single tested mechanism "
    f"without degrading other indices -- expose a specific limitation of "
    f"representing a heterogeneous patient population with one "
    f"synchronized-ventricle waveform. We further show that comparing a "
    f"single representative waveform against separately averaged cohort "
    f"indices is not statistically well posed when those indices are "
    f"per-patient nonlinear ratios, and that a multivariate comparison "
    f"against the patient-level distribution is the appropriate "
    f"alternative. We do not claim that all Doppler indices were "
    f"validated; we report which were, which were not, and why."
)

# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------
doc.add_page_break()
h("References")
for key in _citation_order:
    n = _citation_map[key]
    bib(n, refs[key])

doc.save(OUT_PATH)

# ---------------------------------------------------------------------------
# Verification read-back
# ---------------------------------------------------------------------------
print(f"Saved: {OUT_PATH}")
print(f"Number of numbered equations: {_eq_counter[0]}")
print(f"Number of references: {len(_citation_order)}")

check = docx.Document(OUT_PATH)
n_paras = len(check.paragraphs)
n_tables = len(check.tables)
word_count = sum(len(par.text.split()) for par in check.paragraphs)
print(f"Paragraphs: {n_paras}, Tables: {n_tables}, Approx. word count: {word_count}")
headings = [par.text for par in check.paragraphs if par.style.name.startswith("Heading") or par.style.name == "Title"]
print("Headings found:")
for hd in headings:
    print(" -", hd)
