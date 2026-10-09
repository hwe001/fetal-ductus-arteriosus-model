# Literature review: fetal ductus arteriosus (DA) modelling and Doppler

Compiled 2026-10-09 to support revision of the manuscript after rejection (editor: Introduction
too brief, no critical literature review, Discussion not linked to the literature, motivation unclear).

**Verification status.** Every reference in section 6 was matched against Europe PMC records
(authors, journal, year, volume/pages, DOI, PMID). Content claims come from the abstract or full
text that was read: *[abstract]* or *[full text]*. Items marked **[UNVERIFIED]** came only from
search-result summaries and must be checked before citing. This is not a systematic review.

---

## 1. What the model is

The frozen model (`da_rlc_coupled_model.py`) is a **0D lumped ODE system** with three states
(P_pa, P_ao, Q_da). The DA is a resistance (quadratic, orifice-type) plus inertance bridging the PA
and aortic compartments; compliance is folded into the compartments. The earlier 1D
transmission-line (MacCormack) solver was abandoned. Methodologically this is the same family as
Pennati 1997 and Garcia-Canadilla 2014-2025, so **novelty must come from the question asked and
the gestational window, not the method.**

## 2. State of the art

### 2.1 Fetal circulation models
- **Pennati, Bellotti & Fumero 1997**: first Doppler-based lumped model, 19 compliant compartments,
  late gestation; mean/max error vs Doppler indices 7.7%/20.1%. *[abstract]*
- **Pennati & Fumero 2000**: scaling approach across gestation. (Bibliographic record only.)
- **Myers & Capper 2002**: frequency-domain transmission-line model of the foetal arterial tree,
  Doppler PI/RI in aorta, iliac and umbilical arteries within ~8% of clinical values. *[abstract]*
- **van den Wijngaard et al. 2006**: distributed (Womersley, viscoelastic) fetoplacental model;
  PI vs placental/brain resistance. *[abstract]*
- **Garcia-Canadilla et al. 2014, 2015, 2017; Kulkarni 2018**: lumped models for IUGR redistribution,
  patient-specific placental/vascular properties, aortic isthmus Doppler, maternal diabetes. All
  late pregnancy; placenta/brain/isthmus questions. *[titles verified]*
- **Yigit et al. 2015**: fetal-to-neonatal transition, cord clamping. *[title verified]*
- **Villanueva-Baxarias et al. 2025 (PLoS Comput Biol)**: closed 0D model of coarctation; DA as
  R-L-C plus Bernoulli term, dilation up to 150%; calibrated to 7 controls at 32 weeks, 9 CoA cases.
  Own stated limits: no wave reflection, flow-to-velocity conversion error from uncertain
  diameters, small sample. *[full text]*
- **Reviews**: Zhang & Lindsey 2023: LPNs ignore spatial variation, 3D models use idealised
  geometry/rigid walls, validation data in their table start at 20 weeks, little first-trimester
  modelling *[full text]*. May et al. 2023 (WIREs Mech Dis) review fetus-to-neonate modelling
  *[abstract-level only; read before citing]*.

- **Huikeshoven & Jongsma 1985**: fetal cardiovascular model used to simulate *premature closure* of
  the DA; the simulated changes resemble those after indomethacin in animal experiments, suggesting
  the central cardiovascular effects of indomethacin can be attributed to ductal closure. *[abstract]*
  Earliest model of the constriction scenario found; must be cited and compared. (Model structure
  not read; it refers to a "previously validated" fetal model.)
- **Setchi, Mestel, Siggers, Parker, Tan, Wong 2013 (J Math Biol)**: analytical model (complex
  potential theory, conformal mapping, Fourier series) of flow through the *patent* DA in three
  idealised geometries, with healthy-adult boundary conditions. Predicts aortic/PA pressure
  equalisation, higher shear at the shunt edges, possible backflow. *[abstract]* Postnatal PDA,
  not fetal, not lumped, not validated against Doppler.
- **Spach et al. 1980 (Circulation)**: measured pulsatile aortopulmonary pressure-flow dynamics in
  patients with PDA. *[bibliographic record only; no abstract retrieved]* Postnatal measurement study.
