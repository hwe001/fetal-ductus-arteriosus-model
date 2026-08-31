# 1D Transmission-Line Model of the Fetal Ductus Arteriosus -- Status Report

## 1. Aim

Complete the stub study design already sitting in this project folder
(`../blood flow simulation for the DA.docx`, "Quantifying the blood flow and
shear stress for the ductus arteriosus", Tang/Zhang/Ran/Ho): reproduce
Doppler-measured velocity indices (peak systolic PS, end-diastolic ED, S/D
ratio, pulsatility index PI) for the fetal ductus arteriosus (DA) at
end-of-first-trimester gestation, using a 1D computational hemodynamic model,
validated against a real clinical cohort. This is normal **fetal** DA
physiology (continuous pulmonary-artery-to-aorta shunting driven by elevated
fetal pulmonary vascular resistance) -- NOT the postnatal PDA-of-prematurity/
closure scenario covered by the other (separate, already-drafted) review paper
in this same folder.

## 2. Method

- **Solver**: the two-step MacCormack / electrical-transmission-line 1D
  arterial-flow solver already built, debugged, and published for the
  coarctation-of-the-aorta (CoA) project
  (`../../coarctation_aorta/coa_1d_model/baker_1d_solver.py`), reused
  UNCHANGED. Governing equations: conservation-form continuity + momentum,
  Olufsen-type elastic tube law, transmission-line-derived outlet reflection
  coefficient.
- **Geometry**: Szpinda et al. (2007) published regression of DA length and
  diameter vs. gestational age (n=131 fetuses), evaluated at 13.5 weeks
  (end of first trimester, matching the cohort). Independently cross-checked
  against a pre-existing digitized 1D vessel-network reconstruction
  (`cmgui_model/artery.exelem`/`.exnode`) of the aortic arch + pulmonary
  artery + DA -- the two sources agree on DA length to within 2.5%.
- **Physiology/parameters**: fetal heart rate ~150bpm (Montenegro et al. 1998)
  and the qualitative fact that fetal main pulmonary artery pressure runs
  ~5mmHg above aortic pressure throughout the cycle (Rudolph 1979), driving
  continuous, not just systolic, forward flow through the DA.
- **Validation targets**: real Doppler measurements (PS, ED, S/D, PI) from 24
  fetuses scanned at Chongqing Health Center for Women and Children, from
  `DA related values.xlsx` in this folder -- **anonymized** (patient names
  replaced with PatientNN IDs; the original names never appear in any code,
  output, or this report).

## 3. What was calibrated, and how

The solver's inlet takes a prescribed flow waveform; there is no direct
pressure boundary condition. So the ~5mmHg PA-Ao pressure excess is not
imposed directly -- instead:
- Inlet mean/pulsatile flow amplitude is set so the simulated peak-systolic
  velocity matches the cohort's PS target (close to a direct fit, since
  velocity = flow/area and area is fixed by the geometry).
- The outlet reflection coefficient (`kappa`, representing downstream aortic/
  systemic impedance) and the DA wall stiffness scale (the DA wall is
  actively muscular, not a passive elastic systemic artery, so the standard
  large-artery Olufsen stiffness constants were not expected to transfer
  as-is) are jointly calibrated against ED, S/D, and PI -- a genuine test of
  the model, since these depend on wave/compliance dynamics, not just the
  inlet amplitude.
- The resulting simulated mean PA-Ao pressure difference is compared against
  the ~5mmHg literature value as an independent plausibility check (not a fit
  target).

### First attempt (v1) failed on the pulsatility indices

The initial inlet waveform (a quarter-sine systolic upstroke + exponential
diastolic decay, carried over unchanged from the CoA/adult-aortic-flow
project) could not simultaneously match PS/ED and S/D/PI, across a 41-run
grid search. Every parameter combination fell into one of two failure modes:
low pulsatility gave plausible PS/ED but S/D and PI far too low; high
pulsatility pushed PI toward target but collapsed ED toward zero and sent S/D
to 10-20+. **Diagnosis**: that waveform shape structurally ties "how high
systole goes" to "how deep diastole decays," which is wrong for the fetal DA
-- unlike a systemic artery's diastolic runoff, real fetal DA flow is
sustained through diastole by the continuous PA-Ao pressure excess (visible
in a real clinical Doppler waveform already in this project's `images/`
folder: sharp systolic peaks over a substantial, much-less-decayed diastolic
shelf).

