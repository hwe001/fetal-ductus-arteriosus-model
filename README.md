# A Coupled Reduced-Order Model of First-Trimester Fetal Ductus Arteriosus Flow

A Python implementation of a coupled, nonlinear resistance-inertance (RL)
lumped-parameter model of the normal fetal ductus arteriosus (DA) at
end-of-first-trimester gestation (~13.5 weeks) -- the continuous,
right-to-left shunting state, **not** the postnatal patent ductus arteriosus
(PDA) of prematurity. No parameters in the primary simulation were estimated
from this study's own Doppler cohort: fetal cardiac output, ventricular
output ratio, and ductal anatomy are taken from independent published
literature.

## Citation

This code accompanies the manuscript:

> J. Tang, S. Zhang, S. Ran, H. Ho. "A Coupled Reduced-Order Model of
> First-Trimester Fetal Ductus Arteriosus Flow." Manuscript in preparation /
> under review at the time this repository was published. Please check for
> the final published citation (journal, year, volume, DOI) and cite that
> version if available; otherwise cite this repository directly.

**If you use, adapt, or build on this code, please cite the paper above.**

## What's here

- `da_rlc_coupled_model.py` -- the core model: three simultaneously
  integrated ODEs (pulmonary compartment pressure, aortic compartment
  pressure, ductal flow with nonlinear resistance + inertance). Ductal
  compliance is folded into the two compartments (see the module docstring
  for why).
- `da_geometry.py` -- ductal length/diameter vs. gestational-age regressions
  from published human fetal morphometry (Szpinda et al. 2007; Leao et al.
  2015's narrowest-junction diameter).
- `two_compartment_model.py`, `pda_model.py`, `pda_model_v3_twocompartment.py`
  -- earlier model iterations, kept for the project's documented history
  (see `docs/model_plan_and_literature_data.md`); the current model is
  `da_rlc_coupled_model.py`.
- `multivariate_comparison.py` -- **the canonical script** for the
  manuscript's multivariate/Mahalanobis comparison (Sections 2.6, 3.3):
  standardized (z-scored, training-set-only) Ledoit-Wolf shrinkage
  covariance, leave-one-out reference distribution, and the paired-fold
  sensitivity check. Reproduces D²=1.99, 41st percentile, 59% of patients
  farther, LOO median=2.52.
- `superseded/` -- two earlier, FLAWED versions of the multivariate
  comparison (an unsupported "statistically indistinguishable from the
  medoid" claim, then an unstandardized shrinkage covariance that produced
  scale-biased results). Both refuse to run (raise `SystemExit` pointing to
  the canonical script) and are kept only as a transparent record of the
  errors found and corrected during review -- see
  `docs/model_plan_and_literature_data.md` Sections 21/23 for the full
  account. **Do not use their output.**
- `sensitivity_analysis.py`, `pi_factorial_study.py`, `joint_identifiability.py`,
  `waveform_diagnostics.py` -- the sensitivity/mechanism studies behind
  Results 3.4 (the pulsatility-index discrepancy).
- `uncertainty_propagation_v4.py` (and the earlier `uncertainty_propagation.py`)
  -- epistemic vs. biological-variability Monte Carlo propagation
  (Results 3.5).
- `cross_validation.py`, `calibrate_pda.py`, `finetune_base_frac.py` -- earlier
  calibration-era scripts, kept for documented project history.
- `make_waveform_figure.py`, `make_schematic_figure.py`,
  `make_timing_offset_figure.py`, `make_graphical_abstract_da.py`,
  `render_equations_da.py`, `insert_figures.py` -- manuscript figure/equation
  generation.
- `build_da_paper_docx.py`, `apply_round5_revisions.py`, `apply_round5_part2.py`
  -- the manuscript-building and revision scripts (python-docx).
- `docs/model_plan_and_literature_data.md` -- the full project history:
  every parameter's literature source and confidence level, all model
  iterations, every reviewer round's feedback and how it was addressed
  (25 sections). `docs/REPORT_FOR_REVIEWER.md` and
  `docs/PROGRESS_SINCE_REVIEWER_ROUND1-3.md` are the companion round-by-round
  response documents.
- `figures/` -- the manuscript's main figures (model schematic, simulated
  waveform, timing-offset sensitivity, graphical abstract).
- `data/validation_targets.json` -- the anonymized cohort's aggregate
  (mean/SD) Doppler indices used as the model's zero-fitting comparison
  targets. `data/network_geometry.json` -- a digitized vessel-network
  reconstruction used for geometry cross-checking (Section 2.3). Neither
  file contains patient-level data.
- `data/anonymized_doppler_data_SCHEMA_ONLY.csv` -- the COLUMN SCHEMA of the
  per-patient dataset used in `multivariate_comparison.py`, with no real
  values (see Data availability below).

## Requirements

Python 3.10+, `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`.
Figure/equation rendering with real LaTeX typesetting additionally requires
a local LaTeX installation (e.g. MiKTeX or TeX Live). Manuscript-building
scripts additionally require `python-docx`.

## Running

```bash
python da_rlc_coupled_model.py       # run the calibrated model, print indices
python sensitivity_analysis.py       # one-at-a-time parameter sensitivity
python pi_factorial_study.py         # the PI-mechanism factorial study
python uncertainty_propagation_v4.py # epistemic vs. biological Monte Carlo
python multivariate_comparison.py    # the canonical multivariate/Mahalanobis result
```

`multivariate_comparison.py` requires the real per-patient
`anonymized_doppler_data.csv` (see Data availability) to be placed in the
same directory as the script -- it will not run without it, by design (no
placeholder data is substituted).

## Results and logs (`results/`)

Outputs of the analysis scripts, kept so reported numbers can be checked without re-running:
calibration (`calibration_results*.csv`, `calibration_log*.txt`, `finetune_*`), cross-validation
(`cross_validation_*`; four folds, one row per fold, observed values are group means of 5-6 held-out
patients, no individual rows), sensitivity, joint identifiability, PI factorial study, and uncertainty
propagation (`uncertainty_*`). The scripts write these files to the working directory; here they are
collected in one folder. They are simulation outputs and cohort-level aggregates only. Two earlier
calibration stages (`calibration_results.csv`, `calibration_results_v2.csv`) belong to superseded model
versions and are kept for the record.

## Data availability

**No patient-level data is included in this repository.** The manuscript's
multivariate analyses (Sections 2.6, 3.3) use deidentified per-patient
Doppler indices (peak systolic velocity, end-diastolic velocity, S/D ratio,
pulsatility index -- no names or other identifiers) from a retrospective
cohort at the Chongqing Health Center for Women and Children. Their release
is subject to institutional ethics and data-governance approval, which had
not been obtained as of this repository's publication. Researchers seeking
access should contact the clinical corresponding author.

All OTHER data used in this study -- cohort-level aggregate statistics
(`data/validation_targets.json`), published literature regressions
(`da_geometry.py`), and a digitized anatomical network
(`data/network_geometry.json`) -- are included in full; none of it is
patient-level.

## License

See `LICENSE` (MIT for the code; does not extend to any patient data, none
of which is included here).
