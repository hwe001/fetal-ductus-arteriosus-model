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

"""Apply reviewer round-5 revisions to the manuscript docx:
1. Shorten title
2. Rewrite abstract (~250 words, 4-element structure)
3. Fix "parameterized entirely from independent literature" -> defensible wording
4. Temper anatomical-convergence claims (post-hoc, formalin fixation, small n=10)
5. Replace flawed Mahalanobis claim with corrected LOO/shrinkage/percentile result
6. Soften pressure-gradient withdrawal language (remove "permanent"/"at any GA")
7. De-number the unpublished protocol reference; renumber [6]-[11] -> [5]-[10]
8. Fix Mielke/Benda and Montenegro references with verified details
"""
import re
import docx

PATH = "paper/A Coupled Reduced-Order Model of Fetal Ductus Arteriosus Flow.docx"
d = docx.Document(PATH)
paras = d.paragraphs


def set_text(para, new_text, italic=None):
    """Replace a paragraph's visible text, preserving the first run's formatting."""
    if not para.runs:
        para.add_run(new_text)
        return
    first = para.runs[0]
    first.text = new_text
    if italic is not None:
        first.italic = italic
    for r in para.runs[1:]:
        r.text = ""


def renumber_citations(text, mapping):
    def repl(m):
        nums = [n.strip() for n in m.group(1).split(",")]
        new_nums = [str(mapping.get(int(n), int(n))) for n in nums if int(n) in mapping and mapping[int(n)] is not None]
        return f"[{','.join(new_nums)}]" if new_nums else ""
    return re.sub(r"\[(\d+(?:,\s*\d+)*)\]", repl, text)


# citation renumbering map: old -> new (5 removed/None, 6-11 shift down by 1)
CITE_MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: None, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10}

# --- 1. Title ---
set_text(paras[0], "A Coupled Reduced-Order Model of First-Trimester Fetal Ductus Arteriosus Flow")

# --- 2. Abstract (~250 words, 4-element structure: purpose / model+cohort /
#     principal quantitative findings / restrained conclusion). Pressure-
#     reference history and PI-mechanism detail moved to main text only. ---
new_abstract = (
    "Purpose: no prior computational hemodynamic model reproduces Doppler velocity indices of the "
    "normal fetal ductus arteriosus (DA) -- the continuous, right-to-left shunting state -- as distinct "
    "from the well-studied postnatal condition of a persistently patent DA. "
    "Methods: we built a coupled reduced-order model of the fetal DA at end-of-first-trimester gestation "
    "(~13.5 weeks): three simultaneously integrated ordinary differential equations represent the pulmonary "
    "and aortic compartments and a nonlinear resistance-inertance element for the DA itself. No parameters "
    "in the primary simulation were estimated from this study's own 23-fetus Doppler cohort (retrospective, "
    "anonymized ultrasound, Chongqing Health Center for Women and Children); flow, cardiac-output split, and "
    "ductal length were taken from independent literature, and remaining parameters (compartment compliance, "
    "baseline pressure, discharge coefficient, ventricular waveform shape) are stated assumptions, not fitted "
    "values. "
    "Results: peak systolic velocity was reproduced within 1% of the cohort's measured value. The ductal "
    "throat diameter this required (0.680 relative to a commonly used along-length-average external-diameter "
    "regression) agreed to within 0.2 percentage points with an independently measured anatomical ratio "
    "(0.679) taken specifically at the narrowest ductal-aortic junction -- a striking, independent post-hoc "
    "corroboration, not a pre-specified validation. Because S/D and pulsatility index (PI) are per-patient "
    "nonlinear ratios, we compare the simulated index vector against the cohort's multivariate distribution "
    "rather than separately averaged marginal targets: its squared Mahalanobis distance from an independent, "
    "shrinkage-covariance cohort estimate falls at the 27th percentile of patients' own leave-one-out "
    "distances. PI itself remains 34% low; a systematic mechanism study excludes ductal inertance and finds "
    "no single tested mechanism corrects it without degrading other indices. "
    "Conclusion: independently sourced cardiac output and junctional anatomy reproduce fetal DA peak systolic "
    "velocity without Doppler calibration; PI's shortfall indicates that a single synchronized-ventricle "
    "waveform is an incomplete description of patient-level heterogeneity. Not all four Doppler indices are "
    "validated by this study."
)
set_text(paras[5], new_abstract)

# --- 3. Novelty File wording ---
novelty_text = paras[9].text
novelty_text = novelty_text.replace(
    "parameterized entirely from independent literature (cardiac output, ventricular output ratio, junctional anatomy)",
    "for which no parameters in the primary simulation were estimated from the study Doppler cohort (cardiac output, "
    "ventricular output ratio, and junctional anatomy were instead taken from independent literature)"
)
set_text(paras[9], novelty_text)