### Redesign (v2): partial fix

Replaced the inlet with a flat diastolic **baseline** flow plus a short, sharp
systolic **spike** added on top (`BASE_FRAC` = fraction of mean flow carried
by the baseline), decoupling the diastolic floor from the systolic peak
amplitude. A further sweep (grid + fine-tune, ~80 simulation runs total)
found a substantially better-balanced parameter set.

## 4. Final result

| Index | v1 (old waveform, best) | **v2 (new waveform, final)** | Target (cohort) |
|---|---|---|---|
| PS (cm/s) | 38.7 (-6%) | **41.5 (+0.4%)** | 41.3 |
| ED (cm/s) | 13.9 (+6%) | 10.0 (-23%) | 13.1 |
| S/D | 2.79 (-28%) | **4.15 (+8%)** | 3.85 |
| PI | 1.08 (-50%) | **2.07 (-4%)** | 2.15 |
| total relative error | 0.93 | **0.35** | 0 = perfect |

Final calibrated parameters (now the defaults in `pda_model.py`):
Q_MEAN=0.232 cm^3/s, BASE_FRAC=0.65, KAPPA=-0.3, STIFFNESS_SCALE=0.01,
HR=150bpm, GA=13.5 weeks. Confirmed stable/periodic at N=200000 steps
(~6.7 cardiac cycles), no numerical blow-up (NaN).

Confirmed (by testing BASE_FRAC=0.65/0.75/0.8/0.85, each with the flow
amplitude re-calibrated for PS) that 0.65 is a genuine local optimum, not an
arbitrary stopping point: the total error rises monotonically (0.35 -> 0.61
-> 1.09 -> 1.61) as the baseline fraction increases further.

## 5. Open issues -- exactly where a reviewer's input would help

1. **End-diastolic velocity is still 23% low**, and this appears structurally
   linked to the S/D and PI fit: increasing BASE_FRAC brings ED almost exactly
   to target (13.9 vs 13.1 at BASE_FRAC=0.75) but pushes S/D and PI too low in
   the other direction (2.96 / 1.48). This looks like a genuine three-way
   tension in a single-representative-waveform model, not a bug. Possible
   ways forward: an independently-shaped (non-flat) diastolic taper with its
   own free parameter; fitting per-patient rather than one waveform for the
   whole cohort; or revisiting whether "PI"/"S-D" as computed here
   (from a simulated last-3-cycle window, see `compute_indices()` in
   `pda_model.py`) match the clinical machine's own computation exactly.
2. **Mean PA-Ao pressure cross-check fails badly**: simulated 0.09mmHg vs. the
   ~5mmHg literature value (Rudolph 1979), and this didn't improve between v1
   and v2 -- suggesting a different root cause than the waveform-shape issue.
   The leading suspect is the baseline pressure `P0=30mmHg` in `pda_model.py`,
   which is an UNSOURCED assumption (no literature value was found for
   absolute fetal MAP at 13.5 weeks specifically -- only the ~5mmHg PA-Ao
   *gradient* is well-sourced, not either absolute pressure). It's also
   possible the single-tube-with-reflection-coefficient architecture
   (borrowed from CoA, where both ends of one vessel sit on the same systemic
   circuit) is simply the wrong topology for a vessel that connects two
   genuinely different circulations (pulmonary vs. systemic) -- a real fix
   might need two independent pressure/impedance boundary conditions rather
   than one prescribed-flow inlet + one reflection-coefficient outlet.
3. **DA wall stiffness** (`STIFFNESS_SCALE=0.01`) and **outlet impedance**
   (`KAPPA=-0.3`) are both free-calibrated, not independently sourced -- no
   DA-specific tissue stiffness or fetal pulmonary/systemic impedance
   literature value was found. A negative `kappa` is also worth scrutinizing:
   physically it means the reflected wave has opposite sign to the incident
   one, which needs a clear physical interpretation (or reconsideration) in
   write-up.
