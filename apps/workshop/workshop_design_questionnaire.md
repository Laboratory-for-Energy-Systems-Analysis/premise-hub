# IAM Scenarios Workshop — Design Questionnaire

This questionnaire is the design brief for a roughly 60-minute, interactive
workshop that helps participants choose scenarios for prospective LCA databases
with `premise`.

You do not need to answer every question in prose. Tick an option, replace the
suggested default, or write “default” where the recommendation is acceptable.
Questions marked **Core** are enough for a first storyboard and prototype.

## Context already established

- Duration: approximately 60 minutes.
- Primary purpose: improve scenario literacy before participants select an IAM
  pathway for a prospective LCA database.
- Intended approach: interactive and dashboard-led rather than a conventional
  lecture.
- Available data: 877,135 records covering 6 IAM variants, 29 scenarios, 25
  sectors, 486 variables, 94 model-specific region labels, and years 2005–2100.
- Available models: GCAM, IMAGE, MESSAGE, REMIND, REMIND-EU, and TIAM-UCL.
- The source project already contains a Dash/Plotly scenario explorer and an
  IMAGE handout comparing SSP1-L, SSP2-M, and SSP3-H.
- A separate read-only IAM archive contains original GCAM, TIAM-UCL, REMIND,
  IMAGE, MESSAGE, and WITCH files. These preserve IAMC variable hierarchies,
  units, and variables that were filtered out of the dashboard CSV.
- That archive also contains generated plain-language storylines and metrics for
  38 runs across five model families. These are useful working material but need
  scientific review before being treated as authoritative teaching narratives.
- The CMIP7 ScenarioMIP framework names seven pathways by their emission trends:
  High (H), High-to-Low (HL), Medium (M), Medium-to-Low (ML), Low (L), Very Low
  (VL), and Low-to-Negative (LN). Their quantitative IAM implementations can
  still draw on SSP assumptions, so socioeconomic narrative and emission
  trajectory should be taught as related but distinct dimensions.

## 1. Participants and setting

1. **Core — Who are the participants?**
   - Programme/discipline: Industrial Ecology, LCA
   - Degree or professional level: PhD, academics
   - Approximate number of participants: about 20

2. **Core — What can we assume they already know?** Tick all that apply.
   - [ ] Basic climate science
   - [x] Life-cycle assessment
   - [x] Prospective LCA
   - [x] `premise`
   - [ ] IAMs
   - [ ] SSPs/RCPs
   - [ ] Python/data visualisation
   - [ ] Nothing beyond general environmental literacy

3. What is the workshop language? Is specialist English terminology acceptable?
English. Yes.

4. **Core — What will participants have during the session?**
   - [x] Individual laptops
   - [ ] One device per small group
   - [ ] Phones only
   - [ ] No participant devices; facilitator controls the dashboard
   - Reliable internet: [x] yes [ ] no [ ] uncertain

5. What is the room format: lecture theatre, classroom with movable groups,
   computer lab, or online/hybrid? 
More lecture theater, but should be interactive with discussions throughout the presentation.

6. Are there accessibility requirements to design for (colour-vision safety,
   minimum font size, screen readers, low-bandwidth access, language support)?
Not specifically. It's good to prioritze readibility from a distance.

## 2. Learning outcome and assessment

7. **Core — Complete this sentence:** “At the end of the hour, participants
   should be able to …”
Understand how IAM scenarios are generated, how the SSP, RCP and REP (representative emission pathways)
frameworks work, the narratives/storylines behind the broad scenario families, and how
they influence pLCA results when used via Premise.

8. **Core — Rank these outcomes from 1 (most important) to 5.**
   - Explain what an IAM does and does not do: 1
   - Decode scenario names and narratives: 1
   - Compare quantitative pathways in the dashboard: 1
   - Connect IAM variables to changes made by `premise`: 2
   - Defend a scenario choice for a prospective LCA study: 3

9. **Core — What observable task should close the session?**
   - [x] Choose one scenario and justify it in three sentences **(recommended)**
   - [x] Choose a scenario ensemble and justify the range
   - [ ] Complete a short quiz
   - [ ] Present a group comparison of two scenarios
   - [ ] No assessed task

