# IAM Scenarios for Prospective LCA — Workshop Blueprint

## Purpose and audience

The dashboard helps PhD researchers and academics who already know LCA,
prospective LCA and `premise` understand how IAM scenarios are constructed and
how scenario choice propagates into prospective inventories and LCIA results.
The presentation is facilitator-led in a lecture theatre, with verbal discussion
and show-of-hands responses throughout.

Participants should leave able to:

1. Connect human needs and energy services to infrastructure, energy use,
   greenhouse-gas emissions, cumulative CO₂ and warming.
2. Explain why cross-sector consistency creates a need for IAMs.
3. Explain why a net-zero target year is an endpoint rather than a transition plan.
4. Explain what an IAM integrates, computes and omits.
5. Describe how IAM scenarios became part of the climate-policy evidence chain.
6. Separate narrative, scenario, pathway, projection and forecast.
7. Decode RCP, SSP–RCP and CMIP7 emission-family terminology.
8. Read IAM output as a conditional result rather than a prediction.
9. Trace an IAM pathway through `premise` into an inventory and LCIA score.
10. Select and justify a contrastive scenario range for prospective LCA.

## Scientific grammar

Every quantitative result is described as:

> socioeconomic narrative + emissions/policy pathway + IAM implementation + year + region

The primary controlled comparison uses IMAGE `SSP1-L`, `SSP2-M`, `SSP3-H` and
`SSP2-VLHO`. These scenarios are a contrastive teaching set, not probabilities or
a complete uncertainty space.

The framework chapter distinguishes:

- RCP concentration and forcing pathways used in CMIP5;
- SSP socioeconomic narratives combined with forcing pathways in CMIP6;
- the CMIP7 H, HL, M, ML, L, VL and LN emission-trend families;
- concentration-driven and emission-driven Earth-system-model experiments;
- AR6 evidence from CMIP6 and the intended AR7 role of CMIP7.

## Chapter sequence

The live path contains 30 states and budgets 75 minutes of speaking. The
remaining 15 minutes of a 90-minute slot are reserved for interactions,
transitions and questions. Twenty-two supporting states remain available in a
separate backup chapter.

| Chapter | Core states | Minutes | Audience action |
|---|---:|---:|---|
| Why IAMs | 1–9 | 16 | Translate a political endpoint into the questions a quantified pathway must answer |
| Scenario frameworks | 10–15 | 15 | Decode socioeconomic narrative, forcing/emissions family, IAM implementation and pathway |
| Read the pathways | 16–22 | 18 | Choose an anonymous pathway, compare the system and interrogate sector results |
| From IAM to Premise | 23–24 | 8 | Identify where IAM evidence becomes an inventory parameter and a supportable statement |
| LCIA and interpretation | 25–27 | 11 | Separate unit impact, deployment and causes, then trace a result to evidence |
| Build and report | 28–30 | 7 | State the role of Premise, follow the build hand-off and retain the reporting resources |
| Backup | B1–B22 | 0 | Open supporting theory, accounting layers, sector examples, cases and workflow detail as needed |

Chapter names appear in the application header. The live **Next** sequence stops
at core state 30. Contextual buttons open the most relevant backup group and
store the originating core state; every backup state includes a return button.

## Interaction model

- Ask for a prediction or choice before explaining each major concept.
- Build the motivation as needs → services → infrastructure → energy and
  materials → emissions → accumulation → warming → integrated decisions →
  national commitments → pathways → investment → prospective inventories.
- Hide scenario names during the opening and detective exercises.
- Record show-of-hands counts locally in the facilitator's browser.
- Reveal six evidence rounds: population, GDP, CO2, warming, final energy and CDR.
- Let participants toggle 2020/2040/2060 and absolute/share/cumulative sector views.
- Use Plotly hover and legend isolation to interrogate individual technologies.
- Revisit the opening choice after the scenario-selection method.

## Evidence and comparability rules

Each narrative statement is classified as `source definition`, `model output`,
`derived metric`, or `interpretation`. Intended narratives come from published
scenario protocols; quantities come from original IAM files; dashboard plots use
the curated derivative of the consolidated source CSV.

- Never convert absent rows to zero without checking the original IAM source.
- Show model, scenario, year, region, unit and provenance with every chart.
- Compare absolute values across IAMs only after validating definitions and units.
- Keep native model regions visible and classify R10 mappings as exact,
  aggregated, approximate or unavailable.
- Do not call a scenario “business as usual” without defining the policy case.
- Do not select a `premise` database using temperature alone.
- Do not rank scenarios by probability.

## IAM-to-LCA chain

The presentation repeatedly uses this chain:

> assumptions → IAM pathway → derived `premise` parameter → transformed inventory → functional-unit LCIA → system-scale consequence

Electricity demonstrates regional generation shares and efficiencies. Steel
demonstrates production-route substitution. DAC demonstrates why deployment,
cumulative learning, inventory performance and impact scores are distinct.

Scenario databases use ecoinvent 3.12 cutoff with `premise` 2.4.6 for the four
IMAGE pathways in 2040 and 2060. Climate results use IPCC 2021 GWP100 with
hydrogen and biogenic CO2 factors; EF 3.1 covers minerals/metals, land and water:

- 1 kWh Swiss low-voltage electricity;
- 1 kg WEU low-alloyed steel;
- 1 kg CO2 captured and stored with WEU solvent- and sorbent-based DAC.

The dashboard never executes Brightway and never redistributes ecoinvent data.

## Closing selection method

Participants state:

1. The study question and decision year.
2. Which transformed background sectors matter.
3. An anchor scenario and the conditional question it represents.
4. A contrast that tests a different narrative, policy, model or technology dependency.
5. Model, pathway, year, region mapping, `premise` version, source database and rationale.

Scientific release requires owner review of narratives, unit conversions,
technology groupings, region mappings, transformation descriptions and LCIA
interpretations.
