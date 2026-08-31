# Fetal DA model: progress since reviewer round 1

Standalone summary of what changed in response to the reviewer's round-1
feedback (their six-point sequenced critique). Full technical detail lives in
`REPORT_FOR_REVIEWER.md` (Sections 7-8) and `model_plan_and_literature_data.md`
(Sections 8-10) in this same folder, for anyone who wants to check the numbers.

## 0. Naming/framing

Actioned without further discussion: this is a study of normal **fetal** DA
physiology at ~13.5 weeks gestation, not patent ductus arteriosus (PDA) of
prematurity. Made explicit in the plan doc, the model code's docstring, and
will carry into the eventual paper's title/aims/discussion.

## 1. Clinical index definitions (reviewer's Step 1) -- verified, one new lead found

Checked the standard obstetric-Doppler formulas (S/D = PS/ED, RI = (PS-ED)/PS,
PI = (PS-ED)/TAMX) against a real machine readout already in this project
(one clinical exemplar, GA=24w0d) -- all three matched the machine's own
displayed values to 2-3 significant figures. **Our formula structure was
already correct.**

This surfaced a more useful, still-open lead: clinical PS/ED are near-
centerline (velocity-profile-peak) values, while our model reports the
cross-sectional MEAN velocity (q/A) -- a physically different quantity. A
phase-dependent profile-correction factor (larger at low-velocity diastolic
flow than at high-velocity systole) is a plausible, not-yet-quantified,
candidate explanation for part of the remaining velocity mismatch.

Also checked: raw per-patient waveforms are not available in this project's
data (only pre-computed triplicate summary indices per patient), so
recomputing indices from raw traces, as suggested, isn't possible here.

## 2. Boundary-condition redesign (reviewer's Step 2, their top priority) -- built and largely validated

**What was wrong**: the model's inlet was a directly-prescribed flow
waveform, with no real connection between the simulated pressure and the
known ~5mmHg fetal PA-over-Ao pressure excess (Rudolph 1979) -- exactly the
reviewer's point that "a prescribed-flow inlet plus one reflection
coefficient cannot independently represent pulmonary and systemic
circulations."

**What was built**: a lumped two-compartment model -- one compartment for
the pulmonary artery (fed by RV ejection), one for the aorta/systemic side
(fed by LV ejection) -- connected by an orifice/Bernoulli-type DA relation,
parameterized from real, independently-sourced literature (Vimpeli et al.
2009's directly-measured fetal cardiac output and RV:LV ratio data), NOT
fit to the Doppler targets. DA flow now genuinely EMERGES from the pressure
difference between the two compartments, feeding into the existing (still
unmodified) 1D DA tube solver.

**Result**: the two-compartment model's own pressure gradient converges to
**5.4mmHg** (target ~5mmHg) with continuous, non-reversing forward flow --
both real, non-fitted consequences of the physiology, not tuned to match.
This also explained WHY the original pressure cross-check had failed: the
1D tube's own pressure field uses one uniform baseline for the whole vessel,
so comparing its two ends can only ever report the DA's own tiny local
compliance effect (~0.1mmHg) -- it structurally cannot see the two different
pressure ENVIRONMENTS its ends actually sit in. The true PA-to-Ao pressure
difference is the compartment-level gradient (5.4mmHg) plus that small local
term, which resolves the original discrepancy architecturally.

**New problem this exposed, not yet solved**: the resulting DA velocities
are far below the Doppler targets (peak-systolic ~14 cm/s vs. the cohort's
41.3 cm/s). Because the two-compartment parameters were deliberately kept
literature-derived rather than fit to the Doppler data (to avoid exactly the
calibration/validation conflation the reviewer flagged), this gap is being
reported honestly rather than closed by re-tuning. Three candidate
explanations, not yet distinguished: underestimated first-trimester cardiac
output/shunt fraction (the literature values used were extrapolated from
11-20 week data), the mean-vs-peak velocity profile issue from Step 1, or a
vena-contracta-type effective orifice area smaller than the DA's full
anatomical lumen (consistent with the known constriction where the DA joins
the aorta).

## 3. Identifiability/sensitivity analysis (Step 3) -- a genuine split result

Local sensitivity sweep across the model's key parameters found:
- **Peak-systolic velocity is well-behaved**: predictable, proportional
  response to cardiac output/RV:LV ratio/shunt fraction, and (correctly)
  almost no response to DA wall stiffness.
- **End-diastolic velocity, S/D, and PI are not well-behaved**: their
  response to DA wall stiffness is large and, critically, FLIPS SIGN
  between a +20% and -20% perturbation of the same parameter -- the
  signature of a non-identifiable relationship, not a stable one. These
  three indices cannot currently be considered reliably recoverable.
- A genuine (not a bug) model fragility: independently nudging PA or Ao
  pressure the wrong way can flip the assumed pressure ordering and
  collapse DA flow to zero.

## 4. Cross-validation (Step 4) -- limited but not alarming

4-fold cross-validation of the Doppler-fit model (refitting only the flow-
amplitude parameter per fold, since refitting all 4 free parameters per fold
wasn't computationally affordable -- a disclosed limitation of this test).
Out-of-sample error is moderately worse for peak-systolic velocity and PI,
about unchanged for end-diastolic velocity and S/D. No strong sign of gross
overfitting, but this is a partial test, not a full nested cross-validation.

## 5. Uncertainty propagation (Step 5) -- the most decisive result so far

A 40-sample Monte Carlo across five literature-bounded parameters (cardiac
output, RV:LV ratio, DA shunt fraction, the assumed PA-Ao pressure gradient,
DA wall stiffness) found:
- **The pressure gradient is robust across the entire plausible parameter
  space** -- its 90% interval (3.6-7.3mmHg) comfortably brackets the ~5mmHg
  literature target. This is strong evidence the Step 2 fix is real, not a
  lucky single point estimate.
- **The velocity gap cannot be closed by staying within plausible
  parameter bounds** -- even at the optimistic end of the sampled range,
  peak-systolic velocity reaches well under half the target. This rules out
  "just retune within reasonable ranges" and reinforces that one of the
  three structural explanations from Step 2 is genuinely needed.

## Where this leaves the model

Split verdict, deliberately not averaged into one label: **mechanistic for
the pressure gradient** (sourced, robust, not fit to data), **still
phenomenological for the velocity/shape indices** (peak-systolic velocity at
least predictable; end-diastolic velocity/S-D/PI additionally fragile and
not currently identifiable). Step 6 (revisiting the inlet waveform) has
deliberately not been touched further, per the reviewer's own instruction to
hold off until the above was in place.

**Question for the reviewer**: which of the three velocity-gap
explanations (flow/shunt-fraction underestimate, mean-vs-peak profile
correction, or effective-orifice/vena-contracta effect) is worth pursuing
first, or is there a different one worth considering?
