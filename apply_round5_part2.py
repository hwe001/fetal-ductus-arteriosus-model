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

"""Part 2: fix Methods 2.6's medoid description, replace Results 3.3's flawed
Mahalanobis claim with the corrected LOO/shrinkage/percentile result, fix
references (Mielke/Benda, Montenegro), remove the numbered protocol
reference, and add full dataset/ethics documentation to Methods 2.1."""
import docx

PATH = "paper/A Coupled Reduced-Order Model of Fetal Ductus Arteriosus Flow.docx"
d = docx.Document(PATH)
paras = d.paragraphs


def set_text(para, new_text):
    if not para.runs:
        para.add_run(new_text)
        return
    para.runs[0].text = new_text
    for r in para.runs[1:]:
        r.text = ""


# --- Methods 2.6: replace medoid description with LOO/shrinkage description ---
for i, p in enumerate(paras):
    if "the same distance computed from the cohort's own medoid patient" in p.text:
        new_text = p.text.replace(
            "We compare this to the same distance computed from the cohort's own medoid patient (the single "
            "real patient whose vector minimizes total Mahalanobis distance to all others) to all other "
            "patients, giving an internally consistent benchmark for how “typical” a distance of this "
            "size is within the real population.",
            "Given the small sample (n=22 complete-case patients) relative to four correlated variables, we "
            "use Ledoit-Wolf shrinkage covariance estimation rather than the raw sample covariance. We "
            "benchmark the model's distance against an empirical, leave-one-out (LOO) reference distribution: "
            "for each patient, the population mean/covariance is re-estimated from the other 21 patients only, "
            "and that patient's own out-of-sample squared Mahalanobis distance is computed. The model's "
            "empirical percentile within this LOO distribution -- not a direct comparison to any single "
            "patient's distance -- is the measure of how typical the model is of the cohort."
        )
        set_text(p, new_text)
        break

# --- Results 3.3: replace the flawed claim with the corrected analysis ---
for i, p in enumerate(paras):
    if "The simulated index vector (PS=41.6, ED=10.5, S/D=3.95, PI=1.42) has a Mahalanobis distance" in p.text:
        new_text = (
            "Among the 22 complete-case patients, the correlation structure among the four indices was: "
            "PS-ED +0.70, PS-S/D -0.27, PS-PI -0.42, ED-S/D -0.60, ED-PI -0.47, and S/D-PI +0.11 -- notably, "
            "S/D and PI, both described clinically as pulsatility measures, are only weakly correlated with "
            "each other even within the real patient population. Using Ledoit-Wolf shrinkage covariance "
            "(shrinkage intensity 0.27 for the full cohort), the simulated index vector (PS=41.6, ED=10.5, "
            "S/D=3.95, PI=1.42) has a squared Mahalanobis distance of 0.32 from the cohort's mean. The "
            "leave-one-out (LOO) reference distribution of the 22 patients' own out-of-sample squared "
            "distances ranges from 0.09 to 50.79 (median 0.72); the model's distance sits at the 27th "
            "percentile of this distribution -- that is, 73% of the real patients in this cohort sit farther "
            "from an independent estimate of their own cohort than the model does. (For context only, not as "
            "a primary claim, since multivariate normality of this small clinical sample is unverified: a "
            "chi-squared(4) reference gives an upper-tail p=0.99 for the model's distance.) Univariate "
            "z-scores against the patient-level distribution were PS +0.03, S/D +0.10, ED -0.41, and PI -1.23: "
            "the pulsatility index is the only index more than one standard deviation from the patient-level "
            "mean, and even this is not an extreme deviation relative to the spread among real patients."
        )
        set_text(p, new_text)
        break

# --- References: fix Mielke/Benda [3], remove protocol [old 5]/renumber, fix Montenegro ---
for i, p in enumerate(paras):
    if p.text.startswith("[3] Mielke"):
        set_text(p, "[3] Mielke G, Benda N. Blood flow velocity waveforms of the fetal pulmonary artery and the "
                     "ductus arteriosus: reference ranges from 13 weeks to term. Ultrasound Obstet Gynecol. "
                     "2000;15:213-218. doi:10.1046/j.1469-0705.2000.00082.x")
    elif p.text.startswith("[5] Tang J, Zhang S, Ran S, Ho H. Quantifying"):
        # remove this paragraph entirely (de-numbered; mentioned as unpublished work in-text instead, Part 1)
        p._element.getparent().remove(p._element)
    elif p.text.startswith("[6] Muller"):
        set_text(p, p.text.replace("[6]", "[5]", 1))
    elif p.text.startswith("[7] Baker"):
        set_text(p, p.text.replace("[7]", "[6]", 1))
    elif p.text.startswith("[8] Szpinda"):
        set_text(p, p.text.replace("[8]", "[7]", 1))
    elif p.text.startswith("[9] Leao"):
        set_text(p, p.text.replace("[9]", "[8]", 1))
    elif p.text.startswith("[10] Vimpeli"):
        set_text(p, p.text.replace("[10]", "[9]", 1))
    elif p.text.startswith("[11] Montenegro"):
        set_text(p, "[10] Montenegro N, Ramos C, Matias A, Barros H. Variation of embryonic/fetal heart rate at "
                     "6-13 weeks' gestation. Ultrasound Obstet Gynecol. 1998;11(4):274-276. "
                     "doi:10.1046/j.1469-0705.1998.11040274.x")

d.save(PATH)
print("Saved after Mahalanobis rewrite and reference fixes.")

# --- verify ---
d2 = docx.Document(PATH)
for p in d2.paragraphs:
    if p.text.strip().startswith("["):
        print(p.text[:110])