# --- 4. Introduction wording (para 17) ---
p17 = paras[17].text
p17 = p17.replace(
    "we instead parameterize the model entirely from independent literature on fetal cardiac output, "
    "right/left-ventricular output distribution, and ductal anatomy,",
    "no parameter in the primary simulation is estimated from this cohort's own Doppler measurements: fetal "
    "cardiac output, right/left-ventricular output distribution, and ductal anatomy are instead taken from "
    "independent literature (remaining parameters -- compartment compliance, baseline pressure, discharge "
    "coefficient, ventricular waveform shape -- are stated assumptions, not independently sourced),"
)
p17 = renumber_citations(p17, CITE_MAP)
# de-number the protocol citation entirely -- mention as unpublished internal work, not a numbered reference
p17 = p17.replace(
    "This study completes a previously initiated protocol whose stated aim was",
    "This study completes a previously initiated, unpublished internal study protocol (Tang, Zhang, Ran, Ho; "
    "Chongqing Health Center for Women and Children / Auckland Bioengineering Institute) whose stated aim was"
)
set_text(paras[17], p17)

# --- 5. Renumber citations in all other body paragraphs ---
for i in [12, 16, 26, 36, 37, 39, 43, 45, 60, 75, 79]:
    p = paras[i]
    new_text = renumber_citations(p.text, CITE_MAP)
    if new_text != p.text:
        set_text(p, new_text)

# --- 6. Temper anatomical-convergence claim (para 60) ---
p60 = paras[60].text
p60 = renumber_citations(p60, CITE_MAP)
p60 = p60.replace(
    "We regard this as the strongest single finding of this study: an anatomically motivated, independently "
    "sourced correction (using the narrowest-junction measurement rather than an along-length average) closely "
    "predicts the diameter this cohort's own Doppler velocity requires, without having been fitted to it.",
    "We regard this as a striking independent post-hoc corroboration, not a definitive anatomical validation: "
    "the anatomical source was identified only after the Doppler-fit ratio was already known (Section 4), both "
    "diameter measurements are external, fixed-specimen values from formalin-fixed postmortem material (fixation "
    "can itself alter tissue dimensions), and the anatomical estimate draws on a subgroup of only 10 specimens "
    "with substantial reported variability."
)
set_text(paras[60], p60)

# --- 7. Discussion para 75: reinforce the same tempering ---
p75 = paras[75].text
p75 = renumber_citations(p75, CITE_MAP)
p75 = p75.replace(
    "is, in our view, this study's strongest evidence of genuine mechanistic content, precisely because it was not sought:",
    "is, in our view, a striking post-hoc corroboration rather than a definitive validation, precisely because "
    "it was not pre-specified:"
)
set_text(paras[75], p75)

# --- 8. Fix pressure-gradient withdrawal language (para 77) ---
p77 = paras[77].text
p77 = p77.replace(
    "reflects a genuine, permanent evidence gap for this specific population: direct human fetal cardiac "
    "catheterization at any gestational age is not ethically or technically feasible, and the figure in "
    "question derives from late-gestation fetal lamb instrumentation, a different species and developmental stage.",
    "reflects an evidence gap for this specific population: we found no applicable direct human first-trimester "
    "measurement, and the commonly cited figure derives from a different species (fetal lamb) and a "
    "later gestational context."
)
set_text(paras[77], p77)

# --- 9. Fix independence wording + convergence tempering in Discussion para 74 ---
p74 = paras[74].text
p74 = p74.replace(
    "A coupled reduced-order fetal DA model using independently sourced cardiac output and junctional anatomy",
    "A coupled reduced-order fetal DA model, with no parameters in the primary simulation estimated from this "
    "study's own Doppler cohort,"
)
set_text(paras[74], p74)

# --- 10. Conclusion (para 83) ---
p83 = paras[83].text
p83 = p83.replace(
    "A coupled reduced-order fetal ductus arteriosus model, parameterized entirely from independently sourced "
    "cardiac output and junctional anatomy, reproduced",
    "A coupled reduced-order fetal ductus arteriosus model -- with no parameters in the primary simulation "
    "estimated from this study's own Doppler cohort -- reproduced"
)
p83 = p83.replace(
    "its Doppler-fit junctional-diameter ratio independently converged with a directly measured anatomical value.",
    "its Doppler-fit junctional-diameter ratio showed a striking, independent post-hoc convergence with a "
    "directly measured anatomical value (not a pre-specified validation)."
)
set_text(paras[83], p83)

d.save(PATH)
print("Saved after text-wording revisions (Mahalanobis section and references handled separately).")
