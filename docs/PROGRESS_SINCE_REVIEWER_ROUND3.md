# Fetal DA model: progress since reviewer round 3

Standalone summary of the full response to the reviewer's round-3 feedback,
which followed their own recommended priority order: pressure-reference
audit -> inertance/compliance/waveform factorial study -> uncertainty
analysis -> manuscript. Full technical detail lives in
`REPORT_FOR_REVIEWER.md` and `model_plan_and_literature_data.md`
(Sections 16-19) in this same folder.

## 1. The ~5mmHg pressure target is withdrawn

The reviewer's own Bernoulli consistency check found that our cohort's
observed peak velocity (~0.42 m/s) is physically compatible with only a
~0.7-1.4mmHg gradient -- while a genuine 5mmHg gradient would imply a
velocity nearly 3x higher than anything observed in this cohort. The two
numbers could not both be locally correct for the same vessel. We traced
the "~5mmHg" figure to its source: Rudolph AM, "Fetal and neonatal
pulmonary circulation," *Annu Rev Physiol* 1979 -- a review built on the
chronically-instrumented **fetal LAMB** preparation (human fetal cardiac
catheterization is not ethically or technically feasible at any
gestational age), and one near-universally applied in the **last third**
of gestation, not first-trimester. Species mismatch and gestational-stage
mismatch are each independently sufficient to disqualify this figure as a
quantitative target for our 13.5-week human cohort. No human first-
trimester data exists, or plausibly can exist, given the measurement's
infeasibility -- a permanent evidence gap, not a search failure.

**Result**: the ~5mmHg gradient is withdrawn as a validation criterion.
Our model's own emergent gradient (0.46mmHg) is no longer a "shortfall" --
there is no legitimate number to fall short of, and by the reviewer's own
Bernoulli check, it is broadly consistent with the velocity scale we
actually observe.

## 2. PI factorial study: inertance refuted, RV/LV timing is the standout finding

Ran the reviewer's full requested hierarchy on the corrected, de-
circularized coupled model: DA inertance (0.1-2x theoretical), PA/Ao
compliance (joint and independent, 0.1-10x), the shared resistance
baseline (15-50mmHg, preserving the independently-sourced flow split),
systolic duration and ejection sharpness, and RV/LV relative timing/shape
(previously always identical and perfectly synchronized -- untested until
now).

- **Inertance: cleanly refuted as a mechanism.** Varying it across a 20x
  range changed PI by less than 0.05 and left TAMX (the key diagnostic
  metric) completely unchanged -- direct experimental confirmation of the
  reviewer's theoretical point that inertance cannot sustain a persistent
  mean-level effect over a periodic cycle.
- **Compliance: powerful but destabilizing**, exactly as the reviewer
  warned it might be. One point hit PI almost exactly on target while
  simultaneously breaking S/D and ED badly. No compliance value improves
  PI without a comparable cost elsewhere.
- **The clearest, most consequential finding: RV/LV relative ejection
  timing.** We had always assumed the two ventricles eject in identical,
  perfect synchrony -- an assumption never previously tested. A timing
  offset of just 10-15% of a cardiac cycle alone moves PI from 1.42 up
  through 2.7 to 3.2 -- the largest effect of any factor tested, and a
  previously-unexamined modelling simplification rather than a new free
  parameter.
- **Honest bottom line**: re-scaling flow amplitude after any PI-improving
  change (shorter systole, or the RV/LV timing offset) does pull PI toward
  target, but ED and S/D get correspondingly worse every time. No
  combination tested beats the current zero-fitting baseline's overall
  score. This looks like a genuine structural property of this model
  family -- the same three-way tension first identified all the way back
  in the original (v1/v2) waveform calibration, now independently
  rediscovered in a completely different, more physically-grounded
  architecture.

## 3. Terminology corrected