10. Should participants leave with a “correct” selection method, or primarily
    with an appreciation that scenario choice depends on the research question?
    Suggested default: a transparent selection method, not a universally correct
    scenario.
A transparent selection method, not a universally correct scenario.

11. Will this hour connect to a later practical in which participants actually
    create a `premise` database? If yes, what will that practical ask them to do?
Not really.

## 3. Scientific story and terminology

12. **Core — How should the hour balance its three layers?** Suggested default:
    - IAM concepts and limitations: 20%
    - Scenario architecture and narratives: 35%
    - Dashboard investigation and prospective-LCA choice: 45%

13. **Core — Which terminology bridge should we teach?**
    - [x] SSPs → SSP–RCP forcing combinations → CMIP7 emission-trend pathways
      **(recommended)**
    - [ ] Focus on SSP/RCP terminology used by current `premise` releases
    - [ ] Focus mainly on the CMIP7 H/HL/M/ML/L/VL/LN framework

14. Should “representative emission pathways/trajectories” be introduced as a
    conceptual label, or should we adhere strictly to the identifiers used in the
    CMIP7 ScenarioMIP data and paper?
We should introduce it as the new inherited framework after RCP.

15. **Core — Which distinction deserves the strongest emphasis?** Rank these.
    - Socioeconomic storyline versus climate-policy/forcing pathway: 1
    - Scenario versus prediction or forecast: 2
    - One scenario across different IAM implementations: 3
    - Global narrative versus regional/sector-specific outcomes: 4
    - Climate outcome versus technology mix used by prospective LCA: 5

16. Which narrative assumptions must be explicit? Tick the priorities.
    - [x] Population and economic development
    - [ ] Inequality, institutions, and international cooperation
    - [x] Energy and material demand
    - [x] Technology availability, costs, and learning
    - [x] Climate policy timing and ambition
    - [ ] Trade and regional fragmentation
    - [x] Land use and biomass
    - [x] Carbon capture and carbon dioxide removal
    - [ ] Behaviour and lifestyle change
    - [x] Equity and burden sharing

17. How much IAM mechanics should be explained?
    - [x] Black-box overview: assumptions → optimisation/simulation → pathways
    - [x] Conceptual system map with feedbacks and constraints **(recommended)**
    - [ ] Some equations/optimisation detail

18. Which limitations or critiques must be included? Suggested core set:
    conditional plausibility, model structure, perfect-foresight assumptions where
    applicable, technology optimism, equity, regional aggregation, missing climate
    damages/feedbacks, and the fact that scenarios are not assigned probabilities.
OK

19. Do you want the CMIP7 change to emission-driven Earth-system-model runs and
    carbon-cycle uncertainty covered, or is that outside the LCA-focused scope?
It's good to cover it, as the new framework shift from the old RCP framework. And how
20. those two relate to IPCC's AR6 and AR7.

## 4. Scenario comparison design

20. **Core — What should be the main comparison set?**
    - [ ] Three memorable archetypes: low, medium, high **(recommended for 60 min)**
    - [x] Four scenarios including an overshoot pathway
    - [ ] All seven CMIP7 pathway families
    - [ ] A custom set (list it):

21. **Core — Should the primary comparison control for IAM or expose IAM
    uncertainty?**
    - [x] Start with one IAM and vary scenarios; then show one cross-IAM
      counterexample **(recommended)**
    - [ ] Compare several IAMs throughout
    - [ ] Use only one IAM

22. If one IAM anchors the story, which one and why?
    - [x] IMAGE, reusing the existing SSP1-L / SSP2-M / SSP3-H handout
    - [ ] MESSAGE
    - [ ] REMIND
    - [ ] GCAM
    - [ ] Other:

23. The GCAM data currently contains SSP2–RCP3.7, SSP2–RCP4.5, and SSP2–RCP6.0,
    whereas the other models include different legacy or CMIP7-style families.
    Should GCAM be part of the teaching comparison, an optional exploration, or
    omitted until scenario labels are harmonised?
An optional exploration.

24. **Core — Which two or three sector stories should participants investigate?**
    - [x] Electricity mix **(recommended)**
    - [x] Passenger or freight transport
    - [x] Steel
    - [ ] Cement
    - [ ] Hydrogen/fuels
    - [ ] Biomass and land pressure
    - [x] Carbon dioxide removal
    - [ ] Final energy in buildings/industry

