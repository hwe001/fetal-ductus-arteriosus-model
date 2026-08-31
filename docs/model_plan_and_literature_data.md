# Fetal ductus arteriosus (DA) flow model: 1D transmission-line simulation

**Naming note (reviewer feedback, incorporated)**: this folder is named
`pda_1d_model` for historical reasons (it grew out of the "PDA" folder), but
the work itself is NOT about patent ductus arteriosus (PDA) -- the pathological
postnatal failure-to-close condition. It is a study of NORMAL FETAL ductus
arteriosus hemodynamics at ~13.5 weeks gestation. This distinction must be
explicit in the eventual paper's title, aims, and discussion (e.g. a title
along the lines of "A 1D Transmission-Line Model of Fetal Ductus Arteriosus
Flow" or similar -- NOT anything containing "PDA" or "patent ductus
arteriosus" unqualified, which would misleadingly imply the postnatal
pathological scenario). See Section 1 below for the full distinction from the
separate, already-drafted postnatal-PDA review paper that also lives in the
parent folder.

## 1. What this project actually is

This folder contains the makings of (at least) two distinct, previously-drafted papers that
got filed together but should NOT be conflated:

1. **"Biomechanics and Pharmacokinetics for Patent Ductus Arteriosus in Preterm Infants:
   Would in silico Modelling Help and How to Do It?"** (Tang, Ji, Ho, Ran) -- a
   near-complete REVIEW/perspective article surveying modelling approaches for
   *postnatal* PDA (the pathological failure-to-close scenario in preterm neonates,
   post-birth pressure reversal, pharmacological closure). No new model is built in it.
   Out of scope for this build -- left as-is.

2. **"Quantifying the blood flow and shear stress for the ductus arteriosus"**
   (Tang, Zhang, Ran, Ho) -- a skeleton stub (`blood flow simulation for the DA.docx`)
   with "Blah blah" placeholders but a concrete, real study design already defined:
   - Retrospective, anonymous ultrasound scans of **24 fetuses at the end of the first
     trimester** (~13-14 weeks GA), Chongqing Health Center for Women and Children
     (CHCWC), ethics-approved.
   - Explicit intended method: "a hemodynamic solver similar to Muller et al 4 ...
     solved from the transmission line theory" -- Muller, Clarke & Ho (2017),
     *Comput Methods Biomech Biomed Engin* 20:160-170, a direct precursor of
     Baker, Clarke & Ho (2020) (`cnm.3327`), whose Python port
     (`E:\Google Drive\Harvey Ho Paper\2020\coarctation_aorta\coa_1d_model\baker_1d_solver.py`)
     is already built, debugged, and published for the CoA project.
   - Aim stated verbatim: "the first computational simulations for the blood flow in
     DAs, in conjunction with blood flow measurements from ultrasound."

   **This project (`pda_1d_model/`) is about completing stub #2** -- i.e. normal
   *fetal* DA hemodynamics at ~13.5 weeks gestation (physiological right-to-left,
   pulmonary-to-aortic shunting from high fetal pulmonary vascular resistance),
   NOT the postnatal PDA-of-prematurity/closure scenario. These are physiologically
   opposite pressure regimes -- do not mix parameters between the two.

## 2. Real data already available

### 2.1 Doppler validation targets (anonymized)
`DA related values.xlsx` contains real per-patient DA Doppler measurements for this
exact 24-fetus cohort (peak systolic PS, end-diastolic ED, S/D ratio, PI; triplicate
measurements per patient, already averaged in the sheet's "Modified Data" section
with outliers flagged/adjusted by the original clinical authors).

**PII note**: the original sheet has identifiable Chinese patient names in column A.
Anonymized to `PatientNN` IDs in `anonymized_doppler_data.csv` (this folder). Patient
names must never be reproduced in any output, code, or paper text -- only the
anonymized numeric data is used from here on.

Cohort summary (`validation_targets.json`), n=24 with data (29 total incl. blanks for
patients with no DA measurement):
| Index | Mean | SD |
|---|---|---|
| PS (cm/s) | 41.32 | 12.49 |
| ED (cm/s) | 13.05 | 7.95 |
| S/D ratio | 3.85 | 1.00 |
| PI | 2.15 | 0.63 |

### 2.2 Geometry
Two independent geometry sources, cross-checked against each other:

- **Szpinda et al. (2007)**, *Ann Anat* 189:47-52 (`literature/Szpinda_et_al (2006)...pdf`,
  n=131 human fetuses, spontaneous abortion/stillbirth specimens) -- the literature
  source already cited in both drafts. Linear regressions vs. gestational age x (weeks),
  valid range x=15-34 weeks:
  - length (mm) = -3.0726 + 0.4381 x   (r=0.98, R²=0.96)
  - external diameter (mm) = 0.2072 + 0.0935 x   (r=0.90, R²=0.81)
  - volume (mm³) = 0.0007 x^3.3782   (r=0.94, R²=0.88)

  At x=13.5 weeks (end of first trimester; slightly below the fitted range's lower
  bound of 15 weeks -- a modest, explicitly-flagged extrapolation):
  length = 2.84 mm, external diameter = 1.47 mm -> internal radius ≈ 0.6-0.7 mm
  after a wall-thickness allowance (DA wall is muscular/thick relative to elastic
  systemic arteries -- see Mavrides et al. 2002 histology, in `literature/`, for the
  comparable ductus venosus, as a rough proxy for perinatal ductal wall structure).

- **`cmgui_model/artery.exelem` + `.exnode`**: a real, pre-existing 25-node/20-element
  1D centreline reconstruction (radius field per node) of the aortic arch + its three
  branches (innominate/carotid/subclavian, r≈0.9mm), the main pulmonary artery trunk +
  branch (r≈1.5mm), and the DA itself connecting them (elements 19-20, node chain
  2167->2177->2163), tapering 1.4mm -> 1.0mm (radius, at the narrowest point, node
  2177, consistent with Szpinda's / Setchi's noted constriction where DA joins the
  aorta) -> 1.6mm. Parsed into `network_geometry.json` in this folder.
  **Cross-check**: DA length from this reconstruction = 1.346+1.423 = 2.77 mm, vs.
  2.84 mm predicted by the Szpinda regression at 13.5 weeks -- within 2.5%, a good
  independent agreement. Diameter is somewhat larger in the reconstruction (~2mm at
  the widest) than Szpinda's regression predicts (1.47mm) -- expected, since this is
  a topological/schematic reconstruction (per the earlier fetal-arterial-circulation
  project's established precedent: geometry doesn't need to be metrically exact, only
  topologically sound enough to drive the simulation), not a metrically-calibrated
  patient-specific scan.

  **Modelling decision**: use the cmgui network for topology/figure purposes and as a
  qualitative sanity check (confirms the aortic-junction constriction and the
  relative PA/Ao/DA calibre ratios); use the Szpinda regression as the quantitative
  geometry source for the actual 1D solve, since it is gestational-age-parameterized
  and literature-averaged over 131 specimens (vs. one schematic reconstruction).

## 3. Modelling approach

Reuse `baker_1d_solver.py` UNCHANGED (already validated, debugged, and published for
the CoA project). The DA itself is modelled as the single 1D tube (matching the
already-intended "transmission line theory" method from the stub draft, and Baker's
own solver architecture, which is a single-tube-with-transmission-line-BC scheme):

- **Geometry**: `build_geometry(L, M, r0_func, k1, k2, k3, stiffness_scale)` with
  L = Szpinda length at 13.5 weeks, r0_func = Szpinda-regression radius (uniform or
  mildly tapered along the vessel to reflect the aortic-junction constriction seen
  in the cmgui reconstruction).
- **Inlet** (PA side): prescribed flow/pressure waveform representing the main
  pulmonary artery, at the fetal heart rate for this gestational age.
- **Outlet** (Ao side): transmission-line reflection coefficient `kappa` representing
  the descending-aorta/systemic-bed impedance, calibrated (as with CoA) rather than
  assumed.