The model is now consistently described as a coupled **nonlinear RL**
element (resistance + inertance; compliance is folded into the two
compartments, not a separate DA-level state) -- not "RLC," which had been
used loosely. The 40-point parameter grid from round 2 is now described as
a joint **sensitivity/response-surface** scan, not an "identifiability
analysis" -- true identifiability would need uncertainty quantification,
parameter correlations, and ideally a likelihood-based or Bayesian
treatment.

## 4. Uncertainty propagation -- including an honest mid-analysis correction

150-sample Monte Carlo over the genuinely uncertain, independently-sourced
parameters (cardiac output, RV:LV ratio with its own literature-reported
uncertainty, throat diameter, discharge coefficient, DA shunt fraction, the
unsourced baseline pressure, and PA/Ao compliance).

**A real error was caught partway through and fixed, not hidden**: the
first attempt sampled throat diameter using Leao et al.'s reported
between-specimen standard deviation (0.55mm on a mean of 0.93mm) directly.
This let physically implausible small-diameter samples through and
produced non-physical outputs (simulated peak velocity up to 337 cm/s,
roughly 8x the cohort's own value). The error: this model represents one
representative fetus, not per-patient variation, so the correct quantity
to propagate is the standard error of the mean (SEM = SD/sqrt(n) =
0.174mm), not the raw between-specimen SD. Re-ran with the correction.

**Results (corrected run, n=150)**:

| Index | 5th pct | median | 95th pct | Target |
|---|---|---|---|---|
| Peak-systolic velocity | 20.3 | 45.4 | 96.4 cm/s | 41.3 cm/s |
| End-diastolic velocity | 3.8 | 11.7 | 26.3 cm/s | 13.1 cm/s |
| S/D ratio | 1.80 | 3.28 | 14.2 | 3.85 |
| PI | 0.62 | 1.23 | 3.33 | 2.15 |
| PA-Ao gradient | 0.13 | 0.49 | 2.29 mmHg | (withdrawn, no target) |

Peak-systolic velocity's median and 90% interval reasonably bracket the
target, consistent with the zero-fitting point estimate sitting near the
middle of a plausible range rather than being an isolated lucky value.
PI's interval does span the target (22% of samples reach PI>=2.15) -- but
checking those samples specifically shows they do so only by driving mean
S/D to 12.0, more than 3x its own target. This is the same irreducible
trade-off found in the factorial study, now independently reconfirmed by
random sampling rather than deliberate search -- if anything, this
strengthens rather than weakens that conclusion.

## Where this leaves the model

All four items in the reviewer's own priority sequence are now complete:
pressure-reference audit, factorial mechanism study, terminology
corrections, and uncertainty propagation. The model's current honest state:

- Peak-systolic velocity and S/D ratio: within ~10% of target using
  entirely independently-sourced, non-Doppler-fitted parameters, and shown
  by Monte Carlo to sit near the middle of a physically plausible range,
  not a cherry-picked point.
- The independent 0.679-vs-0.68 diameter-ratio agreement (anatomical
  literature vs. Doppler-fit) remains, in our view, the strongest single
  result.
- PI (and, more diagnostically, TAMX) remains genuinely unresolved --
  refuted as an inertance effect, shown to trade off against S/D/ED under
  every other mechanism tested, and independently reconfirmed as an
  irreducible tension by the Monte Carlo.
- The pressure-gradient "problem" has been resolved by withdrawal, not by
  fitting -- a legitimate outcome given the audit's findings, not an
  evasion.

## Question for the reviewer

Your own priority order is now complete. Two questions: (1) is this the
point to begin drafting the manuscript around what has and hasn't been
resolved (your suggested framing: coherent reduced-order model,
independent diameter convergence, accurate PS/S-D prediction, PI as
evidence of incomplete waveform-boundary physics), or is there further
modeling work you'd want to see first -- e.g. the joint (not one-at-a-time)
multi-parameter search over compliance/resistance/waveform-shape together,
which the factorial study didn't attempt? (2) Is the RV/LV timing-offset
finding worth a dedicated paragraph or figure in its own right, given it
was the single largest-effect, previously-untested factor found in this
round?