25. **Core — Which geography should anchor the exercise?**
    - [x] World first, then one participant-relevant region **(recommended)**
    - [ ] A named country/region:
    - [ ] Global only

26. Should the exercise compare absolute quantities, relative technology shares,
    change from a base year, cumulative quantities, or all four?
Absolute quantities if aligned, and also relative shares.

27. Which years matter for the LCA decision: 2030, 2040, 2050, 2070, 2100, or a
    participant-selected year? Suggested default: 2030/2050/2100, with 2050 as
    the main decision point.
2020/2040/2060

## 5. Connection to `premise` and prospective LCA

28. **Core — How technical should the `premise` connection be?**
    - [ ] Conceptual: which sectors change and why
    - [X] Show the transformation pipeline and mappings **(recommended)**
    - [ ] Live database generation or code demonstration

29. Which transformations should be visible in the one-hour session (electricity,
    fuels, steel, cement, transport, biomass, DAC, efficiency, emissions)?
Electricity (and steel if there's time).

30. Should participants choose a single “most plausible” scenario, a contrastive
    pair, or an ensemble that spans relevant uncertainty? Suggested default:
    discourage a single “most likely” future; choose scenarios based on the
    decision context and include a contrastive range where feasible.
a contrastive range

31. What prospective-LCA case study should ground the decision (for example an
    EV, heat pump, hydrogen route, e-fuel, building, steel product, or DAC)?
Maybe different DAC technologies.

32. What caveats about `premise` must be explicit—for example, IAM variables do
    not directly replace every inventory flow, model regions differ, and equal
    warming outcomes can imply different technology pathways?
Those you mention. Plus, those mentioned here: https://www.sciencedirect.com/science/article/pii/S1364032125005970

## 6. Interaction and facilitation

33. **Core — Preferred interaction model:**
    - [x] Facilitator-led dashboard with whole-room votes
    - [ ] Small groups each investigate a scenario **(recommended)**
    - [ ] Individual self-guided dashboard
    - [ ] Hybrid: facilitator hook, group investigation, plenary choice

34. Which interaction tools are acceptable?
    - [x] Dashboard controls only
    - [ ] Built-in anonymous polls
    - [ ] Mentimeter/Slido or equivalent
    - [ ] Printed scenario cards
    - [ ] Shared worksheet or collaborative board

35. Are participants permitted to use phones or external polling websites?
No

36. Would you like a “scenario detective” mechanic where groups infer the
    narrative from hidden labels, then reveal and discuss the actual scenario?
    Suggested default: yes; it makes assumptions observable before terminology.
OK

37. How much open discussion is realistic with this class? Should group answers
    be collected verbally, through the dashboard, or on a worksheet?
Group answers are collected verbally.

38. **Core — Does the 60 minutes include questions and transitions?** Suggested
    starting rhythm:
    - 0–5 min: hook and preconception poll
    - 5–13 min: IAM system map
    - 13–22 min: RCP → SSP → CMIP7 terminology bridge
    - 22–38 min: dashboard “scenario detective”
    - 38–50 min: trace pathways into `premise`
    - 50–58 min: scenario-choice challenge and debrief
    - 58–60 min: takeaways/exit poll
I think it is possible to stretch it to 90 minute if needed.

## 7. Dashboard and technical architecture

39. **Core — What should we build?**
    - [ ] Extend the existing Python Dash app **(fastest route)**
    - [x] Build a workshop-specific Dash app with guided stages **(recommended)**
    - [ ] Build a static HTML/JavaScript dashboard
    - [ ] Use a notebook with interactive widgets
    - [ ] Use PowerPoint plus facilitator-controlled charts

40. **Core — How will it run in the room?**
    - [x] Hosted publicly
    - [ ] Hosted behind access control
    - [ ] Run locally on the facilitator laptop
    - [ ] Run locally on every participant laptop
    - [ ] Must work fully offline
We cna deploy it on Heroku.

41. Do you already have a preferred host and deployment process (Heroku, Render,
    institutional server, Docker, or another platform)?
Heroku

42. Which guided dashboard features matter most?
    - [x] Curated “story” steps before free exploration
    - [x] Narrative cards linked to curves
    - [x] Side-by-side scenario comparison
    - [x] Cross-IAM comparison with a model-uncertainty warning
    - [ ] Difference-from-reference view
    - [x] Absolute/relative/cumulative toggles
    - [ ] Region and year controls
    - [x] “What `premise` changes” annotations
    - [ ] Export chart/data
    - [x] Polling and group answer capture

43. Should scenario names be hidden during the detective exercise and revealed on
    demand? Should instructors have a separate presentation mode?
Yes, and yes.

44. Should free exploration expose all 486 variables, or only a curated set with
    an optional advanced mode? Suggested default: curated teaching variables.
Curated list, possibly including some that are in the original IAM files.

45. The 94 region labels are model-specific and not directly comparable. Should
    the first release limit comparisons to `World`, add a region concordance, or
    clearly allow only within-model regional comparisons?
We cna use teh the R10 regions definition. Look it up online. But if so, we should clearly
show how we map the IAM-specific regions to R10.

46. The CSV has no `unit` column; units currently live in a separate YAML file.
    Who can confirm the units and aggregation rules for the newly added sectors
    and GCAM records before we present them?
Me.

47. Is the copied dataset final and approved for workshop use, or should we expect
    another `premise`/scenario-data release before delivery?
It's final.

48. May the dashboard repository and derived charts be public? Are the underlying
    IAM data redistributable, or must the raw CSV remain local/untracked?
Yes.

49. **Core — What should be the evidence hierarchy for scenario narratives?**
    Suggested default: published scenario protocol and model documentation for
    intended assumptions; original IAM files for quantified pathways and units;
    transformed workshop CSV only for dashboard-ready variables.
OK

50. The IAM archive contains generated storylines for 38 model runs. Are these
    approved source material, useful drafts to validate, or prior exploratory
    work that should not be reused directly?
I do not know what you refer to.

51. Several source versions do not align exactly. For example, the raw GCAM
    folder includes Base/RCP2.6/RCP4.5 material while the copied workshop CSV has
    a newer GCAM RCP3.7/RCP4.5/RCP6.0 subset. Which release should be authoritative,
    and may versions be combined when clearly labelled?
Consider the new GCAM RCP3.7/RCP4.5/RCP6.0 subset.

52. WITCH files exist in the IAM archive but WITCH is absent from the copied
    dashboard CSV. Should WITCH remain outside this workshop, appear only in a
    model-landscape overview, or be added to the scenario explorer later?
Ignore WITCH files for now.

## 8. Presentation and deliverables

53. **Core — What artifacts do you want?**
    - [ ] Editable PowerPoint deck
    - [x] Dashboard source and deployment instructions
    - [x] Instructor script with timings and prompts
    - [ ] Participant worksheet
    - [ ] Scenario cards
    - [ ] One-page scenario-selection checklist
    - [ ] Follow-up notebook/exercise
    - [ ] Answer key

54. Should the “presentation” be a conventional deck that launches the dashboard,
    or should the dashboard itself be the main presentation surface? Suggested
    default: a short deck for framing and synthesis, dashboard for the middle.
The dashboard itself should be the presentation medium. It should include slides,
interactive polls, questions, interactive graphics, etc.

55. Is there an institutional slide template, logo, colour palette, or font we
    must use? Please provide the source deck/assets if so.
No. Just use the new PSI logo and the mention of PSI LEA where relevant (but keep it discrete).

56. Are speaker notes expected to be detailed enough for another instructor to
    deliver the workshop?
Yes

57. Which references, prior slides, `premise` documentation pages, or case studies
    are mandatory? Which existing materials should not be reused?
None are mandatory. But for inspiration, you may look in this folder: "/Users/romain/Library/CloudStorage/Dropbox/presentations"

58. What is the delivery date, and when should the storyboard, dashboard
    prototype, rehearsal draft, and final package be ready?
As soon as possible. Workshop date: Sept 3rd.

59. Who gives scientific sign-off on scenario narratives, data units, and the
    description of what `premise` changes?
Me.

## Minimum reply needed to begin

For the first storyboard, answers to questions **1, 2, 4, 7–9, 12–13, 20–25,
28, 33, 38–40, 49, 53, and 58** are sufficient. Everything else can initially use
the suggested defaults and be revisited after the prototype.