- **Prior art for the DA-focused lumped approach (summary):** none found that is DA-focused,
  lumped, and validated against DA Doppler indices; closest are Pennati 1997 (DA is one of 19
  compartments), Villanueva-Baxarias 2025 (DA as R-L-C + Bernoulli in a coarctation model) and
  Huikeshoven 1985 (closure scenario).

**Gap claimable (to our knowledge):** all fetal circulation models found target >=20 weeks and treat
the DA as one element among many; none targets the DA waveform at ~13 weeks. Re-run and document
the search before submission (searches so far were title-level queries in Europe PMC).

### 2.2 DA Doppler measurement and reference data
- **Brezinka, Huisman, Stijnen, Wladimiroff 1992**: 298 women, 9-25 wk; first usable recordings at
  11 wk; **end-diastolic velocity absent until 13 wk, present in 50% at 15 wk, all from 17 wk**;
  velocities rise linearly with GA, PI stable. *[abstract]*
- **Brezinka et al. 1994**: reproducibility; ED velocity and acceleration time least reproducible
  (**[UNVERIFIED]**, from a search summary).
- **Mielke & Benda 2000**: reference ranges 13-41 wk, n=222; heart rate affects ED velocity, S/D,
  RI, PI. *[abstract]*
- **Mielke & Benda 2001**: DA carries ~46% of biventricular output (**[UNVERIFIED]**, search summary).
- **Seed et al. 2012**: phase-contrast CMR, 12 fetuses at 30-39 wk; DA = 41 +/- 8% of combined
  ventricular output. *[abstract]*

### 2.3 Why model when ultrasound can measure it? Clinical motivation
- Ductal constriction is clinically important: Huhta 1990; polyphenol-rich foods (Zielinsky 2010, 2012;
  Vian 2018); paracetamol signal (Allegaert 2019; Hauben 2021); herbal tea (Sridharan 2009);
  prevalence study (Zielinsky 2024, third trimester); RV dysfunction (Ma 2022, 60 cases vs 60
  controls *[abstract]*); Wen 2022 (22 cases, 34-41 wk *[abstract]*).
- **Limits of current practice (the argument for the model):** the diagnostic and mechanistic series
  found are all third trimester; diagnosis rests on velocity thresholds from single-centre series;
  they describe velocity, not driving pressure drop, resistance or inertance. First-trimester DA
  Doppler is technically hard (Brezinka), so a model that reproduces the expected waveform and
  shows which indices respond to which physical parameter gives a reference and a mechanistic link.
- Background: Kiserud 2005; Gournay 2011; Heymann & Rudolph 1975. Geometry source: Szpinda 2007.

## 3. Storyline for the rewritten Introduction (about 5 paragraphs)
1. DA carries ~40-46% of fetal combined output (Seed 2012; Mielke 2001); disorders cause RV
   dysfunction and tricuspid regurgitation (Ma 2022; Wen 2022).
2. Practice relies on third-trimester Doppler velocity thresholds; no mechanistic link to
   pressure/resistance; first-trimester waveform poorly characterised (Brezinka; Mielke 2000 starts
   at 13 wk).
3. Fetal circulation models exist (Pennati, Myers, van den Wijngaard, Garcia-Canadilla,
   Villanueva-Baxarias) but target >=20 wk and placenta/brain/isthmus questions; the DA is one
   element and rarely validated against its own waveform.
4. Gap: DA-focused, physics-based model at end of first trimester, non-circular parameterisation,
   uncertainty quantification.
5. Aim and contribution stated as what the model lets you ask (sensitivity of PS/ED/S/D/PI to
   inertance, resistance, timing offset; identifiability), not "we reproduced Doppler".

## 4. Discussion hooks
- Compare simulated PS/ED/PI with Mielke 2000 (13-14 wk) and Brezinka 1992. **Check first:**
  Brezinka found ED absent until 13 wk and in 50% at 15 wk, but the cohort mean ED is 13.1 cm/s at
  13.5 wk. Explain (equipment, transabdominal vs transvaginal, selection, protocol) or reconsider
  the ED target.
