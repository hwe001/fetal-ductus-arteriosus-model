# Fetal DA model: progress since reviewer round 2

Standalone summary of what changed in response to the reviewer's round-2
critique (circularity, one-way coupling, and methodological concerns about
the Section 10 analyses). Full technical detail lives in
`REPORT_FOR_REVIEWER.md` (Sections 9-12) and `model_plan_and_literature_data.md`
(Sections 11-15) in this same folder.

## 1. Circularity and one-way coupling -- accepted, not disputed

The round-1 "resolved" framing was wrong. The 5.4mmHg pressure gradient had
been back-calculated FROM two compartment pressures assumed specifically to
produce ~5mmHg -- circular, exactly as the reviewer identified (the
uncertainty sweep sampling 3-7mmHg and returning 3.6-7.3mmHg was the
smoking gun). The 0D-compartments-to-1D-tube architecture was also correctly
identified as one-way forcing, unable to enforce flow and pressure
continuity simultaneously, with a real risk of double-counting. Both
corrected in the documentation rather than defended.

## 2. Architecture rebuilt: a single, genuinely coupled 0D model

Given a choice between (A) a fully coupled two-sided-impedance 1D model or
(B) a simpler single 0D RLC DA element, chose (B) -- also supported by a
structural finding: the DA is "acoustically short" (wave-transit time under
0.5% of the cardiac cycle), so the extra complexity of 1D wave propagation
isn't obviously buying real physics for this specific vessel.

Built a single system of three simultaneously-integrated equations (PA
pressure, Ao pressure, DA flow with genuine inertance and a nonlinear
orifice/Bernoulli loss term) -- flow and pressure are now solved together,
not staged. De-circularized by anchoring both compartments' resistances to
ONE shared baseline pressure (not two independently chosen to produce a
target gradient), with only the independently-sourced flow split (real
cardiac output/RV:LV data) differing between the two sides. Any resulting
pressure gradient is now a genuine model output, not a foregone conclusion.

This architecture change alone -- before any further correction -- shrank
the velocity gap from ~3x to ~2.1x, just from replacing an instantaneous
algebraic flow relation with real inertial dynamics.

## 3. Geometry/measurement audit -- an independent cross-validation

Investigated the reviewer's own suggested first step and found:

- The literature source used for DA diameter (Szpinda 2007) measures
  **external** diameter on postmortem, fixed specimens -- not the internal/
  luminal diameter that determines flow velocity. The code had been using
  it as if it were internal diameter, with no correction -- a real,
  previously undocumented gap between what the project's own notes claimed
  and what the code actually did.
- A second, previously-unread paper in this project's own literature
  folder (Leao et al. 2015) measures DA diameter specifically at the
  narrowest point (the aortic junction), not an along-length average. Its
  directly-measured value for this cohort's gestational-age range gives a
  diameter ratio of 0.679 relative to the original geometry source.

That number was derived with zero reference to the Doppler data. Separately,
fitting peak-systolic velocity alone (no anatomical information) had
required a diameter ratio of 0.68. **Two completely independent routes
agreed to within 0.2 percentage points.**

Switching to this literature-sourced geometry and re-running with every
parameter independently sourced (real cardiac output data, real anatomical
length, this corrected throat diameter, a standard orifice discharge
coefficient, one shared baseline pressure) -- **zero fitting to the Doppler
targets anywhere in the chain** -- gives peak-systolic velocity within 1%,
end-diastolic velocity and S/D ratio within ~10-20% (see Section 4 below for
the fully corrected numbers), using nothing but independently-sourced
literature.

## 4. Numerical convergence and ED-definition fix -- and an honest correction

Checked, as the reviewer requested, whether the earlier sensitivity results
were properly converged. Fixed a real methodological issue along the way:
end-diastolic velocity had been computed as an averaged window (final 15%
of the cycle) rather than the clinical instantaneous end-diastolic sampling
convention. Direct inspection confirmed this window-average was inflating
the reported ED value. Fixed it -- and it made the ED fit look WORSE (a
real, previously-hidden discrepancy, correctly exposed), while S/D happened
to improve only as an arithmetic side-effect of the lower ED, not genuine
progress. Reporting this plainly rather than only reporting the numbers
that improved.

Confirmed full numerical convergence: RK4 timestep resolution agrees to the
4th decimal place across a 16x range of step counts; cycle-to-cycle
convergence is under 0.001%. Re-ran the full joint identifiability grid with
both fixes in place -- the "no further fitting" default configuration
scores essentially tied with the best point in the entire 40-point grid,
confirming the Section 3 result above wasn't a lucky or cherry-picked point.

## 5. Current honest state of the model

With the ED-definition fix applied (i.e. these are the final, corrected
numbers, not the earlier flattered ones), and zero parameters fit to the
Doppler targets:

| Index | Simulated | Target | Error |
|---|---|---|---|
| Peak-systolic velocity | 41.6 cm/s | 41.3 cm/s | **+0.6%** |
| End-diastolic velocity | 10.5 cm/s | 13.1 cm/s | -19% |
| S/D ratio | 3.95 | 3.85 | **+2.6%** |
| Pulsatility index (PI) | 1.42 | 2.15 | **-34%, unresolved** |
| PA-Ao pressure gradient | 0.46 mmHg | ~5 mmHg | **still short, unresolved** |

Two findings are now well-established and robust (confirmed across a
40-point joint identifiability grid, full numerical convergence, and two
independent geometry sources):

1. **PI does not respond to throat geometry or discharge coefficient at
   all** -- it stays between 1.3 and 1.4 across the ENTIRE tested parameter
   range (area scale from 0.15x to 1.0x, discharge coefficient 0.5-0.9),
   never approaching the 2.15 target anywhere. The leading untested
   hypothesis is that the DA's inertance term is damping/smoothing the
   transmitted pulsatility, or that the ventricular ejection waveform shape
   itself needs revisiting -- neither tested yet.
2. **The pressure gradient remains genuinely short** of the ~5mmHg
   reference even at the anatomically-corrected geometry, and needs either
   a smaller effective area still, a lower discharge coefficient, or a
   mechanism not yet in the model -- it does not resolve simultaneously
   with the velocity gap using the same parameters.

## Question for the reviewer

Given this state -- three of four velocity/shape indices within ~10-20% of
target using entirely independently-sourced parameters, but PI and the
pressure gradient both unresolved and behaving as clean, isolated (not
confounded) problems -- what would be the most valuable next step: (a)
testing the inertance-damping hypothesis for PI directly, (b) revisiting
the ventricular ejection waveform shape (your Step 6, now that the
architecture/geometry/convergence work is in place), (c) a further push on
the pressure-gradient gap specifically, or (d) treating the model as
sufficiently developed to begin drafting the paper's claim (Step 5) around
what has and hasn't been resolved?