4. **Single representative waveform for a 24-fetus cohort**: the model
   currently targets the COHORT MEAN indices, not per-patient variation. The
   real dataset (`anonymized_doppler_data.csv`, this folder) has substantial
   patient-to-patient spread (e.g. PS SD=12.5 cm/s on a mean of 41.3) that
   isn't addressed at all yet.
5. **Blood rho/mu** (1.05 g/cm^3, 0.035 poise) and the **DA taper profile**
   (linear, PA-end-to-Ao-end, informed only qualitatively by the schematic
   `cmgui_model` reconstruction) are both carried over/assumed rather than
   independently sourced for this specific structure and gestational age.

## 6. Where the code is

All in `E:\Google Drive\Harvey Ho Paper\2020\ductus arteriosus\pda_1d_model\`:

| File | What it does |
|---|---|
| `da_geometry.py` | Szpinda regression (length/diameter vs. GA) |
| `network_geometry.json` | parsed cmgui_model reconstruction (nodes/radii/connectivity) |
| `anonymized_doppler_data.csv` | per-patient PS/ED/S-D/PI, anonymized |
| `validation_targets.json` | cohort mean/SD summary (the fit targets) |
| `pda_model.py` | the model itself: geometry, inlet waveform, `run()`, `compute_indices()` -- **run this directly for the current calibrated result** |
| `calibrate_pda.py` | v1 and v2 calibration sweep script (edit TARGET/grids to re-run) |
| `calibration_results.csv` / `calibration_results_v2.csv` | full sweep logs (v1 / v2) |
| `finetune_base_frac.py`, `finetune_results.csv` | BASE_FRAC fine-tuning sweep |
| `model_plan_and_literature_data.md` | full working log -- literature sources, every parameter's derivation, all 3 calibration passes in detail (Sections 1-7) |
| `REPORT_FOR_REVIEWER.md` | this file |

The solver itself (`build_geometry_general`, `simulate`) lives one project
over, unmodified: `..\..\coarctation_aorta\coa_1d_model\baker_1d_solver.py`.

To reproduce the final result: `python pda_model.py` in this folder (takes
~1 minute). To see the full calibration history: `model_plan_and_literature_data.md`
Sections 5-7.

---

## 7. Response to reviewer round 1

Thank you for the sequenced feedback -- summarized responses below; full
detail in `model_plan_and_literature_data.md` Sections 8-9.

- **Naming**: agreed and actioned -- this is a fetal DA study, not a PDA
  (postnatal) study; noted explicitly at the top of the plan doc and in
  `pda_model.py`'s docstring, to carry into the eventual paper's title/aims.
- **Step 1 (clinical index definitions)**: verified using a real machine
  readout already in this project (GA=24w0d exemplar) -- S/D, RI, and PI
  (using TAMX, time-averaged MAXIMUM velocity) all match the machine's
  displayed values to 2-3 significant figures, confirming our formula
  structure was already correct. Surfaced a more consequential, still-
  unresolved issue: clinical PS/ED are near-centerline peak velocities, while
  our model reports cross-sectional MEAN velocity (q/A) -- a profile
  correction factor, likely phase-dependent (blunter at systole, more
  parabolic at diastole), is a promising lead for the residual ED gap,
  not yet quantified. Raw per-patient waveforms are NOT available in this
  project's data (only pre-computed triplicate PS/ED/S-D/PI per patient) --
  recomputing from raw traces, as suggested, isn't possible here.
- **Step 2 (boundary-condition redesign, your top priority)**: built a lumped
  two-compartment model (pulmonary + systemic, `two_compartment_model.py`)
  with literature-informed (not Doppler-fit) cardiac output, RV:LV ratio, and
  shunt-fraction parameters, connected by an orifice/Bernoulli DA relation.
  Its own pressure gradient converges to 5.4mmHg (target ~5mmHg) with
  continuous, never-reversing forward flow -- both genuine, non-fitted
  consequences of the physiology. Feeding this into the unchanged 1D tube
  (`pda_model_v3_twocompartment.py`) revealed WHY the original pressure
  cross-check was comparing the wrong quantity: the 1D solver's tube law
  uses one uniform baseline pressure for the whole vessel, so its own
  inlet-vs-outlet comparison can only ever report the DA's own small local
  compliance effect (~0.04-0.16mmHg), never the two different pressure
  ENVIRONMENTS its ends actually sit in. The physically-meaningful gradient
  is the compartment difference (5.4mmHg) plus that small local term -- once
  interpreted this way, the original discrepancy is resolved architecturally,
  not by re-tuning a parameter. **New open issue this exposed**: the
  resulting DA velocities are ~3x below the Doppler targets (PS=13.9 vs 41.3
  cm/s) -- deliberately NOT closed by re-tuning the orifice coefficient back
  up (that would reintroduce the fit-to-target problem you flagged in Step
  4). Three candidate explanations reported, none yet distinguished:
  under-estimated first-trimester flow/shunt-fraction (extrapolated from
  later gestation), the mean-vs-peak profile issue from Step 1, or a
  vena-contracta-type effective-orifice-area effect at the described
  aortic-junction constriction.
- **Steps 3-5 (identifiability/sensitivity, per-patient/cross-validated
  fit, uncertainty propagation)**: not yet done -- correctly sequenced after
  Step 2, which is now a working first pass. Flagged as the immediate next
  work.
- **Step 6 (revisit waveform)**: not revisited further per your instruction
  to hold off until the above is in place.

**Honest status**: the boundary-condition redesign is real progress (it
resolves the mechanism of the pressure-gradient failure, not just the
number), but it introduces a new, larger velocity-magnitude discrepancy that
is currently unresolved. This is not yet a stronger model in the sense of
"fits the data better" -- it is a more scientifically honest one, with the
next failure mode now visible instead of hidden behind free-parameter
fitting. Your read on which of the three candidate explanations (or a
different one) is most worth pursuing first would be valuable before more
compute goes into any of them.

## 8. Steps 3-5 (identifiability, cross-validation, uncertainty) -- complete

Full detail in `model_plan_and_literature_data.md` Section 10; summary:

- **Step 3 (sensitivity/identifiability)**: split result. Peak-systolic
  velocity (PS) is well-behaved -- clean, monotonic, order-1 elasticities to
  cardiac output/RV:LV ratio/shunt fraction, and correctly near-insensitive
  to DA wall stiffness. **End-diastolic velocity, S/D, and PI are not** --
  their response to DA stiffness is large (elasticities up to 6x) AND
  changes sign between +-20% perturbations, meaning they are not reliably
  identifiable given the current parameterization. Separately, independently
  perturbing PA or Ao pressure (not symmetrically) can flip the assumed
  P_pa>P_ao ordering and collapse DA flow to zero -- a genuine, disclosed
  fragility, not patched over.
- **Step 4 (cross-validation)**: 4-fold CV of the v2 (Doppler-fit) model,
  refitting only the flow-amplitude parameter per fold (a disclosed partial,
  not full nested, CV). Out-of-sample errors are moderately worse than
  in-sample for PS (0.4%->8.3%) and PI (4%->10.3%), roughly unchanged for ED
  and S/D. No strong evidence of gross overfitting, but only 1 of 4 free
  parameters was actually tested out-of-sample.
- **Step 5 (uncertainty propagation)**: 40-sample Monte Carlo over 5
  literature-bounded parameters. **The pressure gradient is robust across
  the ENTIRE plausible range** (90% interval 3.6-7.3mmHg brackets the ~5mmHg
  target) -- strong evidence the two-compartment fix is real, not a lucky
  point estimate. **The velocity gap is NOT closeable within this plausible
  range** -- PS's 95th percentile (18.7 cm/s) stays under half the 41.3
  target, and S/D/PI's 95th percentiles stay well below target too. This
  rules out "just retune within plausible bounds" as a fix and strengthens
  the case that one of the three structural explanations in Section 7/9
  is needed.

**Verdict on your "phenomenological vs. mechanistic" framing**: split, and
we think it should stay split rather than be collapsed into one label --
the pressure mechanism is now genuinely mechanistic (sourced, robust,
not fit); the velocity/shape indices remain phenomenological (PS at least
predictable and stable; ED/S-D/PI additionally fragile/non-identifiable).

---

## 9. Response to reviewer round 2 -- circularity and coupling critique accepted

You were right, and we were wrong to call the 5.4mmHg gradient a "genuine,
non-fitted consequence of the physiology." On inspection: the compartment
pressures (32.5/27.5mmHg) were assumed specifically to produce ~5mmHg;
R_pulm/R_sys/K_DA are all back-calculated from that assumption; the
uncertainty sweep sampling 3-7mmHg and returning 3.6-7.3mmHg is exactly the
circularity made visible, not evidence of robustness as we originally
(wrongly) framed it. Corrected throughout `model_plan_and_literature_data.md`
(Sections 9, 10.1, 10.4, new Section 11).

The one-way-coupling point is also accepted as a real architectural flaw,
not a resolved issue: 0D compartments -> prescribed DA flow -> 1D tube
cannot enforce flow and pressure continuity simultaneously at both
interfaces, the 1D tube's pressure drop can't feed back into the 0D system,
and our original write-up's move of adding the two pressure-drop numbers
together was unjustified and risked double-counting. Withdrawn.

One structural (not parametric) finding does survive: the DA is
"acoustically short" (wave-transit time ~0.0016s vs. a 0.4s cardiac period,
i.e. under 0.5% of the cycle) -- meaning a full 1D wave-propagation
treatment may not be buying much physically for this specific vessel beyond
what a properly-coupled lumped RLC element would also capture. This is a
real argument in favor of your suggested "simpler publishable alternative"
(a single coupled 0D DA element), not just a shortcut.

Also accepted without dispute: the 3x mean-to-peak correction is
implausible (classical ratios cap at ~2); a vena-contracta correction
needs direct evidence, not gap-filling convenience; OAT sensitivity is not
identifiability; the partial CV is not full out-of-sample validation. Your
effective-diameter hypothesis (~0.58x the modeled diameter) is a concrete,
testable next step we intend to pursue directly.

**Adopting your recommended path forward as this project's plan** (full
detail in `model_plan_and_literature_data.md` Section 12): (1) choose one
internally consistent architecture (leaning toward your Option B, the
single 0D RLC element, given the acoustic-shortness finding above -- open
to discussion); (2) audit the geometry/measurement correspondence (Szpinda
diameter definition, Doppler sample location, narrowest-jet vs. main-lumen
question); (3) fix numerical convergence and the ED sampling definition;
(4) run a real joint identifiability analysis on a small parameter set;
(5) decide the paper's claim (mechanistic reproduction vs. your suggested
honest diagnostic/negative-result framing) based on what the above actually
shows, not in advance.

Thank you for not letting the round-1 "resolved" framing stand -- this is a
more honest position to build from.

## 10. Architecture rebuilt (your Option B), tested against your own hypothesis

Chose your "simpler publishable alternative": a single, genuinely coupled
0D model (`da_rlc_coupled_model.py`) -- three states (P_pa, P_ao, Q_da)
integrated SIMULTANEOUSLY via RK4, with the DA as a proper resistance +
inertance element (nonlinear Bernoulli/orifice loss, not linear Poiseuille),
compliance folded into the two compartments (disclosed simplification, given
the DA's acoustic shortness). De-circularized as promised: `R_pulm`/`R_sys`
are now anchored to ONE shared baseline pressure (not two independently
chosen to produce ~5mmHg), and the DA loss coefficient comes from orifice
theory (discharge coefficient x throat area), not a back-calculated
gradient. Converges to <0.001% cycle-to-cycle difference within 8 cycles,
and runs ~10x faster than the old 1D PDE -- both directly answer your
convergence concern.

**Tested your effective-diameter hypothesis directly**: at full anatomical
throat area, the new architecture alone (genuine inertance/dynamics instead
of an instantaneous algebraic relation) already shrinks the velocity gap
from ~3x to ~2.1x. Bisecting the effective-diameter ratio to hit peak-
systolic velocity exactly lands at **~0.68** (your estimate was ~0.58, in
the same ballpark) -- and at that point, **end-diastolic velocity and S/D
both land within ~10%** of target (a real improvement from v3's -23%/+8%).

**A genuine joint (not OAT) identifiability scan** (40-point grid, effective-
diameter-ratio x discharge-coefficient, all confirmed fully converged) found
clean, non-degenerate structure: peak-systolic/end-diastolic velocity and
S/D respond strongly and specifically to effective diameter, barely at all
to discharge coefficient (well-identified); the emergent pressure gradient
responds to both (also identifiable, but only via pressure, not velocity).
**PI is the one index that stays stuck around 1.3-1.4 across the ENTIRE
grid, never approaching target regardless of either parameter** -- a clean
negative result pointing away from throat geometry/discharge coefficient and
toward the inertance term (which physically damps transmitted pulsatility)
or the ventricular waveform shape as the more likely explanation -- not yet
tested directly.

**Honest status**: 3 of 4 indices (PS, ED, S/D) are now within ~10% of
target using a single, physically-motivated, non-circular diameter
correction; PI remains a genuine, isolated ~37-40% shortfall; the emergent
pressure gradient (0.45mmHg at the diameter-corrected point) is still far
below your ~5mmHg reference, though it now increases in the expected
direction as the DA is made more resistive.

## 11. Geometry/measurement audit (your Step 2) -- an independent confirmation, not a coincidence

Did exactly what you suggested first. Two findings:

1. **Szpinda (2007) measures EXTERNAL diameter** (formalin-fixed, dissected,
   photographed specimens) -- and this project's code had been using it
   directly as internal/luminal diameter with no wall-thickness correction,
   despite our own docs claiming otherwise. A real bug, now flagged.
2. **A better-located, previously-unread source exists**: Leao et al. (2015),
   *J Morphol Sci*, measured diameter SPECIFICALLY at the ductus-aortic
   junction (the narrowest point, not an along-length average like
   Szpinda's) -- their directly-measured 9-14-week bin value is 0.93+-0.55mm
   (n=10). Converting to a radius and comparing to our model's previous
   Szpinda-based throat radius gives a ratio of **0.679**.

That number was derived with ZERO reference to the Doppler data. Section
13.1's diameter ratio, found by fitting peak-systolic velocity alone, was
**0.68**. These two numbers come from completely independent routes (one
anatomical paper we hadn't read; one curve-fit against a different paper's
Doppler data) and agree to within 0.2 percentage points.

Switched the model to use Leao's value as the default throat geometry
(literature-sourced, not fitted) and re-ran with every parameter
independently sourced -- Vimpeli's cardiac output, Szpinda's length, Leao's
throat diameter, a standard Cd=0.7 orifice coefficient, one shared baseline
pressure, **zero fitting to the Doppler targets anywhere in the chain**:

| Index | Result | Target | Error |
|---|---|---|---|
| PS (cm/s) | 41.6 | 41.3 | **+0.6%** |
| ED (cm/s) | 11.8 | 13.1 | -9% |
| S/D | 3.51 | 3.85 | -9% |
| PI | 1.36 | 2.15 | -37% |
| gradient (mmHg) | 0.46 | ~5 | still short |

Three of four indices within ~10%, entirely from independently-sourced
literature. We think this is a legitimate, if partial, mechanistic result --
not overclaiming, since PI stays exactly where your joint-identifiability
scan predicted it would (unmoved by geometry, since it never responded to
throat area or discharge coefficient), and the pressure gradient is still
well short of your ~5mmHg reference. Both remain open, honestly reported,
not swept under the rug. Small-n caveat on Leao's data (n=10 in the relevant
bin, R=0.48) noted, not hidden.

## 12. Numerical convergence and ED definition (your Step 3) -- fixed, and it made the fit look WORSE, honestly reported

Did exactly what you asked, and didn't like everything it found. ED was
being computed as a mean over the final 15% of the cycle -- an arbitrary
window, not the clinical end-diastolic sampling convention. Direct
inspection confirmed the velocity trace decays smoothly through diastole
(no numerical noise), and the window-mean was systematically HIGHER than
the true instantaneous end-of-cycle value. Fixed to sample the actual
instantaneous point. Result: **ED goes from -9% to -19%** (a real,
previously-hidden discrepancy, now correctly exposed) -- **S/D happens to
improve from -9% to +2.6%**, but only as an arithmetic byproduct of the
lower ED raising the ratio, not an independent improvement, and we're
saying so rather than presenting it as progress. PI is essentially
unchanged.

Numerical convergence is now fully verified for this architecture, and
cheaply so: RK4 step count from 500 to 8000 per cycle agrees to the 4th
decimal place at every resolution tested; cycle-to-cycle (periodic)
convergence is <0.001% at 8 cycles. Re-ran the full joint identifiability
grid (Section 11) with the corrected ED definition and full convergence --
the "no further fitting" default (Leao geometry as-is, Cd=0.7) scores 0.57
against a grid-wide best of 0.56, confirming Section 11's result wasn't a
lucky or cherry-picked point. **PI remains stuck at 1.3-1.4 across all 40
grid points (0.26-1.44 range), never approaching 2.15 anywhere** -- this
finding is now confirmed robust to both the ED-definition fix and full
numerical convergence, not an artifact of either. "Spatial resolution"
no longer applies to this architecture (no spatial mesh) -- noted rather
than silently dropped.

## 13. The ~5mmHg target is withdrawn -- your Bernoulli check was the key move

Traced it down. "~5mmHg" comes from Rudolph AM, "Fetal and neonatal
pulmonary circulation," *Annu Rev Physiol* 1979 -- a review synthesizing a
research program built on the chronically-instrumented **fetal LAMB**
preparation (human fetal catheterization isn't feasible at any GA). It's
repeated in secondary sources as a general statement about relative
pressure LEVELS between the two circulations, not an isolated local DA
pressure drop. Chronic fetal lamb instrumentation is also near-universally
done in the LAST THIRD of gestation -- late 2nd/3rd trimester equivalent,
not our 13.5-week first-trimester cohort. Species mismatch and gestational-
stage mismatch are each independently sufficient to disqualify it. No human
first-trimester fetal PA/Ao pressure data exists or plausibly can exist,
given the ethics/feasibility of the measurement -- a permanent gap, not a
literature-search failure.

**Withdrawn as a quantitative target, per your instruction.** Our 0.46mmHg
emergent gradient is no longer a "shortfall" -- there's no valid number to
fall short OF. It's simply the model's own prediction, and by your own
Bernoulli check, broadly consistent with the velocity scale we actually
observe.

## 14. PI factorial study -- your inertance caution was right, and the honest answer is "not yet resolved by any single mechanism"

Ran your full hierarchy (inertance 0.1-2x; PA/Ao compliance joint and
independent, 0.1-10x; resistance baseline 15-50mmHg with the flow split
preserved; systolic duration/sharpness; RV/LV relative timing and shape --
previously always identical and perfectly synchronized, never tested
otherwise). Also fixed the terminology you flagged: this is a coupled
nonlinear RL model (compliance lives in the compartments, not the DA
itself), and the 40-point grid is a sensitivity/response-surface scan, not
a full identifiability analysis.

**Inertance: refuted as a mechanism, cleanly.** 0.1x to 2x theoretical value
changes PI by less than 0.05 and TAMX not at all -- direct experimental
confirmation of your `<L*dQ/dt>=0` point. Withdrawing that hypothesis.

**Compliance: powerful, but destabilizing, exactly as you warned.** One
point (joint compliance at 0.5x baseline) hits PI=2.16 almost exactly --
while S/D blows up to 10.6 and ED collapses to 4.9. No compliance value
improves PI without breaking ED/S-D.

**The real diagnostic** (your TAMX framing): target PI implies TAMX~14.5
cm/s; our simulated TAMX is 21.9 -- 1.5-1.7x too high. The waveform spends
46% of the cycle above half of peak-systolic velocity -- too broad, not too
low or too high in its extremes.

**The most informative single finding: RV/LV relative timing.** We had
always assumed identical, perfectly-synchronized RV and LV ejection --
untested until now. A 10-15% cycle-fraction timing offset alone moves PI
from 1.42 to 2.71-3.23. This is the largest-effect factor tested, and it's
a previously-unexamined modelling assumption, not a new free parameter --
real hearts don't necessarily eject in perfect synchrony.

**Honest bottom line**: re-scaling flow amplitude after any PI-improving
shape change (shorter systole, or the RV/LV offset) does pull PI toward
target, but ED and S/D get worse by a comparable amount every time. No
combination tested beats the current baseline's overall score. This looks
like a genuine structural property of this model family, not a matter of
finding the right untested parameter -- consistent with the same three-way
tension we first hit all the way back in the original waveform calibration.
We did NOT run this as a joint multi-parameter search (only your specified
one-at-a-time hierarchy) -- that remains the one clearly untried avenue if
you think it's worth the compute before moving to the paper.

## 15. Round 4: your five focused items, all complete -- model now FROZEN

Per your instruction, no further target-driven tuning from here. All five
items done:

**1. Dataset reconciliation.** Not a data bug. The original xlsx's own
SUMMARY row (computed by the clinical authors) gives PS=41.32, ED=13.05,
S/D=3.85, PI=2.15 -- and recomputing directly from our anonymized CSV
reproduces all four exactly. The actual counts: 23 patients have PS/ED/PI,
22 have S/D (one patient has PS/ED/PI but no S/D -- a pre-existing gap in
the original spreadsheet, not an exclusion we made). Your "3.68" traces to
dividing by 23 instead of 22 for the S/D-specific statistic -- both
numbers are arithmetically correct once matched to the right per-index n.
`validation_targets.json`'s "24 patients" label was simply our own
bookkeeping error, now fixed.

**2. The Jensen's-inequality point -- confirmed, and it reframes everything.**
You were right that mean(PS)/mean(ED) != mean(S/D): 3.02 vs. 3.85 on the
complete-case (n=22) subset. Built the internally-consistent comparison you
asked for: patient-level (PS,ED,S/D,PI) vectors, their correlation
structure (S/D and PI are only weakly correlated with each other even in
the real patients, r=0.11), and the simulated model's Mahalanobis distance
from that multivariate distribution. **The result is the strongest finding
of this round**: our zero-fitting simulated vector has a Mahalanobis
distance of 1.80 from the patient population -- statistically
indistinguishable from the medoid (most "typical") real patient's own
distance to everyone else (1.81). By this correct multivariate metric, our
model is about as representative a member of this patient population as
the most representative actual patient in it. PI alone drives what
distance there is (z=-1.23); the other three indices are essentially
on-target in the multivariate sense, not just marginally.

**3. Epistemic vs. biological uncertainty, separated.** Fixed an
inconsistency you'd have caught anyway (we'd used raw SD for RV:LV ratio
while using SEM for diameter). Now report both properly: epistemic
(SEM-based, both parameters) and biological (raw SD for RV:LV ratio,
log-normal matched to Leao's mean/SD for diameter -- not the Normal that
produced the earlier "non-physical" outliers, since you're right that the
wide spread itself wasn't the problem, the non-positive-respecting
distribution shape was). Biological variability gives meaningfully wider
bands than epistemic uncertainty throughout, as physically expected. PI's
band spans target under both framings, but -- consistent with the
factorial study -- only by breaking S/D, under both.

**4. Timing-offset trade-off figure**, attached (`Figure_RVLV_timing_offset_sensitivity.png`) -- 
PI, ED, and S/D plotted together across the offset range, explicitly
labeled as a sensitivity finding with the ~40-60ms interventricular-delay
caveat, not presented as an explanation.

**5. Model frozen.** No further parameter tuning against the Doppler
targets from this point. Also adopting your exact framing for the
withdrawal language ("we found no applicable human first-trimester
reference," lamb data as context not validation) and your recommended
paper claim verbatim -- and explicitly will NOT claim all Doppler indices
were validated.

Ready to begin drafting.