- DA share of output vs Seed 2012 / Mielke 2001: the model assumes ~85% DA shunt fraction vs 41-46%
  of combined output. Possibly different denominators; state this explicitly.
- Modelling choices vs Pennati (Bernoulli term, scaling), Villanueva-Baxarias (R-L-C, dilation to
  150%), and the "acoustically short" argument against needing 1D.
- Shared limitations: no autoregulation, n=24, single centre, flow-to-velocity conversion, angle error.
- Future: simulate constriction (reduce area) and compare with third-trimester thresholds once
  verified from primary sources.

## 5. Not found / not verified
- No first-trimester DA reference range beyond Brezinka 1992/1994; 11-14 wk literature found is
  almost entirely ductus venosus.
- No fetal DA-specific CFD/WSS study found (search summary only).
- Constriction cut-offs (PSV, PI) only from a search summary; take from primary sources.
- Most items read at abstract level only. Not looked up: Sa Couto 2000, Huikeshoven 1980,
  Menigault 1998, Muller/Clark models (named in the 2025 paper).

## 6. Verified reference list
1. Pennati G, Bellotti M, Fumero R. Mathematical modelling of the human foetal cardiovascular system based on Doppler ultrasound data. Med Eng Phys 1997;19:327-335. doi:10.1016/s1350-4533(97)84634-6. PMID 9302672.
2. Pennati G, Fumero R. Scaling approach to study the changes through the gestation of human fetal cardiac and circulatory behaviors. Ann Biomed Eng 2000;28:442-452. doi:10.1114/1.282. PMID 10870901.
3. Myers LJ, Capper WL. A transmission line model of the human foetal circulatory system. Med Eng Phys 2002;24:285-294. doi:10.1016/s1350-4533(02)00019-x. PMID 11996847.
4. Capper WL, Cowper JG, Myers LJ. A transfer function-based mathematical model of the fetal-placental circulation. Ultrasound Med Biol 2002;28:1421-1431. doi:10.1016/s0301-5629(02)00658-0. PMID 12498937.
5. van den Wijngaard JP, Westerhof BE, Faber DJ, Ramsay MM, Westerhof N, van Gemert MJ. Abnormal arterial flows by a distributed model of the fetal circulation. Am J Physiol Regul Integr Comp Physiol 2006;291:R1222-R1233. doi:10.1152/ajpregu.00212.2006. PMID 16778066.
6. Garcia-Canadilla P, Rudenick PA, Crispi F, et al. A computational model of the fetal circulation to quantify blood redistribution in intrauterine growth restriction. PLoS Comput Biol 2014;10:e1003667. doi:10.1371/journal.pcbi.1003667. PMID 24921933.
7. Garcia-Canadilla P, Crispi F, Cruz-Lemini M, et al. Patient-specific estimates of vascular and placental properties in growth-restricted fetuses based on a model of the fetal circulation. Placenta 2015;36:981-989. doi:10.1016/j.placenta.2015.07.130. PMID 26242709.
8. Garcia-Canadilla P, Crispi F, Cruz-Lemini M, et al. Understanding the aortic isthmus Doppler profile and its changes with gestational age using a lumped model of the fetal circulation. Fetal Diagn Ther 2017;41:41-50. doi:10.1159/000444142. PMID 26906235.
9. Kulkarni A, Garcia-Canadilla P, Khan A, et al. Remodeling of the cardiovascular circulation in fetuses of mothers with diabetes: a fetal computational model analysis. Placenta 2018;63:1-6. doi:10.1016/j.placenta.2017.12.020. PMID 29486850.
10. Yigit MB, Kowalski WJ, Hutchon DJ, Pekkan K. Transition from fetal to neonatal circulation: modeling the effect of umbilical cord clamping. J Biomech 2015;48:1662-1670. doi:10.1016/j.jbiomech.2015.02.040. PMID 25773588.
11. Villanueva-Baxarias I, Pellise-Tintore A, Perez-Rodriguez M, et al. Understanding the hemodynamic changes in fetuses with coarctation of the aorta using a lumped model of fetal circulation. PLoS Comput Biol 2025;21:e1013096. doi:10.1371/journal.pcbi.1013096. PMID 40446209.
12. Zhang D, Lindsey SE. Recasting current knowledge of human fetal circulation: the importance of computational models. J Cardiovasc Dev Dis 2023;10:240. doi:10.3390/jcdd10060240. PMID 37367405.
13. May RW, Maso Talou GD, Clark AR, et al. From fetus to neonate: a review of cardiovascular modeling in early life. WIREs Mech Dis 2023;15:e1608. doi:10.1002/wsbm.1608. PMID 37002617.
14. Brezinka C, Huisman TW, Stijnen T, Wladimiroff JW. Normal Doppler flow velocity waveforms in the fetal ductus arteriosus in the first half of pregnancy. Ultrasound Obstet Gynecol 1992;2:397-401. doi:10.1046/j.1469-0705.1992.02060397.x. PMID 12796913.
15. Brezinka C, Stijnen T, Wladimiroff JW. Doppler flow velocity waveforms in the fetal ductus arteriosus during the first half of pregnancy: a reproducibility study. Ultrasound Obstet Gynecol 1994;4:121-123. doi:10.1046/j.1469-0705.1994.04020121.x. PMID 12797205.
16. Mielke G, Benda N. Blood flow velocity waveforms of the fetal pulmonary artery and the ductus arteriosus: reference ranges from 13 weeks to term. Ultrasound Obstet Gynecol 2000;15:213-218. doi:10.1046/j.1469-0705.2000.00082.x. PMID 10846777.
17. Mielke G, Benda N. Cardiac output and central distribution of blood flow in the human fetus. Circulation 2001;103:1662-1668. doi:10.1161/01.cir.103.12.1662. PMID 11273994.
18. Seed M, van Amerom JF, Yoo SJ, et al. Feasibility of quantification of the distribution of blood flow in the normal human fetal circulation using CMR: a cross-sectional study. J Cardiovasc Magn Reson 2012;14:79. doi:10.1186/1532-429x-14-79. PMID 23181717.
19. Szpinda M, Szwesta A, Szpinda E. Morphometric study of the ductus arteriosus during human development. Ann Anat 2007;189:47-52. doi:10.1016/j.aanat.2006.06.008. PMID 17319608.
20. Kiserud T. Physiology of the fetal circulation. Semin Fetal Neonatal Med 2005;10:493-503. doi:10.1016/j.siny.2005.08.007. PMID 16236564.
21. Gournay V. The ductus arteriosus: physiology, regulation, and functional and congenital anomalies. Arch Cardiovasc Dis 2011;104:578-585. doi:10.1016/j.acvd.2010.06.006. PMID 22117910.
22. Heymann MA, Rudolph AM. Control of the ductus arteriosus. Physiol Rev 1975;55:62-78. doi:10.1152/physrev.1975.55.1.62. PMID 1088992.
23. Huhta JC, Cohen AW, Wood DC. Premature constriction of the ductus arteriosus. J Am Soc Echocardiogr 1990;3:30-34. doi:10.1016/s0894-7317(14)80296-4. PMID 2310589.
24. Zielinsky P, Piccoli AL, Manica JL, Nicoloso LH. New insights on fetal ductal constriction: role of maternal ingestion of polyphenol-rich foods. Expert Rev Cardiovasc Ther 2010;8:291-298. doi:10.1586/erc.09.174. PMID 20136615.
25. Zielinsky P, Piccoli AL, Manica JL, et al. Reversal of fetal ductal constriction after maternal restriction of polyphenol-rich foods: an open clinical trial. J Perinatol 2012;32:574-579. doi:10.1038/jp.2011.153. PMID 22052330.
26. Vian I, Zielinsky P, Zilio AM, et al. Increase of prostaglandin E2 in the reversal of fetal ductal constriction after polyphenol restriction. Ultrasound Obstet Gynecol 2018;52:617-622. doi:10.1002/uog.18974. PMID 29205592.
27. Zielinsky P, Sulis NM, Martins CM, Zucatti KP, Bonamigo ER, Vian I. Fetal ductal constriction in the third trimester of pregnancy: a prevalence study. J Perinatol 2024;44:444-445. doi:10.1038/s41372-023-01844-9. PMID 38042943.
28. Allegaert K, Mian P, Lapillonne A, van den Anker JN. Maternal paracetamol intake and fetal ductus arteriosus constriction or closure: a case series analysis. Br J Clin Pharmacol 2019;85:245-251. doi:10.1111/bcp.13778. PMID 30300944.
29. Hauben M, Bai S, Hung E, Lobello K, Tressler C, Zucal VP. Maternal paracetamol intake and fetal ductus arteriosus constriction/closure: comprehensive signal evaluation using the Austin Bradford Hill criteria. Eur J Clin Pharmacol 2021;77:1019-1028. doi:10.1007/s00228-020-03039-z. PMID 33410971.
30. Wen J, Guo X, Cai S, Xu D, Zhang G, Bai X. Fetal ductus arteriosus premature constriction. Int Heart J 2022;63:722-728. doi:10.1536/ihj.21-723. PMID 35831144.
31. Ma J, Cao H, Hong L, et al. Cardiac function assessment in fetuses with ductus arteriosus constriction: a two-dimensional echocardiography and FetalHQ study. Front Cardiovasc Med 2022. doi:10.3389/fcvm.2022.868675. PMID 35958395.
32. Sridharan S, Archer N, Manning N. Premature constriction of the fetal ductus arteriosus following the maternal consumption of camomile herbal tea. Ultrasound Obstet Gynecol 2009;34:358-359. doi:10.1002/uog.6453. PMID 19705407.
33. Huikeshoven FJ, Jongsma HW. Cardiovascular changes due to premature closure of the ductus arteriosus: a mathematical model. Eur J Obstet Gynecol Reprod Biol 1985;20:305-310. doi:10.1016/0028-2243(85)90141-8. PMID 3935497.
34. Setchi A, Mestel AJ, Siggers JH, Parker KH, Tan MW, Wong K. Mathematical model of flow through the patent ductus arteriosus. J Math Biol 2013;67:1487-1506. doi:10.1007/s00285-012-0596-8. PMID 23053537.
35. Spach MS, Serwer GA, Anderson PA, Canent RV, Levin AR. Pulsatile aortopulmonary pressure-flow dynamics of patent ductus arteriosus in patients with various hemodynamic states. Circulation 1980;61:110-122. doi:10.1161/01.cir.61.1.110. PMID 7349924.