- Stiffness law: Olufsen `Eh/r0 = k1*exp(k2*r0)+k3` as a first pass, same as CoA --
  BUT flag as a limitation that the DA wall is actively muscular (unlike a passive
  elastic systemic artery), so an independent stiffness scale factor may be needed
  (mirrors the CoA project's `EXTRA_STIFFEN_FACTOR` precedent) if a plain Olufsen law
  cannot reproduce the measured S/D and PI simultaneously.
- Validation: compute PS, ED, S/D, PI from the simulated DA velocity waveform the
  same way as the real Doppler measurements, compare against section 2.1's targets.

## 4. Literature parameters (search complete)

- **Fetal heart rate**: 145-175 bpm at 11-13 weeks, declining to ~150 bpm by 14 weeks
  (Montenegro et al. 1998, *Ultrasound Obstet Gynecol*, PMID 9618852). **Use 150 bpm**
  (T_period = 0.4 s) for this end-of-first-trimester cohort.
- **Fetal PA-Ao pressure gradient**: classic fetal physiology -- fetal main PA pressure
  runs **~5 mmHg above** aortic/systemic pressure throughout the cycle (Rudolph 1979;
  Reid & Thornburg 1990; Hooper 1998), which is what drives *continuous* (not just
  systolic) right-to-left flow through the DA -- consistent with our anonymized
  cohort's data showing positive (forward, PA->Ao) velocity at both peak-systole and
  end-diastole for nearly all patients (a few raw outliers were already flagged/
  corrected by the original clinical authors in the sheet's "Modified Data" pass).
  **Setchi et al. (2013)** (the one prior DA-specific hemodynamic model) is NOT a
  usable source for fetal pressures -- it models the postnatal (adult-pressure-regime)
  asymptomatic-PDA scenario, not fetal circulation; noted only as a postnatal-contrast
  reference, not used for parameterization here.
  **Gap**: no source found for the *absolute* fetal MAP at 13-14 weeks specifically
  (only the ~5mmHg PA-Ao gradient is well-sourced). Baseline p0 is therefore a
  flagged assumption (Section 5), not a directly-cited value.
- **Independent DA Doppler reference range** (for sanity-checking our own validation
  targets, NOT used to fit the model): Mielke & Benda (2000), *Ultrasound Obstet
  Gynecol*, "Blood flow velocity waveforms of the fetal pulmonary artery and the
  ductus arteriosus: reference ranges from 13 weeks to term" (n=222 normal fetuses,
  13-41 weeks) is the gold-standard reference-range paper for exactly this
  measurement and GA window (not held locally in `literature/` -- cite from the
  published record). Normal fetal DA PI has also been reported as 2.46+-0.52 and
  2.47+-0.30 in other sources -- our cohort's PI=2.15+-0.63 sits within ~1 SD,
  i.e. physiologically plausible.
- **Blood rho/mu**: no DA- or first-trimester-specific value found in the literature
  searched; reusing the CoA project's rho=1.05 g/cm^3, mu=0.035 poise as a carried-
  over, not DA-specific, assumption.
- **Additional real single-case cross-check** (`images/` folder, one clinical Doppler
  exam, CQ Women & Children's Hospital, GA=24w0d -- a later gestational age than the
  24-fetus first-trimester cohort, so used only as an order-of-magnitude sanity check,
  not a fit target; patient identifier redacted per PII policy): on-screen machine
  measurements PS=59.1 cm/s, ED=10.0 cm/s, S/D=5.91, PI=2.28, RI=0.83, fetal HR=146bpm.
  PI=2.28 and FHR=146bpm are both close to, respectively, our cohort's PI target
  (2.15+-0.63) and our assumed 150bpm (consistent with HR declining slightly with
  GA, Montenegro et al. 1998) -- an encouraging independent consistency check.

## 5. Modelling/calibration design (resulting from the above)

`baker_1d_solver.py`'s `simulate()` takes a single scalar `p0` and a *prescribed-flow*
inlet -- there is no explicit two-sided pressure boundary condition, so the ~5mmHg
PA-Ao gradient from Section 4 is NOT imposed directly. Instead:

- **Inlet (PA end) mean/pulsatile flow amplitude** is calibrated so the simulated
  peak-systolic velocity matches the cohort's PS target (41.3 cm/s) -- this is close
  to a direct fit (velocity = flow/area, area set by Szpinda geometry), not a genuine
  prediction.
- **Outlet reflection coefficient `kappa`** (representing the downstream aortic/
  systemic-bed impedance) and the **local DA wall stiffness scale** (DA wall is
  actively muscular, not a passive elastic systemic artery -- plain Olufsen systemic-
  artery constants are not expected to apply as-is) are jointly calibrated against
  the cohort's ED, S/D, and PI targets -- these depend on wave/compliance dynamics,
  not just the inlet amplitude, so matching them is a genuine (if still in-sample)
  test of the model, analogous to the CoA project's kappa/stiffness calibration.
- **Cross-check, not a fit target**: the resulting simulated mean pressure difference
  between the PA and Ao ends of the model is compared against the independent
  ~5mmHg literature value (Section 4) as a plausibility check on the calibrated
  parameter set.

## 6. Calibration results (first pass) -- an honest negative/partial finding

A 41-run sweep (`calibrate_pda.py`, results in `calibration_results.csv`) bisected
Q_MEAN against the PS target, then grid-searched KAPPA x STIFFNESS_SCALE x
Q_PULSE_FRAC against all four targets jointly. Confirmation run (N=150000, ~3.5
cycles) at the best-scoring point (q_mean=0.354 cm^3/s, kappa=-0.3,
stiffness_scale=0.02, q_pulse_frac=0.5):

| Index | Simulated (Ao end) | Target (cohort) | Rel. error |
|---|---|---|---|
| PS (cm/s) | 38.7 | 41.3 | -6% |
| ED (cm/s) | 13.9 | 13.1 | +6% |
| S/D | 2.79 | 3.85 | -28% |
| PI | 1.08 | 2.15 | -50% |

**PS and ED (the absolute velocity magnitudes) are matched well. S/D and PI (the
pulsatility/shape indices) are NOT** -- and this is a consistent, systematic
pattern across the ENTIRE grid, not a local optimum failure: every combination
tried lands on one of two failure modes -- low pulse fraction (0.5) gives
plausible PS/ED but S/D and PI too low (as above); high pulse fraction (1.1)
pushes PI up close to target but collapses ED toward zero and sends S/D to
10-20+ (e.g. PS=48.2, ED=2.5, SD=19.4, PI=2.19 at kappa=0, stiff=0.01,
pulse=1.1). No point in the grid balances all four simultaneously.

**Diagnosis**: the inlet flow waveform SHAPE (quarter-sine systolic upstroke +
exponential diastolic decay) was carried over unchanged from the CoA/adult-
aortic-flow project. That shape's diastolic branch decays smoothly toward a low
runoff value, which is the correct qualitative behaviour for a systemic artery
feeding a high-resistance vascular bed -- but the real fetal DA Doppler
waveform (see the actual clinical example in `../images/`, redacted patient ID)
instead shows a repeating series of relatively sharp systolic peaks over a
substantial, less-decayed diastolic shelf of CONTINUOUS forward flow (consistent
with the physiology: the ~5mmHg PA-over-Ao pressure excess, Section 4, persists
through diastole, unlike a systemic artery's diastolic runoff against elastic
recoil alone). Forcing our borrowed shape's amplitude up to chase the PI target
necessarily drives its diastolic minimum toward zero (since amplitude and
decay depth are coupled in this shape family), which is exactly the failure
mode observed.

**Also unresolved**: the calibrated point's simulated mean PA-Ao pressure
difference is only 0.16mmHg, vs. the ~5mmHg literature value (Section 4) -- a
30x discrepancy. This wasn't a fit target, but it's a real inconsistency worth
resolving alongside the waveform-shape fix, not a separate issue: a corrected
waveform shape with genuinely sustained diastolic forward flow will likely also
raise the simulated mean pressure gradient closer to the literature value,
since both come from the same underlying under-representation of sustained
diastolic driving pressure in the current inlet shape.

**Recommended next step** (not yet done): replace `_inlet_shape()` in
`pda_model.py` with a fetal-DA-appropriate shape -- e.g. a sharper, narrower
systolic peak on top of a flatter, less-decayed diastolic baseline (a
raised-sine or asymmetric-triangular pulse, rather than an exponential decay
toward near-zero) -- informed directly by the real waveform morphology visible
in the clinical example image, then re-run this same calibration sweep.

## 7. Waveform redesign (v2) -- partial fix, final calibrated model

Implemented the Section 6 recommendation: `pda_model.py`'s inlet is now a flat
diastolic BASELINE flow with a short, sharp systolic SPIKE added on top
(`BASE_FRAC` = fraction of mean flow carried by the baseline; the spike
carries the rest), replacing the old single-parameter shape that coupled
systolic height to diastolic decay depth. This directly targets the
mechanism identified in Section 6.

**Result: this fixes 3 of 4 indices, not all 4.** A joint sweep (Q_MEAN
bisected against PS; BASE_FRAC, KAPPA, STIFFNESS_SCALE grid-searched, then
BASE_FRAC fine-tuned with Q_MEAN re-bisected at each value -- see
`calibrate_pda.py` / `calibration_results_v2.csv` / `finetune_base_frac.py` /
`finetune_results.csv`) found a substantially better-balanced point:

| Index | v1 (old shape, best) | v2 (new shape, best) | Target |
|---|---|---|---|
| PS (cm/s) | 38.7 (-6%) | **41.5 (+0.4%)** | 41.32 |
| ED (cm/s) | 13.9 (+6%) | 10.0 (-23%) | 13.05 |
| S/D | 2.79 (-28%) | **4.15 (+8%)** | 3.85 |
| PI | 1.08 (-50%) | **2.07 (-4%)** | 2.15 |
| total score | 0.93 | **0.35** | (0=perfect) |

Final calibrated parameters (now the module defaults in `pda_model.py`):
Q_MEAN=0.232 cm^3/s, BASE_FRAC=0.65, KAPPA=-0.3, STIFFNESS_SCALE=0.01
(HR=150bpm, GA=13.5wk geometry unchanged from Section 2-3). Confirmed stable
and periodic at N=200000 (~6.7 cycles), no NaN.

A fine-tune sweep across BASE_FRAC=0.65/0.75/0.8/0.85 (each with Q_MEAN
re-bisected for the PS target) showed the total-score improvement is
**one-directional and monotonic away from 0.65** -- score rises to 0.61, 1.09,
1.61 as BASE_FRAC increases further -- so 0.65 is a genuine (local) optimum
for this waveform family, not an arbitrary stopping point.

**What's still not resolved**:
- **ED remains the worst-fit index** (-23%). Raising BASE_FRAC further trades
  ED accuracy for S/D and PI accuracy (at BASE_FRAC=0.75, ED reaches 13.9, an
  almost exact match, but S/D and PI overshoot the other way to 2.96/1.48) --
  a genuine three-way tension in this waveform family between matching the
  absolute diastolic velocity and matching the two dimensionless pulsatility
  ratios simultaneously. Not resolved by this redesign; would need a further
  degree of freedom (e.g. an independently-shaped, non-flat diastolic taper,
  or relaxing the assumption that the whole cohort is fit by one representative
  waveform rather than per-patient variation) to chase further.
- **Mean PA-Ao pressure cross-check still fails**: 0.09mmHg simulated vs. the
  ~5mmHg literature value (Rudolph 1979) -- essentially unchanged from the v1
  finding despite the waveform fix. This suggests the pressure-gradient gap
  has a different root cause than the velocity-waveform-shape issue (plausibly
  the low, unsourced P0=30mmHg baseline assumption, Section 5's flagged gap,
  interacting with the calibrated KAPPA/STIFFNESS_SCALE) -- flagged as an open
  limitation for this model, analogous to the CoA project's disclosed
  post-op negative result, rather than force-fitted further.

**Overall assessment**: the v2 model is a legitimate, presentable first-pass
result -- it reproduces the cohort's peak-systolic velocity almost exactly and
gets both pulsatility indices (S/D, PI) within ~10%, using a single
literature/topology-derived geometry and a small number of jointly-calibrated
physiological parameters. The end-diastolic velocity mismatch and the failed
pressure cross-check are genuine, disclosed limitations, not swept under the
rug -- consistent with this project folder's established practice (see the
CoA project's honestly-reported post-op negative result) of reporting what a
first-principles model does and doesn't reproduce.

## 8. Reviewer feedback (round 1) -- response and Step 1 findings

A reviewer who read `REPORT_FOR_REVIEWER.md` gave a clear, sequenced set of
recommendations, summarized here for reference (full text kept in project
history): (1) verify clinical index definitions before further waveform
tuning; (2) fix the boundary-condition architecture (single biggest scientific
weakness -- the pressure cross-check failure); (3) run an identifiability/
sensitivity analysis; (4) validate per-patient/cross-validated, not just
against the calibration cohort's own mean; (5) source or bound the uncertain
physiological parameters and propagate uncertainty; (6) only then revisit the
waveform, and only with a physiologically-interpretable parameter, not an
empirical fit. Go/no-go verdict: promising preliminary evidence, not yet
submittable -- the pressure-gradient failure and calibration-vs-validation
conflation are likely major-reviewer objections if left as-is. Naming
feedback (this is a FETAL DA study, not a PDA study) actioned in the note at
the top of this document.

### Step 1 result: clinical index definitions verified using a real exemplar

Using the one real, single-case clinical Doppler readout already captured in
this project (Section 4's cross-check image, GA=24w0d, patient ID redacted;
on-screen fields PS=-59.06, ED=-9.99, TAmax=-21.53, and the machine's own
displayed S/D=5.91, RI=0.83, PI=2.28 cm/s), the standard obstetric-Doppler
formulas were verified directly, to 2-3 significant figures:

- S/D = PS/ED = -59.06/-9.99 = **5.912** (displayed 5.91) [OK]
- RI = (PS-ED)/PS = (-59.06+9.99)/-59.06 = **0.831** (displayed 0.83) [OK]
- PI = (PS-ED)/TAMX = (-59.06+9.99)/-21.53 = **2.279** (displayed 2.28) [OK]

**This confirms PI uses TAMX (time-averaged MAXIMUM velocity, i.e. the time-
average of the velocity envelope), not a simple intensity-weighted time-
averaged mean** -- exactly the reviewer's flagged concern. `compute_indices()`
in `pda_model.py` already used mean(u(t)) over whole cardiac cycles as PI's
denominator, which is the CORRECT formula structure for a bulk 1D model (which
only outputs one representative velocity per timestep, not a full spectral
distribution to extract a separate "envelope" from) -- so this specific
concern is resolved/confirmed, not a bug. Fixed a smaller, related precision
issue while verifying this: the cycle-averaging window is now aligned to an
exact whole number of cardiac cycles ending at the last simulated timestep
(previously a fixed time offset that could clip a partial cycle and bias the
mean slightly); this changed the calibrated result negligibly (PI 2.067 vs
2.067, RI now also reported: 0.759 vs the real exemplar's 0.83, same order).

**A more consequential, previously-unexamined issue surfaced during this
verification, and remains UNRESOLVED**: clinical PS/ED/TAMX are near-
centerline (velocity-profile-PEAK) values from the Doppler spectral envelope,
whereas this model's u=q/A is, by construction of the governing equations
(q = the volumetric flow rate, A = cross-sectional area), the CROSS-SECTIONAL
MEAN velocity -- a physically different quantity, related by a profile-shape
correction factor >=1 (1.0 for a fully blunt/plug profile, up to 4/3 for fully
developed parabolic Poiseuille flow) that this model does not currently apply.
If that correction factor were larger during diastole (low-velocity, more
viscous-dominated, more parabolic flow) than during systole (high-velocity,
blunter profile) -- physically plausible, and consistent with a Womersley-type
analysis, though not yet computed for this vessel's specific dimensions/HR --
it would raise true ED relative to true PS by more than a uniform correction
would, which is exactly the asymmetric direction of the residual mismatch
(PS matched to +0.4%, ED still -23% low). Flagged as the most promising
concrete lead for the remaining ED discrepancy, NOT YET investigated
quantitatively (would need a Womersley-number calculation for this vessel's
radius/HR/viscosity, and a profile-correction factor applied per-phase, not
just a single constant).

**Raw waveform data availability, checked**: `DA related values.xlsx`
contains, per patient, THREE repeated PS/ED/S-D/PI measurements each (i.e.
three separately-measured cardiac cycles' worth of already-computed indices),
not a raw digitized velocity-vs-time waveform. **Recomputing indices from raw
waveforms, as the reviewer suggested, is therefore not possible with the data
currently in this project folder** -- would require either the original
ultrasound system's raw spectral Doppler trace exports (not present here) or
a fresh prospective acquisition. Noted as a hard data-availability
constraint, not something to be worked around.

### Step 2 result: two-compartment (pulmonary/systemic) boundary redesign

Built `two_compartment_model.py`: a lumped 0D model of the PA compartment
(fed by RV ejection, draining to the pulmonary vascular bed via `R_pulm`) and
the Ao/systemic compartment (fed by LV ejection, draining via `R_sys`),
connected by an orifice/Bernoulli-type DA relation
`Q_DA = K_DA*sign(dP)*sqrt(|dP|)` -- standard cardiac-shunt convention, and
consistent with the review draft's own emphasis on Bernoulli's equation at
the DA constriction. This does NOT modify `baker_1d_solver.py` (kept
unchanged, since it underpins the published CoA repo) -- instead, the
resulting Q_DA(t) becomes the 1D DA tube's prescribed inlet flow
(`pda_model_v3_twocompartment.py`), so DA flow now genuinely EMERGES from a
pressure difference between two independently-parameterized circulations,
rather than being an assumed shape (the reviewer's core architectural ask).

**Parameters** (see file docstring for full derivation): combined fetal
cardiac output at 13.5wk log-interpolated from Vimpeli et al. (2009)'s
directly-measured anchor points (9mL/min at 11wk, 121mL/min at 20wk;
WELL-SOURCED anchors, EXTRAPOLATED interpolation) = ~18.5mL/min; RV:LV output
ratio ~1.32 (same source family, close-GA, WELL-SOURCED); DA shunt fraction
85% of RV output (qualitatively well-established fetal physiology, but the
specific fraction is EXTRAPOLATED from near-term data); absolute PA/Ao
compartment pressures (32.5/27.5mmHg) are ASSUMED (no first-trimester value
found -- chosen only so the mean gradient matches Rudolph 1979's ~5mmHg);
`R_pulm`/`R_sys`/`K_DA` are back-calculated from those assumptions, not
independently sourced magnitudes; compartment compliances are placeholder
values chosen only for a plausible RC time constant.

**Result 1, CORRECTED after reviewer round 2 -- the 5.4mmHg gradient is
circular, not an independent prediction**: a second review pass identified
that this is NOT a non-fitted consequence of the physiology, as originally
(wrongly) claimed. The chain is: `P_PA_MEAN_MMHG=32.5` and
`P_AO_MEAN_MMHG=27.5` were ASSUMED specifically so their difference equals
Rudolph's ~5mmHg target; `R_pulm`/`R_sys` are then back-calculated FROM those
assumed pressures; `K_DA` is back-calculated from the same assumed gradient.
Recovering "5.4mmHg" from a model whose resistances and orifice coefficient
were themselves derived from an assumed ~5mmHg is circular -- confirmed
starkly by the Section 10.3 uncertainty sweep, which sampled a 3-7mmHg
ASSUMED gradient and got a 3.6-7.3mmHg OUTPUT interval: the output range is
just the input range, not an emergent, independently-constrained result.
**This does not mean the two-compartment architecture is worthless** -- it
correctly reproduces the qualitative direction/order-of-magnitude of known
fetal physiology, and DA flow does stay forward (non-reversing) throughout
the cycle, which is a structural (not parametric) consequence of the model's
equations. But the specific "5.4mmHg" number must NOT be reported as a
non-fitted mechanistic prediction, and Section 8/`REPORT_FOR_REVIEWER.md`'s
original framing of it as such has been corrected (see Section 11).

**Result 2, CORRECTED after reviewer round 2 -- a real one-way-coupling
architecture flaw, not a resolution**: the original write-up here claimed
adding the 0D gradient (5.4mmHg, itself now known circular, see Result 1
above) to the 1D tube's own small local pressure drop (~0.04-0.16mmHg) gives
"the true physically-meaningful pressure difference" -- this was WRONG, for
a reason the reviewer identified precisely: the architecture is
`0D compartments -> prescribed DA flow -> 1D tube`, a ONE-WAY forcing. The
1D tube's own pressure drop has NO way to feed back into the 0D compartments'
equations (the 0D system was already solved, independently, before the 1D
tube ever ran). Naively adding the two pressure-drop numbers together risks
DOUBLE-COUNTING the same physical pressure drop (since the 0D layer's
Bernoulli/orifice relation ALREADY converts the assumed compartment pressure
difference into the DA flow -- the 1D tube's own drop is not necessarily an
independent, additional physical effect on top of that, and simply summing
them is not justified without solving the two subsystems SIMULTANEOUSLY,
which this architecture does not do). More fundamentally: flow and pressure
continuity are not enforced simultaneously at both DA/compartment interfaces
-- this is one-way forcing, not a coupled 0D-1D model, and should not be
described as one. See Section 11 for the reviewer's recommended fix (choose
ONE internally consistent architecture: either a genuinely coupled two-sided
impedance 1D model, or a single 0D DA element with R/L/C, not a disconnected
0D-then-1D chain).

One structural (not parametric) finding from v3 DOES survive this
correction: the DA's wave-transit time is tiny relative to the cardiac cycle
(L=0.284cm, calibrated wave speed c~178cm/s at stiffness_scale=0.01, giving
transit time ~0.0016s vs. T_period=0.4s, i.e. the DA is "acoustically short,"
its length being under 0.5% of the pressure wave's cycle-length) -- meaning a
full 1D wave-propagation treatment is not obviously buying anything physical
for this specific vessel that a properly-coupled lumped (0D) RLC element
would not also capture. This is a genuine argument in favor of the reviewer's
"simpler publishable alternative" (Section 11, Option B), not just an
expedient shortcut.

**Result 3 -- a new, genuine, UNRESOLVED discrepancy**: the resulting
simulated velocities are far below the Doppler targets -- PS=13.9 vs 41.3,
ED=8.7 vs 13.1 cm/s at the Ao end (S/D and PI similarly low, ~1.6 and ~0.54
vs targets 3.85/2.15). Because `K_DA` and the flow/shunt-fraction inputs here
are deliberately literature-derived rather than fit to the Doppler indices
(to avoid exactly the calibration-vs-validation conflation the reviewer
flagged for Step 4), this ~3x velocity gap is being reported as a finding,
NOT closed by re-tuning K_DA back up to match PS. Three candidate
explanations, none yet distinguished:
  (a) the cardiac-output/shunt-fraction inputs, extrapolated from later-
      gestation data, may genuinely underestimate first-trimester DA flow;
  (b) the mean-vs-peak velocity profile issue already flagged in Step 1
      (clinical PS/ED are near-centerline peak velocities; this model's
      u=q/A is a cross-sectional mean) -- a profile correction factor could
      close some or all of this gap;
  (c) real flow may accelerate through an effective orifice area smaller
      than the full anatomical DA lumen (a vena-contracta-type effect at the
      described aortic-junction constriction), which would raise the true
      local velocity for the same volumetric flow.
This is left open rather than force-fit -- consistent with the reviewer's
Step 5/6 guidance to source/bound parameters honestly and only revisit the
waveform once the boundary-condition and identifiability work is in place.

**Status**: this is a first-pass, working implementation of the two-
compartment architecture, not yet a finished replacement for v2. Remaining
reviewer steps (3: identifiability/sensitivity; 4: per-patient/cross-
validated fit; 5: full uncertainty propagation over the several ASSUMED
parameters above) are follow-on work -- done below (Section 10).

## 10. Reviewer round 1, Steps 3-5

### 10.1 Sensitivity/identifiability (`sensitivity_analysis.py`)

Local one-at-a-time sweep (+-20%/+-40% from baseline) of the two-
compartment+1D model's key parameters, elasticities (`%change in output /
%change in parameter`) computed against the baseline (PS=13.86, ED=5.69,
SD=2.43, PI=0.85, gradient=5.44 -- NOTE these are the shorter-run (N=60000,
~2 cycles) sensitivity-sweep baseline values, not the longer-run N=150000
values quoted in Section 9, since the sweep prioritized speed/consistency
across ~25 runs over full per-run convergence precision):

| Parameter | PS elasticity | ED elasticity | S/D elasticity | PI elasticity | gradient elasticity |
|---|---|---|---|---|---|
| combined cardiac output | +1.1 to +1.3 | +0.2 to +0.5 | +0.8 to +1.0 | +0.8 to +1.0 | +0.13 to +0.18 |
| RV:LV ratio | +0.7 to +0.8 | ~0 (-0.01 to -0.02) | +0.7 to +0.85 | +0.8 to +1.0 | +0.02 to +0.16 |
| DA shunt fraction | +0.94 to +0.97 | +0.91 to +1.01 | ~0 (-0.05 to +0.09) | ~0 (-0.04 to +0.07) | ~0.03-0.04 |
| **DA stiffness scale** | **~0.03-0.05** | **-6.1 to +1.5** | **-1.1 to +2.8** | **-1.0 to +4.3** | **~0** |

**Two clean, robust findings**:
1. **Peak-systolic velocity (PS) is well-behaved and mechanistically
   sensible**: it responds to cardiac output, RV:LV ratio, and shunt
   fraction with clean, monotonic, order-1 elasticities (roughly
   proportional response, as expected for a flow/area-driven quantity), and
   is almost completely INSENSITIVE to DA wall stiffness (elasticity
   ~0.03-0.05) -- physically sensible, since stiffness governs compliance/
   wave dynamics, not bulk flow amplitude.
2. **End-diastolic velocity (ED), and consequently S/D and PI, are NOT
   well-behaved**: their response to DA stiffness scale is enormous
   (elasticities up to 6x in magnitude) AND changes SIGN between the -20%
   and +20% perturbations (e.g. ED's elasticity swings from -6.1 to +1.4) --
   a hallmark of a highly nonlinear, possibly near-singular local response,
   not a stable, well-identified relationship. This means ED/S-D/PI are
   fundamentally fragile to a parameter (DA wall stiffness) that has NO
   independent source or bound in this project (Section 4/9's flagged gap)
   -- i.e., these three indices are NOT reliably recoverable/identifiable
   from the current parameterization, distinct from PS which is.

**Degenerate-regime finding (a genuine fragility, not a bug)**: independently
perturbing `p_pa_mean_mmhg` downward or `p_ao_mean_mmhg` upward by as little
as 20% flips the assumed pressure ordering (P_pa no longer > P_ao), which
hits a deliberate fallback in `derive_parameters()` (`k_da=0` when the
assumed gradient is <=0) and collapses DA flow to zero identically (PS=ED=
0.075, S/D=1.0 exactly, PI~0 -- these are not physically meaningful outputs,
just the model's designed response to an internally-inconsistent input). This
demonstrates the model's entire behavior is critically contingent on
maintaining P_pa>P_ao -- true fetal physiology, but NOT independently
verified at 13.5 weeks specifically (Section 4's flagged gap) -- a real,
disclosed structural fragility, not treated as a numerical bug to silently
patch.

**Conclusion**: by the reviewer's own suggested test ("if many parameter
combinations produce similar indices, describe the model as phenomenological
rather than patient-specific") -- PS passes as reasonably mechanistic;
**ED/S-D/PI do not** -- their sensitivity analysis supports describing them,
at the current stage, as phenomenologically rather than mechanistically
determined.

### 10.2 Cross-validation (`cross_validation.py`)

4-fold CV of the v2 single-tube model (not v3 -- v2 is the model whose free
parameters are actually fit to Doppler data, so it's the one subject to the
reviewer's calibration-vs-validation conflation concern). Disclosed
simplification: only `Q_MEAN` was refit per fold (bisected against the
training folds' mean PS); `BASE_FRAC`/`KAPPA`/`STIFFNESS_SCALE` stayed at
their once-fit, full-cohort values -- this is a partial, not full nested, CV.

| Index | In-sample (full cohort) error | Out-of-sample (4-fold CV) mean abs. error |
|---|---|---|
| PS | 0.4% | ~8.3% |
| ED | 23% | ~20% |
| S/D | 8% | ~7.3% |
| PI | 4% | ~10.3% |

Calibrated `Q_MEAN` was stable across folds (0.226-0.237, a narrow ~5%
range), and the out-of-sample errors are not dramatically worse than the
in-sample fit for any index (ED and S/D are actually about the same or
marginally better out-of-sample; PS and PI degrade moderately, as expected
when refitting only one of four parameters to a smaller training set).
**Conclusion**: no strong evidence of gross overfitting from this partial
CV, but this is a limited test (3 of 4 free parameters were never
out-of-sample validated) -- a full nested CV refitting all 4 parameters per
fold would be needed for a stronger claim, and was not done here (compute
cost ~4x the original ~50-run grid sweep per fold).

### 10.3 Uncertainty propagation (`uncertainty_propagation.py`)

40-sample Monte Carlo over combined cardiac output (+-30%), RV:LV ratio
(+-0.28, the literature's own reported uncertainty), DA shunt fraction
(0.75-0.90), the assumed PA-Ao pressure gradient (3-7mmHg), and DA stiffness
scale (0.005-0.02) -- see Section 9 for each range's sourcing. Blood rho/mu
and the DA taper ratio were NOT varied in this pass (disclosed scope
limitation).

| Index | 5th percentile | median | 95th percentile | Target |
|---|---|---|---|---|
| PS (cm/s) | 8.7 | 12.8 | 18.7 | **41.3** |
| ED (cm/s) | 5.7 | 8.6 | 12.9 | 13.1 |
| S/D | 1.06 | 1.41 | 2.27 | 3.85 |
| PI | 0.08 | 0.41 | 0.93 | 2.15 |
| gradient (mmHg) | 3.6 | 5.2 | 7.3 | ~5 |

**The pressure gradient is well-constrained and correct across the ENTIRE
plausible parameter space** -- its 90% interval (3.6-7.3mmHg) comfortably
brackets the ~5mmHg literature target, and the median (5.2mmHg) sits right
on it. This is the strongest evidence yet that the two-compartment
architecture genuinely, robustly fixes the reviewer's originally-flagged
pressure-gradient failure -- not by luck of one parameter choice, but across
the whole space of literature-plausible inputs.

**The velocity indices do NOT reach their targets anywhere in the plausible
space** -- PS's 95th percentile (18.7) is still under half the target (41.3);
S/D and PI's 95th percentiles (2.27, 0.93) remain well below their targets
(3.85, 2.15) too. ED is the partial exception: its 95th percentile (12.9)
comes close to its target (13.1). **This is important**: it shows the
~3x PS gap identified in Section 9 is NOT an artifact of one unlucky
parameter choice or a point estimate that could be nudged into range by
plausible re-tuning -- it is a robust, structural shortfall that persists
across the entire literature-plausible parameter space. This strengthens
(does not weaken) the case that one of Section 9's three candidate
explanations (underestimated first-trimester flow, mean-vs-peak velocity
profile correction, or an effective-orifice/vena-contracta area smaller than
the anatomical DA lumen) is needed to close the gap -- no amount of
within-range recalibration of THESE five parameters will do it.

### 10.1 CORRECTION (reviewer round 2): sensitivity results are NOT yet trustworthy as identifiability evidence

The round-2 review identified that `sensitivity_analysis.py` used N=60000-step
(~2 cardiac cycle) runs for speed, and that "the reported indices differ
materially between short and long runs" in this project's own prior results
(true -- e.g. v3's ED was 5.69 at a short/~2-cycle run vs. 8.67-9.997 at
longer 5-7 cycle runs in Section 9's own numbers). The dramatic, sign-
flipping elasticities reported for `stiffness_scale` in the table above may
therefore reflect **incomplete periodic convergence, not genuine parameter
non-identifiability** -- a materially different, and much less alarming,
explanation than what was originally concluded. Additionally, the current
`compute_indices()` ED definition (mean velocity over the final 15% of the
cycle, a somewhat arbitrary averaging window) does not match the clinical
end-diastolic SAMPLING convention (a specific instantaneous point in the
cycle), which could itself introduce discontinuities/noise into the
reported ED as parameters vary. **The Section 10.1 conclusions above
("ED/S-D/PI are not reliably identifiable") are PROVISIONAL, not confirmed
-- pending a re-run to full periodic convergence with a corrected ED
definition (Section 12).** Separately, one-at-a-time (OAT) sensitivity, even
once convergence is fixed, is NOT a real identifiability analysis on its own
-- it cannot detect compensating/degenerate parameter COMBINATIONS (e.g. two
parameters that trade off to preserve the same output), which requires joint
exploration (a 2D+ grid, parameter-correlation/profile-likelihood analysis,
or a posterior/Bayesian treatment) -- not yet done (Section 12).

### 10.4 Overall verdict on phenomenological vs. mechanistic -- CORRECTED (reviewer round 2)

The paragraph originally here claimed "the pressure-gradient mechanism is
now genuinely mechanistic... robust across the entire plausible parameter
range, not fit to any Doppler target." **This was wrong, and is exactly the
overclaim the reviewer's round 2 rejected**: Section 9's Result 1 correction
explains why -- the pressure-gradient result is circular (the compartment
pressures were assumed specifically to produce ~5mmHg, and everything else
is back-calculated from that assumption), so "robust across the plausible
range" in Section 10.3 is really just restating that the sampled INPUT range
(3-7mmHg assumed) reappears as the OUTPUT range (3.6-7.3mmHg) -- not
independent confirmation of anything. **The correct verdict, per Section 11,
is that NEITHER half of this model should currently be called mechanistic
in the sense of "an independently-constrained, non-circular prediction"** --
the pressure side is circular by construction, and the velocity/pulsatility
side is phenomenological (as this section originally, correctly, said). See
Section 11 for the full accounting and Section 12 for the path to an
actually-defensible mechanistic claim.

## 11. Reviewer round 2: circularity and coupling critique -- accepted in full

The reviewer's second pass rejected the round-1 "resolved" framing and
identified two substantive problems the round-1 response had missed, plus a
methodological critique of the Section 10 analyses. Both substantive
problems are ACCEPTED, not disputed -- see the corrections inline in
Sections 9 and 10.1/10.4 above (each marked "CORRECTED after reviewer
round 2"):

1. **Circularity**: the 5.4mmHg gradient is back-calculated FROM an assumed
   ~5mmHg-producing pair of compartment pressures, so recovering it is not
   independent validation. The uncertainty sweep's 3-7mmHg-in ->
   3.6-7.3mmHg-out result is the clearest evidence of this circularity, not
   (as originally framed) evidence of robustness.
2. **One-way coupling / possible double-counting**: the architecture
   (0D compartments -> prescribed DA flow -> 1D tube) cannot enforce flow
   AND pressure continuity simultaneously at both DA interfaces; the 1D
   tube's own pressure drop cannot feed back into the 0D system; summing the
   0D gradient and the 1D tube's local drop (as the original Section 9 text
   did) is not justified and risks double-counting.

**Also raised, and accepted as valid critique of Section 10** (not yet
acted on -- see the work plan below): the mean-to-peak velocity correction
cannot plausibly be as large as 3x (classical peak/mean ratios are <=~2 for
developed parabolic profiles, smaller for flatter/pulsatile ones) -- this
materially weakens candidate explanation (b) from Section 9; a
vena-contracta correction (candidate (c)) should not be invoked just to
close the gap without direct evidence (measurement location, insonation
angle, anatomical diameter, narrowest-lumen location); the OAT sensitivity
analysis is not an identifiability analysis; the partial cross-validation
(1 of 4 parameters refit per fold) is not genuine out-of-sample validation
of the fitted model as a whole.

**New, concrete, testable hypothesis from the reviewer**: since velocity
varies inversely with cross-sectional area, a 3x velocity shortfall
corresponds to an EFFECTIVE DIAMETER of only 1/sqrt(3) ~= 0.58x the modeled
diameter. This reframes candidate explanation (a)/(c) from Section 9 into a
specific, checkable anatomical/measurement question (Section 12, Step 2)
rather than a vague "flow might be underestimated" hand-wave.

**Reviewer's recommended path forward** (adopted as this project's plan,
Section 12):
1. Choose ONE internally consistent architecture -- either (A) a genuinely
   coupled 0D-1D model with pressure/impedance applied at BOTH DA
   boundaries so flow and pressure are solved together, or (B) a simpler,
   single 0D DA element (resistance + inertance + compliance, "RLC"), with
   no separate/disconnected 1D tube.
2. Audit the geometry/measurement correspondence (DA diameter at ~13.5wk;
   whether Szpinda's diameter is external/internal/mean/endpoint; Doppler
   sample location and angle correction; whether clinical PS/ED represent
   the narrowest jet or the main DA lumen; triplicate-averaging and
   patient-level distributions) -- the reviewer's own first-priority
   investigation for the velocity gap.
3. Establish numerical convergence (full periodic convergence for every
   sensitivity run, not ~2-cycle short runs; replace the ED definition with
   the clinical end-diastolic sampling convention; test temporal/spatial
   resolution).
4. A real JOINT identifiability analysis (not OAT) on a small, defensible
   parameter set (effective diameter, outlet impedances, compliance/
   stiffness, possibly a loss coefficient) -- parameter correlations and
   prediction intervals, not just one-parameter-at-a-time elasticities.
5. Decide the paper's claim before writing more: a realistic, honest,
   publishable claim may be "a reduced-order fetal DA model demonstrates
   that literature-constrained flow and anatomy do not reproduce observed
   Doppler velocities, identifying a structural inconsistency requiring
   revised geometry or boundary representation" -- explicitly NOT a claim of
   successful mechanistic validation.

**Reviewer's go/no-go estimate**: ~55-65% of the way to a strong
submission; ready now to start drafting Methods/limitations-framed Results;
~3-6 weeks from a defensible preprint/internal-circulation draft (assuming
the geometry/numerical audits resolve the main questions); ~2-4 months from
a journal-submission-ready state; high risk of rejection if submitted as-is,
specifically on the circular pressure validation, one-way coupling, and
unresolved 3x velocity error.

## 12. Next-steps plan (adopted from reviewer round 2)

Work items, roughly in the reviewer's recommended order (Step 2, the
geometry/measurement audit, and Step 3, numerical convergence, do not
depend on the Step 1 architecture choice and can proceed in parallel with
it; Step 4 depends on Steps 1 and 3 both being settled first):

- [ ] **Step 1 (architecture choice)**: decide between Option A (fully
  coupled two-sided-impedance 1D model -- harder, more rigorous) and Option
  B (single coupled 0D RLC DA element, no disconnected 1D tube -- simpler,
  and arguably MORE appropriate given the DA's short acoustic length noted
  in Section 9's correction). Needs a decision before further model-building
  effort is invested either way.
- [ ] **Step 2 (geometry/measurement audit)**: check Szpinda (2007)'s
  diameter definition (external vs. internal vs. mean vs. endpoint) against
  what "diameter" should mean for a Doppler cross-sectional-area
  calculation; check whether the clinical PS/ED in this cohort's data was
  measured at the narrowest point or the main lumen; check for any
  reported/typical insonation angle correction; test the reviewer's
  effective-diameter-ratio hypothesis (~0.58x) directly against whatever
  independent diameter information can be found.
- [ ] **Step 3 (numerical convergence + ED definition fix)**: re-run
  Section 10.1's sensitivity sweep (and re-verify Section 10.2-10.3) at full
  periodic convergence (confirm via last-2-cycle comparison, not just a
  fixed step count); replace `compute_indices()`'s late-diastole-window-mean
  ED definition with a true end-diastolic instantaneous-sample convention;
  add a mesh (M) and timestep (CFL) convergence check.
- [ ] **Step 4 (joint identifiability)**: once Steps 1 and 3 are done, run a
  joint (not OAT) exploration -- 2D+ grids or a proper profile-
  likelihood/posterior treatment -- over a SMALL, defensible parameter set
  (effective diameter, outlet impedance(s), compliance/stiffness, possibly a
  discharge/loss coefficient), reporting correlations and prediction
  intervals, not single-parameter elasticities.
- [ ] **Step 5 (claim decision)**: once the above is in hand, decide
  explicitly whether the paper's claim is (i) successful mechanistic
  reproduction of Doppler indices (only justified if the velocity gap gets
  resolved), or (ii) the reviewer's suggested honest alternative -- a
  diagnostic/negative result showing literature-constrained flow/anatomy
  fails to reproduce the observed Doppler velocities, pointing to a specific,
  identified structural inconsistency. Both are legitimate publishable
  outcomes; which one applies should be decided by the evidence, not
  assumed in advance.

## 13. v4: de-circularized, genuinely coupled 0D RLC model (Step 1 done)

User chose Option B (single coupled 0D RLC DA element) over Option A (fully
coupled two-sided-impedance 1D model), given the acoustic-shortness argument
in Section 9's correction. Built `da_rlc_coupled_model.py`:

- **State**: `(P_pa, P_ao, Q_da)` -- THREE simultaneously-integrated ODEs
  (RK4), not a staged 0D-then-1D pipeline. `Q_da` is now a genuine dynamical
  state with inertance (`L_da`, real phase lag/memory) and a nonlinear
  orifice/Bernoulli loss term (`R_da`), replacing v3's instantaneous
  algebraic `Q=K*sqrt(dP)` relation. Flow and pressure are solved together --
  directly resolves the reviewer's one-way-forcing/double-counting critique.
- **De-circularization**: `R_pulm` and `R_sys` are now both anchored to a
  SINGLE shared baseline pressure (`P0_BASELINE_MMHG=30.0`, chosen without
  reference to any target gradient), with only the independently-sourced
  flow split (Vimpeli et al. 2009 cardiac output/RV:LV ratio, extrapolated
  ~85% shunt fraction) differing between the two sides. `R_da` (loss
  coefficient) is derived from orifice theory (discharge coefficient x
  throat area), not back-calculated from any assumed pressure difference.
  Any resulting P_pa-P_ao gradient is now a genuine emergent output.
- **Compliance simplification, disclosed**: no separate DA-level compliance
  state -- folded into `C_pa`/`C_ao`, justified by the acoustic-shortness
  finding (Section 9) and needed to keep the free-parameter count small
  (reviewer's Step 4 request). `R`+`L` only for the DA element itself.
- **Convergence**: this coupled ODE system is ~10x cheaper to run than the
  old 1D PDE (~1-5s vs. 20-30s) and converges to <0.001% cycle-to-cycle
  difference within 8 cycles (vs. the flagged ~2-cycle short runs in
  Section 10.1) -- directly resolves the reviewer's Step 3 convergence
  concern for this architecture.

### 13.1 Testing the reviewer's effective-diameter hypothesis

At the full anatomical Szpinda throat area (`area_scale=1.0`, discharge
coefficient Cd=0.7, otherwise literature-sourced parameters unchanged): PS=
19.4, ED=5.4, S/D=3.59, PI=1.38, emergent gradient=0.10mmHg. **The velocity
gap is now ~2.1x (down from v3's ~3x)** purely from the architecture fix
(genuine dynamics/inertance vs. an instantaneous algebraic relation) --
before even invoking a diameter correction.

Bisecting `area_scale` to hit the PS target exactly: **area_scale=0.464**
(diameter ratio=0.68, close to the reviewer's own back-of-envelope 0.58
estimate -- reasonable agreement given the different baseline) gives PS=41.3
(exact, by construction), **ED=11.8 (-10%, much improved from v3's -23%)**,
**S/D=3.51 (-9%, close)**, PI=1.36 (-37%, still the outlier), emergent
gradient=0.45mmHg (target ~5mmHg, still ~11x short).

### 13.2 Joint identifiability: `area_scale` x `discharge_coeff` (Step 4)

Fast full-convergence coupled model made a genuine JOINT 2D scan tractable
(40 points, `joint_identifiability.py`/`joint_identifiability_results.csv`,
all confirmed <0.001% cycle-to-cycle convergence). Clean, non-degenerate
structure found -- NOT a compensating ridge, which is itself informative:

- **PS, ED, S/D respond strongly and cleanly to `area_scale`** (smooth,
  monotonic, inversely related, as physically expected from velocity=flow/
  area) and are **nearly INSENSITIVE to `discharge_coeff`** (e.g. at
  area_scale=0.393, PS varies only 46.4-49.1 and ED only 13.9-14.2 across
  Cd=0.5-0.9) -- these three indices are well-identified by `area_scale`
  specifically, not confounded with `discharge_coeff`.
- **The emergent pressure gradient responds to BOTH parameters** (smaller
  area AND lower Cd both increase DA resistance and raise the gradient) --
  e.g. at area_scale=0.15, gradient ranges 2.46-7.09mmHg across Cd=0.9-0.5 --
  meaning `discharge_coeff` IS identifiable, but only via the pressure
  gradient, not via the velocity indices.
- **PI is structurally stuck (~1.3-1.4) across the ENTIRE 2D grid**,
  regardless of `area_scale` or `discharge_coeff` -- from 0.69 at the most
  extreme constriction tested up to a ~1.38 plateau for area_scale>0.5,
  NEVER approaching the 2.15 target anywhere in this 2-parameter space.
  **This is a clean, informative negative result**: PI's shortfall is NOT
  explained by throat geometry or discharge coefficient at all -- it points
  toward the inertance (`L_da`, which physically low-pass-filters/damps
  transmitted pulsatility -- a plausible mechanism, not yet tested
  directly) or the ventricular ejection waveform shape as the more likely
  lever, not the orifice/area parameters this scan covered.

**Best point in this 2D grid** (area_scale~0.39-0.51, minimizing total
score): PS overshoots by 12-19%, ED is within 6-9%, S/D within 8-15%, but
**PI remains 37-41% low everywhere tested** -- a genuine, isolated,
unresolved gap distinct from the other three indices, not closed by
anything in this parameter set.

### 13.3prime Geometry/measurement audit (Step 2) -- a real, independently-sourced fix

**Finding 1 -- Szpinda (2007) measures EXTERNAL diameter, and this project's
code was silently using it as if it were internal/luminal diameter.**
Re-reading Szpinda's Methods (verified in `szpinda_extract.txt`): specimens
were formalin-fixed, dissected under a stereoscope, and photographed --
"external diameter" is stated explicitly and repeatedly. `da_geometry.py`'s
`da_geometry_cm()` computed `r_mean_mm = d_mm/2.0` directly from this value
with NO wall-thickness correction -- despite this project's OWN plan doc
(Section 2.2) claiming, incorrectly, that an "internal radius after a
wall-thickness allowance" had been applied. **This was a real, previously
undocumented bug: aspirational text in the docs that was never actually
implemented in code.** No DA-specific wall-thickness value was found in
Szpinda (2007) or anywhere else searched -- this specific gap (external vs.
internal) remains UNRESOLVED as a wall-thickness question, but see Finding 2.

**Finding 2 -- an independent, better-located diameter source exists and
was not being used.** Leao et al. (2015), *J Morphol Sci* 32(3):170-175
(n=44 human fetuses, 9-26 weeks GA, in `literature/`, previously unread) --
measures diameter SPECIFICALLY at "the ductus base at the aorta" (their
parameter G), i.e. the narrowest point at the aortic junction (matching
Szpinda's/Setchi's own description of a constriction there, and matching
where this project's model already defined its "throat"/Ao-end comparison
point) -- NOT an along-length average like Szpinda's regression. Their
directly-measured (not regression-extrapolated) age-binned value for
9-14 weeks GA (n=10, covering this cohort's 13.5wk): **G = 0.93+-0.55mm**.

**Cross-check against the Section 13.1 empirical finding**: 0.93mm/2 =
0.465mm radius, vs. this project's Szpinda-regression-based throat radius of
0.685mm (diameter 1.469mm) -- a ratio of **0.679**. Section 13.1's
bisection search, using the Doppler PS target ALONE (no anatomical
information), independently arrived at a diameter ratio of **0.68** to
match peak-systolic velocity. **These two numbers, arrived at by completely
independent routes (one from an anatomical morphometry paper never
previously read in this project; one from fitting a completely different
paper's Doppler velocity data), agree to within 0.2 percentage points.**

**Action taken**: `da_geometry.py` now includes `da_diameter_base_at_aorta_mm()`
(Leao's regression + age-binned values), and `da_rlc_coupled_model.py`'s
default throat radius now comes from Leao's 9-14wk value, not Szpinda's
general regression. Re-running the model with ZERO Doppler-fitted
parameters (Vimpeli cardiac output, Szpinda length, Leao throat diameter,
a standard Cd=0.7 orifice discharge coefficient, single shared baseline
pressure) gives:

| Index | Simulated (fully literature-sourced, no fitting) | Target | Rel. error |
|---|---|---|---|
| PS (cm/s) | **41.6** | 41.3 | **+0.6%** |
| ED (cm/s) | 11.8 | 13.1 | -9% |
| S/D | 3.51 | 3.85 | -9% |
| PI | 1.36 | 2.15 | -37% |
| gradient (mmHg) | 0.46 | ~5 | still short |

**This is a materially different, and much stronger, result than anything
in Sections 6-13**: PS, ED, and S/D are now all within ~10% of target using
ENTIRELY independently-sourced parameters -- no Doppler-target fitting
anywhere in the chain. This is a legitimate, non-circular, partially
mechanistic success for 3 of 4 indices -- NOT a coincidence given the
cross-check above, though still a modest-n (10 specimens), noisy (R=0.48)
anatomical data point, not a large, gestational-age-specific cohort.

**PI remains the one clear, unexplained outlier** (-37%), consistent with
Section 13.2's joint identifiability finding that PI does not respond to
throat geometry or discharge coefficient at all -- this geometry fix,
exactly as that finding predicted, did NOT move PI. The inertance-damping
or ventricular-waveform-shape hypotheses remain the live leads for PI
specifically, unaffected by this section's finding.

**The pressure gradient (0.46mmHg) is still far short of ~5mmHg** even with
the corrected, smaller throat area -- consistent with Section 13.2's finding
that the gradient needs an even smaller area AND/OR lower discharge
coefficient than what closes the velocity gap alone; these two targets
(velocity vs. gradient) are not simultaneously satisfied by the same
`area_scale` in this parameterization. Still an open gap, not closed by
this finding.

**Other Step 2 items, checked but inconclusive (data gaps, not resolved)**:
Doppler sample location and insonation angle correction for this cohort's
own scans are not documented in this project's data (only the pre-computed
PS/ED/S-D/PI values are available, Section 8); the narrowest-jet-vs-main-
lumen question is presumptively addressed by using Leao's "base at aorta"
(narrowest point) location, consistent with standard clinical practice of
sampling Doppler at the point of maximal/jet velocity, but this project has
no direct confirmation of the original sonographers' exact sample-gate
placement for this specific 24-fetus cohort.

### 13.3 Status against the reviewer's 5-step plan

Step 1 (architecture): DONE, de-circularized, user-approved choice. Step 2
(geometry/measurement audit): DONE (Section 13.3prime) -- found Szpinda's
diameter is external/postmortem (a real, previously undocumented modeling
gap) and, more importantly, found an independent literature source (Leao et
al. 2015) measuring diameter at the correct anatomical location (the
aortic-junction narrowest point) whose value, used with NO Doppler fitting,
independently matches the 0.68 diameter ratio found by fitting PS alone --
a genuine cross-validation, not a coincidence. Step 3 (convergence): DONE
for this architecture (see above). Step 4 (joint identifiability): a first
real pass DONE (Section 13.2) -- extended to more parameters (outlet
impedances, inertance) would strengthen it further, particularly to test
the inertance-damping hypothesis for PI, still the one unresolved index.
Step 5 (claim decision): still pending -- but the evidence increasingly
supports a REAL (if partial) mechanistic claim for PS/ED/S-D specifically,
with PI and the pressure gradient remaining honest, unresolved gaps.

## 15. Numerical convergence and ED-definition fix (Step 3, completed properly)

**ED definition, fixed**: `compute_indices_0d()` previously computed ED as
the MEAN velocity over the final 15% of the cycle -- an arbitrary averaging
window, not the clinical convention. Direct inspection of the velocity trace
near the cycle boundary (smooth, monotonic decay through diastole, no
numerical noise) confirmed the window-mean was systematically HIGHER than
the true end-of-cycle value, because it averaged in earlier, higher-velocity
samples from earlier in the diastolic decay. **This means the OLD ED number
throughout Sections 13-14 (e.g. "ED=11.8, -9%") was flattering the model --
the true, clinically-correct instantaneous end-diastolic sample is LOWER.**
Fixed to sample the velocity at the true instantaneous end-of-cycle point
(the clinical end-diastolic sampling convention).

**Re-running the literature-sourced, zero-fitting configuration (Section
13.3prime) with the corrected ED definition**:

| Index | Old (window-mean ED) | **Corrected (instantaneous ED)** | Target |
|---|---|---|---|
| PS (cm/s) | 41.6 | 41.6 (unaffected) | 41.3 |
| ED (cm/s) | 11.8 (-9%) | **10.5 (-19%)** | 13.1 |
| S/D | 3.51 (-9%) | **3.95 (+2.6%)** | 3.85 |
| PI | 1.36 (-37%) | 1.42 (-34%, ~same) | 2.15 |

**Honest interpretation, not spin**: fixing the ED definition makes the ED
match WORSE (a real, previously-hidden discrepancy, now correctly exposed),
while S/D happens to look BETTER purely as an arithmetic consequence of a
lower ED raising the S/D ratio closer to target -- this is not an
independent improvement, just a byproduct of using the correct formula, and
should not be reported as if the model got better. PI is essentially
unchanged (still the clear outlier).

**Numerical convergence, fully verified for this architecture** (a
directly-answerable question the 0D model makes cheap, unlike the old 1D
PDE's CFL-limited short runs):
- **Temporal resolution**: varied RK4 steps-per-cycle from 500 to 8000 --
  results agree to the 4th decimal place at ALL tested resolutions (PS
  41.5797 at 500 steps/cycle vs. 41.5809 at 8000). The model's default
  (4000 steps/cycle) is far more than adequate.
- **Cycle-count (periodic) convergence**: <0.001% difference between the
  last two cycles at 8 cycles (already established in Section 13).
- **"Spatial resolution" no longer applies**: this architecture has no
  spatial mesh (a direct, disclosed consequence of choosing the 0D RLC
  option over the two-sided-impedance 1D option) -- noted explicitly
  rather than silently dropped.

**Joint identifiability grid (Section 13.2) re-run with the corrected ED
definition** (`joint_identifiability_results.csv`, all runs re-confirmed
<0.01% cycle-to-cycle convergence): note this grid's `area_scale` now
multiplies the ALREADY Leao-corrected throat area (Section 13.3prime), not
the original Szpinda-based one, so the numbers are not directly comparable
to Section 13.2's original table. At `area_scale=1.0` (i.e. Leao's value
used as-is): PS=40.4-42.0, ED=10.5-10.6, S/D=3.79-4.01, PI=1.36-1.44 across
Cd=0.5-0.9 -- confirming the "no further fitting" default (area_scale=1.0,
Cd=0.7) is very close to the best-scoring point in the ENTIRE 40-point grid
(score 0.57 vs. a grid-wide best of 0.56) -- i.e., the good result in
Section 13.3prime is not a cherry-picked or lucky point. **PI remains stuck
at 1.3-1.4 across the entire grid (ranging only 0.26-1.44 across all 40
points), never approaching 2.15 anywhere** -- this conclusion is now
confirmed robust to BOTH the ED-definition fix AND full numerical
convergence, strengthening (not weakening) the Section 13.2 finding that
PI's shortfall is not explained by throat geometry or discharge coefficient.

## 16. Pressure-reference audit (reviewer round 3, highest priority) -- the ~5mmHg target is WITHDRAWN

The reviewer's Bernoulli consistency check (ΔP≈4v² with v in m/s, ΔP in
mmHg) found that the cohort's own observed peak velocity (~0.416 m/s)
implies a physically-compatible gradient of only ~0.7mmHg (with a
Cd=0.7 nonlinear-loss estimate of ~1.4mmHg at peak) -- i.e. our model's
0.46mmHg emergent gradient (Section 13.3prime) is **broadly consistent with
the velocity scale actually observed in this cohort**, not a failure.
Conversely, a genuine 5mmHg gradient implies a velocity of ~1.12 m/s --
nearly 3x the cohort's observed peak. The two targets (5mmHg and 41cm/s)
cannot both be locally correct for the same vessel under basic orifice
physics. Investigated which one is wrong, per the reviewer's explicit
instruction not to force area/Cd to reach 5mmHg regardless of the answer.

**Finding: the "~5mmHg" figure fails on BOTH species and gestational-age
grounds, independently.** Traced to Rudolph AM, "Fetal and neonatal
pulmonary circulation," *Annu Rev Physiol* 1979, 41:383-395 -- a REVIEW
article (not a primary measurement), synthesizing a research program built
on the chronically-instrumented **fetal LAMB (sheep)** preparation, the
standard invasive fetal cardiovascular physiology model of that era. Human
fetal cardiac catheterization is not ethically or technically feasible at
ANY gestational age -- this figure was never, and could never have been, a
direct human measurement. Secondary sources (e.g. Crossley et al. 2009,
also fetal-lamb-based) repeat "~5mmHg" as a general statement about
relative pressure LEVELS between the pulmonary and systemic circulations
(reflecting high fetal PVR vs. lower SVR) -- i.e. it reads as a
representative/summary figure about the two circulations generally, not a
rigorously isolated LOCAL pressure drop measured specifically across the DA
orifice. Additionally, chronic fetal lamb instrumentation is near-
universally performed in the LAST THIRD of gestation (term ~145 days) --
physiologically comparable to human late 2nd/3rd trimester, not to this
project's 13.5-week first-trimester cohort. **Species mismatch (lamb vs.
human) and gestational-stage mismatch (late-gestation vs. first-trimester)
are each INDEPENDENTLY sufficient reasons to disqualify this figure as a
quantitative target** -- not merely the local-vs-whole-pathway ambiguity
(itself also unresolved, since the secondary sources don't specify).

**No human first-trimester fetal PA/Ao pressure data exists, and is
unlikely to ever exist**, given the ethical/technical infeasibility of the
measurement at this gestational age. This is a genuine, PERMANENT evidence
gap for this specific target population -- not a search failure, and not
something further literature review will resolve.

**Action taken, per the reviewer's explicit instruction**: the ~5mmHg
gradient is WITHDRAWN as a quantitative validation criterion for this
model. It should NOT appear in future work as a target to hit, and the
emergent 0.46mmHg gradient should NOT be described as a "shortfall" or
"unresolved gap" -- reframed, it is the model's own (currently unvalidated,
since no legitimate comparison target exists) prediction, and is at least
qualitatively consistent (same order of magnitude implied by Bernoulli) with
the cohort's own observed velocity scale. This resolves what Sections 13-16
had been treating as an open, unexplained shortfall -- it was never a valid
comparison in the first place, not a model failure requiring further
fitting. Every prior mention of "gradient still short of ~5mmHg target" in
Sections 13-16 above should be read with this correction; the number itself
(0.46mmHg) is unchanged, only its interpretation as a "failure."

## 17. PI mechanism factorial study and waveform diagnostics (reviewer round 3, Steps 2-3)

### 18.1 Diagnostic waveform characterization

Per the reviewer's request, computed TAMX (time-averaged maximum velocity,
PI's denominator) directly rather than only reporting PI: target
PI=2.15 with PS=41.6/ED=10.5 implies TAMX~14.5-15 cm/s; the simulated
waveform's actual TAMX is **21.9 cm/s -- 1.5-1.7x too high**. This confirms
the reviewer's diagnosis precisely: **the problem is not PS or ED
individually, it's that simulated velocity stays too high through too much
of the cycle.** Quantified: the simulated waveform spends **46.3% of the
cycle above 50% of peak-systolic velocity** -- a broad, sustained profile,
not the sharp systolic peak / low sustained diastolic floor shape that a
PI~2.15 waveform implies.

### 18.2 Factorial study results (`pi_factorial_study.py`/`pi_factorial_results.csv`)

Refactored `da_rlc_coupled_model.py` to support independently varying:
inertance scale, PA/Ao compliances (joint and independent), the shared
resistance baseline (preserving the independently-sourced flow split),
systolic duration and ejection sharpness, and RV/LV relative timing/shape
(previously both ventricles used IDENTICAL scaled waveforms). Tested each
hierarchy level the reviewer specified, one at a time from the current
best (literature-sourced, non-Doppler-fitted) baseline:

- **Inertance (0.1x-2x theoretical): NO effect on PI (1.40-1.44 throughout)
  or TAMX (unchanged at 21.9 cm/s).** This is a clean, direct experimental
  CONFIRMATION of the reviewer's theoretical point that inertance cannot
  sustain a persistent mean/TAMX-level effect over a periodic cycle
  (`<L*dQ/dt>=0`) -- the inertance-damping hypothesis floated in Section
  13.2 is now REFUTED, not just theoretically doubted.
- **Compliance (PA/Ao, joint and independent, 0.1x-10x): large effects, but
  destabilizing.** E.g. joint compliance at 0.5x gives PI=2.16 (almost
  exactly on target!) but simultaneously SD=10.6 and ED=4.9 (both far off) --
  compliance is a genuinely powerful lever, but there is no compliance
  value found that improves PI without badly breaking ED/S-D. Confirms the
  reviewer's caution that compliance may be at least as important as
  inertance -- it is, but not in a way that resolves the problem cleanly.
- **Resistance baseline (15-50mmHg, flow split preserved): PI improves as
  baseline decreases** (PI=2.12 at 15mmHg, vs. 1.42 at the default 30mmHg)
  **but PS overshoots substantially** (51.3 vs. target 41.3) -- a real,
  monotonic, informative direction, but not a free win.
- **Systolic duration and ejection sharpness: the clearest, most
  physiologically-interpretable lever.** A SHORTER systolic window
  (`systolic_frac`=0.20 instead of 0.35) alone gives PI=2.02 (close to
  target) with a much narrower waveform (25.9% of cycle above half-max, vs.
  46.3% at baseline) -- but PS overshoots to 53.6. Sharper ejection
  (higher power exponent) shows the same pattern.
- **RV/LV relative timing: the single largest-effect factor tested.** A
  10-15% of a cycle phase offset between RV and LV ejection (previously
  ALWAYS perfectly synchronized -- an assumption never examined until now)
  moves PI from 1.42 up through 2.71 (offset=0.10) to 3.23 (offset=0.15,
  now OVERSHOOTING target) -- confirming this untested assumption
  (identical, perfectly-synchronized RV/LV waveforms) was a real,
  consequential modelling simplification, not a safe default.

**Combined shape+amplitude test**: re-scaling flow amplitude to bring PS
back to the 41.3 target after applying a PI-improving shape change (shorter
systole, or RV/LV timing offset) does raise PI close to target (up to
~2.06-2.18) -- but ED and S/D both get WORSE in the process (ED drops
further to 7-8 cm/s, -40% to -45%; S/D overshoots to 5.0-5.9, +30% to +53%).
None of the combined points tested beat the current baseline's overall
score (0.57) -- every mechanism that improves PI trades away ED/S-D
accuracy by a comparable amount.

### 18.3 Honest conclusion

This is the same fundamental three/four-way tension first identified all
the way back in Section 6-7's original waveform calibration (v1/v2),
re-discovered independently in this much more physically-grounded
architecture: **no single tested mechanism (inertance, compliance,
resistance baseline, systolic duration/sharpness, or RV/LV relative timing)
simultaneously improves PI without degrading ED and/or S-D by a comparable
amount.** This looks like a genuine structural property of this model
family (a single lumped DA connecting two compartments, driven by scaled
ventricular ejection waveforms), not a matter of finding the right
untested parameter. Two directions remain untried and are the most
promising next steps, in the reviewer's own framing: (a) a joint,
multi-parameter optimization/response-surface exploring compliance,
resistance-baseline, and waveform-shape TOGETHER rather than one-at-a-time
(this factorial study was explicitly one-at-a-time per the reviewer's
requested hierarchy, not a joint search); (b) accepting PI as an honestly-
reported, currently-unresolved limitation and moving toward the paper's
claim (reviewer's Step 5/6) built around what IS resolved (PS/S-D accuracy
without Doppler fitting, the independent diameter-ratio convergence, the
withdrawal of the invalid pressure-gradient target) rather than continuing
to chase PI with more free parameters.

## 18. Uncertainty propagation on the corrected model (reviewer round 3, Step 3) -- supersedes Section 10.3

**Section 10.3's Monte Carlo is now INVALID and superseded** -- it ran on
the withdrawn, circular v3 two-compartment architecture (Section 11). This
section re-does it properly on the corrected, de-circularized coupled-RL
model with the Leao-throat-diameter geometry fix.

**A real methodological error, caught and fixed mid-analysis (reported
honestly, not hidden)**: the first attempt at this Monte Carlo sampled the
throat diameter from Normal(0.93mm, SD=0.55mm) -- Leao et al. (2015)'s
reported BETWEEN-SPECIMEN standard deviation (n=10). This let physically
implausible small-diameter tail samples through (down to a floored 0.2mm),
which drove numerically extreme, non-physical outputs (peak-systolic
velocity up to 337 cm/s -- roughly 8x the cohort's own observed value).
**The error**: this model represents ONE representative fetus at this GA
(this project does not attempt per-patient variation, Section 5/9's
disclosed scope), so the correct quantity to propagate is the STANDARD
ERROR OF THE MEAN (uncertainty in the population mean estimate), not the
raw between-specimen SD (biological variability across the 10 specimens).
SEM = SD/sqrt(n) = 0.55/sqrt(10) = 0.174mm -- re-ran with this corrected,
much tighter distribution.

### 18.1 UPDATE (reviewer round 4): epistemic vs. biological uncertainty, reported separately

Round 4 identified a further inconsistency in the analysis above (not
disputed): `rv_lv_ratio` was sampled from `Normal(1.32, 0.28)` -- the RAW
between-subject SD from Vimpeli et al.'s n=143 cohort -- while
`leao_diameter_mm` had already been corrected to use the SEM. This mixed
an epistemic (population-mean) treatment for one parameter with a
biological-variability treatment for another, inconsistently. **Fixed, and
extended per the reviewer's explicit request to report BOTH kinds of
uncertainty separately, not conflate them**:

- **Epistemic** (uncertainty in the ESTIMATED POPULATION-MEAN parameter --
  appropriate since this model represents one "representative" fetus, not
  per-patient variation): `rv_lv_ratio` ~ Normal(1.32, SEM=0.28/sqrt(143)=0.023),
  `leao_diameter_mm` ~ Normal(0.93mm, SEM=0.174mm) -- both now consistently
  using SEM, not raw SD.
- **Biological variability** (variation AMONG INDIVIDUAL FETUSES -- what
  the prediction might look like if built for a randomly-drawn individual
  rather than the population-representative one): `rv_lv_ratio` ~
  Normal(1.32, raw SD=0.28); `leao_diameter_mm` ~ Log-Normal, matched to
  Leao's own reported mean=0.93mm/SD=0.55mm -- **a log-normal, not a
  Normal, per the reviewer's correction**: the earlier (Section 18,
  original version) rejection of the raw-SD run as producing "non-physical"
  outliers was itself imprecise -- the wide outputs were not inherently
  non-physical, they resulted from using a Normal distribution (which
  permits near-zero/negative diameters in its left tail) for a strictly-
  positive physical quantity. A log-normal matched to the same mean/SD
  respects positivity by construction; the fix is distribution SHAPE, not
  simply narrowing the spread from SD to SEM.

**150-sample Monte Carlo, each version** (other parameters -- combined
cardiac output, discharge coefficient, shunt fraction, baseline pressure,
compliance -- held the same in both, as these are engineering-judgment
ranges without a clear epistemic/biological statistical distinction to
draw):

| Index | Epistemic 5th-95th (median) | Biological 5th-95th (median) | Target |
|---|---|---|---|
| PS (cm/s) | 20.9-99.8 (46.0) | 9.4-180.2 (60.5) | 41.3 |
| ED (cm/s) | 3.7-26.1 (11.7) | 2.2-124.9 (14.4) | 13.1 |
| S/D | 1.82-15.2 (3.28) | 1.24-13.5 (2.85) | 3.85 |
| PI | 0.64-3.36 (1.29) | 0.23-3.15 (1.16) | 2.15 |
| gradient (mmHg) | 0.14-2.21 (0.52) | 0.02-16.8 (0.91) | WITHDRAWN (Section 16) -- descriptive only |

**As expected, biological variability gives meaningfully WIDER bands than
epistemic uncertainty** for every index except S/D/PI (which are ratios,
partly self-normalizing against the amplitude swings) -- e.g. the
gradient's 95th percentile is 2.2mmHg (epistemic) vs. 16.8mmHg
(biological), and PS's is 99.8 vs. 180.2. This is the physically-expected
pattern: not knowing the true population-mean diameter precisely (epistemic)
is a smaller source of variation than the diameter genuinely varying from
fetus to fetus (biological). **~11% (17/150) of the biological run's
samples are numerically-stiff outliers** (PS>150, tracing to the log-
normal's own right tail combined with low-compliance draws) -- a higher
rate than the epistemic run's ~4%, expected given the biological
distribution's genuinely wider spread; noted, not hidden, and not
re-filtered given the diminishing-returns point already reached on this
analysis.

**Interpretation, both analyses**: PS's median and 90% interval bracket
the target reasonably in both cases, reinforcing that the zero-fitting
point estimate (41.6) is not an isolated lucky value under either
uncertainty framing. PI's interval spans the 2.15 target in both cases,
but (as in the original Section 18 analysis) the samples that reach it
do so only by badly breaking S/D -- the same irreducible trade-off
documented in Section 17's factorial study, now reconfirmed under BOTH
epistemic and biological uncertainty framings, not just one. The pressure
gradient's bands are reported descriptively only, per Section 16's
withdrawal of any quantitative target.

## 19. Reviewer round 4: dataset reconciliation and the multivariate/Jensen's-inequality finding

### 20.1 Dataset reconciliation

The reviewer independently recomputed statistics from `anonymized_doppler_data.csv`
and found the S/D mean did not reproduce 3.85 (getting 3.68 instead), and
flagged the 23-vs-24-vs-29 count inconsistency. Investigated by going back
to the original xlsx directly:

- **Not a data bug.** The original xlsx's own "Modified Data" SUMMARY row
  (computed by the original clinical authors) gives PS_mean=41.3196,
  ED_mean=13.0463, S/D_mean=3.8492, PI_mean=2.1542 -- and recomputing these
  same statistics directly from `anonymized_doppler_data.csv` with pandas
  (`.mean()`, which skips missing values per-column) reproduces ALL FOUR
  numbers exactly. The anonymization/extraction pipeline has no error.
- **The actual counts, corrected** (validation_targets.json previously said
  "24 patients with data," a bookkeeping error in that file, not a data
  error): of 29 total patient identifiers, **23 have recorded PS/ED/PI**,
  and **22 have a recorded S/D value** -- one patient (anonymized
  Patient12: PS=44.68, PI=3.75) has PS/ED/PI but NO S/D value, a
  pre-existing gap in the original clinical spreadsheet (not an exclusion
  performed during this project's anonymization). `validation_targets.json`
  corrected accordingly.
- **Why the reviewer got 3.68**: dividing the sum of the 22 available S/D
  values by 23 (i.e. using the wrong, PS-based denominator for a
  statistic that has one fewer valid observation) gives 84.68/23=3.68.
  Using the CORRECT, index-specific denominator (22, excluding Patient12
  who lacks this specific value) gives 84.68/22=3.85, matching the
  original clinical summary exactly. Both this project's numbers and the
  reviewer's recomputation are arithmetically consistent with each other
  once the correct per-index n is used -- there was no missing "24th
  record" to find, just a subtle off-by-one in which denominator applies
  to which index.
- **"Outlier-adjusted"**: refers to the original xlsx's own "Modified
  Data" section (used throughout this project, vs. the sheet's separate,
  unused "Original Data" section) -- the original clinical authors' own
  correction of individual triplicate sign-flip/measurement errors, per
  the sheet's own embedded notes ("Values in orange are modified data").
  This project did not perform any additional exclusions beyond using this
  pre-existing, clinician-corrected section.
- **Cohort size is index-specific, not one universal number**: n=29 total
  identifiers; n=23 for any table involving PS, ED, or PI; n=22 for any
  table involving S/D specifically. Report tables should state this
  explicitly per row/column rather than a single blanket "n=24."

### 20.2 The deeper point: Jensen's-inequality averaging artifact -- confirmed, and a major reframing

The reviewer's more important point, independent of the counting question:
**mean(PS)/mean(ED) != mean(S/D)** in general, since S/D is a per-patient
NONLINEAR ratio. Confirmed numerically on the complete-case (n=22, all
four indices present) subset: ratio of means PS/ED = **3.018**, vs. mean of
the per-patient S/D values = **3.849**. **No single representative
waveform can simultaneously have PS=41.3, ED=13.6 (this subset's own
marginal means), AND S/D=3.85** -- S/D is fully determined by PS/ED once
those two are fixed for any one waveform, so three independently-averaged
marginal targets are mutually over-determined by construction, not because
of any model limitation. This is stated explicitly here, per the
reviewer's requirement, rather than left implicit.

**Built the internally-consistent alternative** (`multivariate_comparison.py`):
patient-level (PS,ED,S/D,PI) vectors for the n=22 complete cases, their
covariance/correlation structure, and the simulated model's Mahalanobis
distance from that multivariate distribution (rather than four independent
marginal percentage errors, which is what Sections 6-19's "score" metric
effectively did, and which is now understood to be a statistically naive
comparison given the Jensen's-inequality issue above).

**Correlation structure among the real patients' own indices** (n=22):
PS-ED: +0.70 (both scale with overall flow, as expected); PS-S/D: -0.27;
PS-PI: -0.42; ED-S/D: -0.60 (strong, expected: S/D=PS/ED, so higher ED at
similar PS mechanically lowers S/D); ED-PI: -0.47; **S/D-PI: only +0.11**
(these two "pulsatility" indices are only weakly correlated with each
other even in the REAL patient data -- a useful empirical calibration for
how independent these clinically-related-sounding indices actually are).

**The headline result**: the current zero-fitting simulated vector
(PS=41.58, ED=10.53, S/D=3.95, PI=1.42) has a **Mahalanobis distance of
1.80** from the n=22 patient-level distribution. **The medoid patient**
(the single REAL patient whose own vector is most "central"/typical within
the cohort, found by minimizing total Mahalanobis distance to all other
patients -- Patient29: PS=37.93, ED=14.21, S/D=3.89, PI=1.87) has a mean
distance to all OTHER patients of **1.81** -- statistically
indistinguishable from the simulated model's distance. **Empirically, the
simulated point is farther from the cohort centroid than only 55% of the
real patients themselves are** -- i.e., by the proper multivariate metric,
this zero-fitting model prediction is about as "typical" a member of this
patient population as the most representative actual patient in it.

Univariate z-scores confirm which index actually drives the (modest)
overall distance: PS z=+0.03, S/D z=+0.10 (both excellent), ED z=-0.41
(unremarkable), **PI z=-1.23** (the one index more than 1 SD from the
patient-level mean -- consistent with every other analysis in this
project, but notably NOT an extreme outlier even in the patient population
itself).

**This substantially reframes how the model's fit should be reported.**
The "four independent marginal percentage errors" framing used throughout
Sections 6-19 (e.g. "PS +0.6%, ED -19%, S/D +2.6%, PI -34%") is not wrong
as a set of individual facts, but IMPLICITLY treats the four targets as
independently achievable, which the Jensen's-inequality result above shows
they are not, even in principle, for a single representative waveform.
**The multivariate comparison is the scientifically correct way to state
this model's overall fit, and it is considerably more favorable than the
marginal-error framing suggested.** PI remains the one genuinely
under-performing index (z=-1.23), but this should be reported as a
specific, isolated, moderate deviation within an otherwise well-fitting
multivariate prediction -- not summed together with three other
"discrepancies" that are, on inspection, largely an artifact of comparing
one waveform against separately-averaged marginal statistics.

## 20. Terminology corrections (reviewer round 3) -- apply retroactively when reading Sections 11-15

Two precision corrections, applied going forward rather than by rewriting
every historical mention (this document's established practice of layering
corrections rather than erasing history):

1. **"RLC" -> "coupled nonlinear RL."** The DA element has resistance (R_da)
   and inertance (L_da) only -- there is no separate DA-level compliance
   state (DA compliance is, by design, folded into `C_pa`/`C_ao` instead,
   as already noted where the model was introduced). Every "RLC" in
   Sections 11-15 above should be read as "RL, with compliance accounted
   for in the adjacent compartments," not as a claim that the DA element
   itself has its own compliance term.
2. **"Joint identifiability analysis" -> "joint sensitivity/response-surface
   analysis."** Section 13.2's 40-point `area_scale` x `discharge_coeff`
   grid (and Section 15's re-run) is a sensitivity/response-surface scan,
   not a complete identifiability analysis -- true identifiability requires
   uncertainty quantification, parameter correlations, and ideally a
   likelihood-based or Bayesian treatment, none of which has been done.
   Every "identifiability" in Sections 10-15 describing that 2D grid should
   be read with this caveat.

**Also, a physics point to carry forward correctly** (reviewer round 3):
inertance CANNOT sustain a persistent mean pressure difference over a
periodic cycle -- `<L*dQ/dt> = 0` when averaged over a full period, by
construction (the inductor's voltage-time integral over one cycle is zero
in steady state). Inertance can alter WAVEFORM SHAPE (and, through the
nonlinear R_da loss term's dependence on the resulting flow shape,
influence the cycle-mean pressure loss indirectly) -- but it is not itself
an independent source of a persistent gradient. Any future discussion of
"inertance explaining the pressure gradient" must be phrased through this
indirect, shape-mediated mechanism, not as a direct effect.

## 21. Reviewer round 5: Mahalanobis analysis corrected (not disputed)

Section 19's claim that the model's distance was "statistically
indistinguishable" from the medoid patient's own distance was WRONG in a
specific, technical way, correctly identified by the reviewer: it compared
two non-comparable quantities (model-to-cohort-centroid distance vs. one
patient's mean distance to all others), with no hypothesis test or
uncertainty interval attached to either number. **Withdrawn, and replaced
with the reviewer's specified analysis** (`multivariate_comparison_v2.py`):

1. **Leave-one-out (LOO) reference distribution**: for each of the n=22
   complete-case patients, the population mean/covariance is estimated from
   the OTHER 21 patients only, and that patient's own squared Mahalanobis
   distance (D^2) from that independent, out-of-sample estimate is
   computed. This gives a proper empirical distribution of "how far a
   genuine cohort member typically sits from an independent estimate of
   their own cohort" -- LOO D^2 ranges from 0.09 to 50.79 across the 22
   patients (median 0.72; the large maximum reflects genuine clinical
   outliers in real patient data, not a modelling artifact).
2. **Shrinkage covariance** (Ledoit-Wolf): used throughout, given n=22 is
   small relative to 4 correlated variables (the raw sample covariance
   matrix is poorly conditioned at this n/p ratio) -- shrinkage intensity
   0.27 for the full-cohort estimate (0=raw sample covariance, 1=fully
   shrunk to a diagonal/uncorrelated target).
3. **The model's squared Mahalanobis distance** from the full-cohort
   (shrinkage) mean/covariance estimate: **D^2 = 0.32**.
4. **Empirical percentile**: the model's D^2 sits at the **27th percentile**
   of the LOO patient-distance distribution -- i.e. **73% of the real
   patients in this cohort sit farther from an independent estimate of
   their own cohort than the model does.** This is the correct, defensible
   version of the claim Section 19 was reaching for, and if anything it is
   a STRONGER statement than the withdrawn one: by this like-for-like,
   out-of-sample comparison, the model is closer to "typical" than most
   individual patients are.
5. A chi-squared(4) reference value is reported for context only (p=0.988
   upper-tail for the model's D^2) -- explicitly NOT the primary claim,
   since multivariate normality of n=22 real clinical measurements is not
   itself verified, and the empirical LOO percentile above is the primary,
   distribution-free result.

**Univariate z-scores (unchanged from Section 19, still informative)**: PS
z=+0.03, S/D z=+0.10, ED z=-0.41, PI z=-1.23 -- PI remains the one index
more than 1 SD from the patient-level mean, consistent with every other
analysis in this project.

**Action**: `multivariate_comparison.py` (the flawed version) is superseded
by `multivariate_comparison_v2.py`. All manuscript text describing this
result must use the corrected framing (D^2=0.32, 27th percentile / 73% of
patients farther, NOT "statistically indistinguishable from the medoid").

## 22. Reviewer round 5: full clinical dataset documentation

Re-examined the original xlsx's "Original Data" vs. "Modified Data" sections
directly (matched by patient identity internally, never printed -- only
anonymized `PatientNN` IDs and aggregate counts appear below or anywhere
else, per this project's standing PII policy).

**What constituted an "outlier"**: in every one of the 12 affected patients
(out of 29 total), the correction was a SIGN FLIP of exactly one triplicate
PS or ED measurement (never both in the same patient) from negative to its
absolute (positive) value -- e.g. anonymized Patient07: PS triplicate
(52.66, 39.21, **-24.79**) -> (52.66, 39.21, **24.79**); Patient16: ED
triplicate (7.12, 12.09, **-9.65**) -> (7.12, 12.09, **9.65**). In every
case, the flagged value was the ONLY negative reading among that patient's
own triplicate set, inconsistent with the other two readings and with the
expected physiology of continuous forward (PA-to-Ao) DA flow -- consistent
with a sign-convention/data-entry artifact in the raw acquisition, not a
genuine flow reversal.

**No value was excluded or replaced with a different magnitude** -- the
correction is precisely `abs(x)`, confirmed for all 12 cases by direct
comparison. This was performed by the ORIGINAL clinical co-authors (Tang/
Zhang/Ran, CHCWC) as part of their own initial data preparation -- the
"Original Data" and "Modified Data" sections, with each section's own
embedded SUMMARY row, existed in the source spreadsheet exactly as
supplied to this modelling project, BEFORE any model was built or run.
**The correction unambiguously preceded and is independent of this
project's model results** -- there is no possibility of the correction
having been influenced by, or chosen to match, any simulation output.

**Sensitivity analysis using the uncorrected ("Original Data") cohort
statistics** (the original authors' own SUMMARY row for that section):

| Index | Original (uncorrected) | Modified (sign-corrected, used throughout) | Relative difference |
|---|---|---|---|
| PS mean (cm/s) | 42.16 | 41.32 | -2.0% |
| ED mean (cm/s) | 13.98 | 13.05 | -6.7% |
| S/D mean | 3.68 | 3.85 | +4.6% |
| PI mean | 2.154202898550724 | 2.154202898550724 | **exactly unchanged** |

(PI is numerically IDENTICAL to the last displayed digit between the two
sections -- indicating the per-triplicate PI values were entered
independently of the PS/ED sign convention, not recalculated from them.)

The model's zero-fitting result compared against the UNCORRECTED targets:
PS 41.58 vs. 42.16 (-1.4%, vs. +0.6% against the corrected target), ED
10.53 vs. 13.98 (-24.7%, vs. -19% against the corrected target), S/D 3.95
vs. 3.68 (+7.3%, vs. +2.6%), PI unchanged (-34% either way). **The
qualitative conclusion is unaffected by which version of the data is
used**: PS and S/D remain within ~10% under both, ED and PI remain the
weaker indices under both.

**Ethics, consent, and reporting details -- documented as far as available
project materials allow, not fabricated beyond them**:
- Ethics approval: per the original study protocol
  (`../blood flow simulation for the DA.docx`), "The study has been
  approved by the ethics committee of CHCWC [Chongqing Health Center for
  Women and Children]." **No specific approval/reference number is present
  in any project material available to this analysis** -- this must be
  supplied by the clinical co-authors (Tang/Ran, CHCWC) before submission;
  not fabricated here.
- Consent: retrospective review of anonymous ultrasound scans, per the
  same protocol document. No explicit consent/consent-waiver statement
  language is present in available materials -- needs confirmation from
  the clinical co-authors (a consent waiver is plausible for retrospective,
  anonymized review, but this project cannot assert the exact wording used
  by the CHCWC ethics committee).
- Inclusion/exclusion criteria: the protocol states "24 fetuses at the end
  of the first trimester" (the actual reconciled count with any DA
  measurement is 23, Section 20) -- no further explicit inclusion/exclusion
  criteria (e.g. exact GA window boundaries, structural-anomaly exclusion)
  are documented in available materials. Needs confirmation from the
  clinical co-authors, not assumed here.
- Acquisition equipment/settings: a single real clinical exemplar image
  elsewhere in this project (a different scan, GA=24w0d, not part of this
  23-fetus cohort) shows a Voluson-series system in use by the same
  clinical department -- suggestive of the likely equipment family, but
  NOT confirmed to be the specific system/settings used for this cohort's
  actual scans. Should be stated as such, not asserted as confirmed.

**Data and code availability**: this project's code (geometry, model,
calibration, sensitivity/uncertainty/factorial-study scripts) is intended
to be made available, following this session's established precedent for
the sibling CoA project (a public GitHub repository, MIT-licensed, with a
citation-request notice). No patient-level data would be included or
required (all validation targets are cohort-level summary statistics,
already anonymized). **Actually publishing a public repository is a
separate action requiring the user's explicit go-ahead** (per this
session's standing practice for any public-facing action) -- not done
unilaterally as part of this documentation pass.

## 23. Reviewer round 6: Mahalanobis analysis corrected AGAIN -- standardization before shrinkage

Section 21's corrected analysis (LOO, Ledoit-Wolf shrinkage, D^2=0.32,
27th percentile) was itself flawed in a way the reviewer correctly
identified: **Ledoit-Wolf shrinkage toward a scaled-identity target is not
invariant to variable scaling**. PS/ED (cm/s, large variance) and
dimensionless S/D/PI were fed to `LedoitWolf().fit()` without
standardization, so the large-variance velocity variables dominated the
shrinkage regularization differently than S/D/PI would.

**Fixed** (`multivariate_comparison_v3.py`): at every step (both within each
LOO fold and for the full-cohort model comparison), variables are
standardized (z-scored) using ONLY the relevant training-set mean/SD before
Ledoit-Wolf shrinkage is fit; the held-out patient (or the model) is then
standardized using that SAME training-set mean/SD (not its own), and the
squared Mahalanobis distance is computed in standardized space throughout.

**Independently reproduced the reviewer's corrected numbers exactly**
(computed from scratch, not copied): shrinkage intensity rises to 0.658
(standardized) from 0.27 (unstandardized, Section 21); LOO squared distance
across the 22 patients: min=0.29, **median=2.52**, max=65.07; **model's
squared Mahalanobis distance = 1.99** (not 0.32); **empirical percentile =
41%** (not 27%) -- i.e. **59% of real patients** (not 73%) sit farther from
an independent estimate of their own cohort than the model does.

**Still a favorable, defensible result, just more moderate**: the model
remains centrally located within the patient population (below the median
LOO distance of 2.52), just not as extremely central as the unstandardized
calculation wrongly suggested. The chi-squared(4) reference value is
REMOVED entirely per the reviewer -- not reliable after shrinkage and
small-sample LOO construction; the empirical percentile is the sole
reported statistic going forward.

**Action**: `multivariate_comparison_v2.py` (unstandardized shrinkage) is
now superseded by `multivariate_comparison_v3.py`. All manuscript text
must use D^2=1.99 / 41st percentile / 59% farther / LOO median=2.52 -- NOT
the Section 21 numbers.

## 24. Reviewer round 6 (continued): code-manuscript mismatch and procedure consistency, fixed

**Code-manuscript mismatch, fixed**: `multivariate_comparison_v2.py` (the
unstandardized-shrinkage script) still reproduced the obsolete D^2=0.32/
27th-percentile result if run, while the manuscript reports the corrected
standardized result -- a real repository-hygiene problem the reviewer
caught (whoever runs the deposited code must get the manuscript's numbers).
Fixed by adding explicit "SUPERSEDED -- DO NOT USE" headers to
`multivariate_comparison.py` and `multivariate_comparison_v2.py`, and a
"CANONICAL SCRIPT" header to `multivariate_comparison_v3.py`, making
unambiguous which file is the one whose output should be cited/deposited.

**Methods/Results procedure inconsistency, fixed**: Methods 2.6 described
standardizing the model itself WITHIN each LOO training fold (implying 22
different model distances), while Results 3.3 reports ONE model distance
from full-cohort standardization -- an internal inconsistency the reviewer
caught. Fixed Methods 2.6 to describe the actual PRIMARY procedure
correctly (full-cohort standardization for the model's single D^2=1.99,
placed within the LOO distribution of patients' own out-of-sample
distances) and added the paired-fold approach as an explicitly-labeled
SECONDARY sensitivity check.

**Paired-fold sensitivity check, computed and added** (`multivariate_comparison_v3.py`'s
new `paired_fold_sensitivity()` function): recomputing the model's D^2
WITHIN each of the 22 LOO folds (using that fold's own training-set
standardization for the model too, not the full cohort) gives model
D^2 ranging 1.84-2.44 across folds (mean 2.01), with the held-out patient
farther than the model in 59% of folds -- independently reproducing the
reviewer's quoted range exactly, and confirming the primary (full-cohort)
result is not an artifact of that specific standardization choice. Added
to Results 3.3.

## 25. Remaining submission blockers (reviewer round 6) -- status

Per the reviewer's final punch list:
1. **Ethics committee name, approval number, consent/waiver wording,
   confirmed eligibility criteria** -- STILL NOT AVAILABLE in any project
   material; must come from the clinical co-authors (Tang/Ran, CHCWC).
   Not fabricated.
2. **Funding and CRediT contributions** -- placeholder fields added to the
   manuscript's new Declarations section; must be completed by the authors.
3. **Conflict-of-interest confirmation** -- a "no known conflicts" default
   statement is in place, but per the reviewer, every named author must
   personally confirm this before submission.
4. **AI-assistance disclosure, per journal policy** -- a disclosure
   statement is in place (this project's Claude-assisted development);
   the authors should check Physiological Measurement's specific AI-use
   policy and adjust wording/scope if other tools (e.g. OpenAI/Codex) were
   also used at any stage.
5. **Whether Table S1 should move to a separate supplementary file** --
   depends on the journal's specific formatting requirements; not resolved
   here, flagged for the authors to check against Physiological
   Measurement's author guidelines.
6. **Deposit the exact reproducing code in a review-accessible repository
   AT SUBMISSION**, not just after publication -- this project's code is
   ready (and now internally consistent, per Section 24), but actually
   publishing a public/review-accessible repository is a separate action
   requiring the user's explicit go-ahead (this session's standing
   practice for any public-facing action, per the sibling CoA project's
   precedent) -- not done unilaterally here.
7. **Manual Word-rendered equation/figure QA** -- this project's tooling
   cannot visually render the .docx; the user should open the file in Word
   and check equations/figures directly before submission.