### Postnatal PDA prediction literature (context for the late-pregnancy extension; titles only, not read)
36. Villamor-Martinez E, Kilani MA, Degraeuwe PL, Clyman RI, Villamor E. Intrauterine growth restriction and patent ductus arteriosus in very and extremely preterm infants: a systematic review and meta-analysis. Front Endocrinol 2019;10:58. doi:10.3389/fendo.2019.00058. PMID 30800098.
37. Park HW, Choi YS, Kim KS, Kim SN. Chorioamnionitis and patent ductus arteriosus: a systematic review and meta-analysis. PLoS One 2015;10:e0138114. doi:10.1371/journal.pone.0138114. PMID 26375582.
38. Behbodi E, Villamor-Martinez E, Degraeuwe PL, Villamor E. Chorioamnionitis appears not to be a risk factor for patent ductus arteriosus in preterm infants: a systematic review and meta-analysis. Sci Rep 2016;6:37967. doi:10.1038/srep37967. PMID 27892517.
39. Lee JA, Sohn JA, Oh S, Choi BM. Perinatal risk factors of symptomatic preterm patent ductus arteriosus and secondary ligation. Pediatr Neonatol 2020;61:439-446. doi:10.1016/j.pedneo.2020.03.016. PMID 32362475.

No study was found that uses fetal DA Doppler to predict postnatal PDA (title-level search only).
