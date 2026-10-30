"""A four-case visual narrative, built from the portal's existing lectures."""

from __future__ import annotations

from dash import dcc, html
from apps.setac_2026 import deck as short
from . import comparison as compare
from . import contributions as attribution
from .technical import erw_timing, root_attribution
from .editorial import clean_audience_footer
from .speaker import POINTS
from .scenario_backups import ssp_narratives, climate_trajectories
from .scenario_labels import warming_labels
from .branding import tool_link
from .visuals import (
    case_ribbon,
    carbon_atlas,
    coastal_scene,
    pulse_equivalence_map,
    discussion_cases,
    temporal_introduction,
)
from .processes import process_carousel
from .reused import iam_systems, scenario_layers, pathway_story, thank_you
from . import methods as teaching
from . import case_pulse as pulse_lesson
from .metric_discussion import discussion as gwp_discussion
from .bio import introduction as presenter_introduction
from .workflow import workflow_map
from .layout import (
    text,
    stack,
    cards,
    equation,
    _rewrite,
    _cover,
    _sources,
    _print_safe,
    _dated_equations,
    _climate_equations,
)

# One source for audience navigation, notes, timers and PDF order.
SLIDES = [
    {
        "title": "Why timing matters in life cycle assessment",
        "phase": "Opening",
        "seconds": 45,
        "cue": "Ask how changing production systems and the timing of emissions and removals "
        "affect the assessment of a long-lived project.",
        "notes": "Seoul National University, 30 October 2026. Seventy minutes of teaching includes three "
        "short discussions, followed by twenty minutes of open discussion. Explain timing "
        "through four continuing cases. Formal equations are available in backup rather than "
        "dominating the core lecture.",
        "key": "cover",
    },
    {
        "key": "about",
        "title": "Romain Sacchi",
        "phase": "About me",
        "seconds": 60,
        "cue": "Introduce your PSI role, research interests, open-source projects and selected publications.",
        "notes": "Scientist in the Technology Assessment Group, Laboratory for Energy Systems Analysis, "
        "Paul Scherrer Institut. The user confirmed Scientist and the selected projects/interests. "
        "Use the supplied portrait from Downloads. "
        "Locate PSI near Villigen on the Switzerland map. The career column shows the 2012 MSc "
        "in Environmental Sciences and 2018 industrial PhD in Industrial Ecology at Aalborg University, "
        "then joining PSI in June 2019, as documented in the PSI biography. EDGES uses its original logo. "
        "Introduce industrial ecology, future energy/mobility, climate timing and open science. "
        "The collaborative projects are premise, TRAILS, carculator "
        "and EDGES, each linked to its current public GitHub repository. Three selected publications "
        "link to their DOIs; ORCID provides the fuller record. Titles of the premise and passenger-car "
        "papers are shortened for the slide. Do not imply sole authorship or invent personal hobbies. "
        "Spend one minute here, then transition from these interests to the lecture's timing question.",
    },
    {
        "key": "why-time",
        "title": "Conventional LCA usually collapses time",
        "phase": "Opening · why retain time?",
        "seconds": 150,
        "cue": "Trace the electric car's production, charging and recycling into the aggregate inventory, then distinguish changing "
        "supply systems, climate timing and impacts long after disposal.",
        "notes": "Set the scene before introducing the four cases. Conventional static LCA can cover "
        "construction, use, replacement and end-of-life, but usually aggregates exchanges "
        "without retaining their event dates. This does not mean all emissions physically occur "
        "today, or that an LCA cannot include the entire life cycle. Also distinguish event "
        "dates from the reference year or vintage of a dataset. The electric-car lifecycle "
        "is illustrative, with no assumed vehicle lifetime, mandatory battery replacement or "
        "calculated EV impact values. Car and battery production precede driving, charging and "
        "maintenance recur during use, and dismantling/recycling follow use. Three "
        "different temporal questions motivate this lecture: (1) a long-lived activity can draw "
        "on suppliers that change over its lifetime, and (2) emission/removal dates influence "
        "climate response and the time available before an assessment endpoint, and (3) landfill "
        "leachate can release pollutants centuries after disposal, creating potential human-toxicity "
        "impacts beyond a short study horizon. A delayed release is distinct from environmental "
        "fate, exposure and effects after that release. Conventional LCA has no universal temporal "
        "cutoff: ecoinvent already distinguishes long-term releases (more than 100 years after the "
        "activity), and some static LCIA implementations characterize them. Explicitly excluding "
        "long-term flows or choosing a short horizon can omit their impacts; including them in "
        "an aggregate total still need not retain their dates. The landfill example is a general "
        "motivation, not a quantified electric-car waste scenario or a claim that FaIR models toxicity. "
        "None of these effects "
        "is automatically material in every study; explain why it matters for the question and "
        "system being assessed. GWP100 already has a 100-year characterization horizon, but "
        "standard fixed factors do not place events on a common calendar window. Prospective "
        "static LCA addresses conditional future production conditions; time-explicit "
        "inventories retain dates; dynamic climate assessment evaluates their response. The "
        "rest of the lecture develops these steps with DACCS, BECCS, coastal ERW and cement "
        "plus CCS. References on the slide: Beloin-Saint-Pierre, Heijungs & Blanc (2014), The "
        "ESPA (Enhanced Structural Path Analysis) method, International Journal of Life Cycle "
        "Assessment 19, 861–871, DOI 10.1007/s11367-014-0710-9; Müller et al. (2025), "
        "Time-explicit life cycle assessment: a flexible framework for coherent consideration "
        "of temporal dynamics, International Journal of Life Cycle Assessment 30, 3052–3071, "
        "DOI 10.1007/s11367-025-02539-3; Levasseur et al. (2010), Considering time in LCA: "
        "dynamic LCA and its application to global warming impact assessments, Environmental "
        "Science & Technology 44, 3169–3174, DOI 10.1021/es9030003; Turner, Beaven & Woodman "
        "(2017), Evaluating landfill aftercare strategies: A life cycle assessment approach, Waste "
        "Management 63, 417–431, DOI 10.1016/j.wasman.2016.12.005 (leachate assessment over "
        "10,000 years, including human toxicity); ecoinvent, About Life Cycle Impact Assessment "
        "(LCIA), LT/no-LT guidance, https://support.ecoinvent.org/lcia-results.",
    },
    {
        "title": "Changing supply systems and carbon timing: four cases",
        "phase": "Opening",
        "seconds": 150,
        "cue": "Carry forward the two questions from slide 2: which suppliers change, and when does carbon move? Then trace each carbon route.",
        "notes": "Connect explicitly to the previous slide: each case is supplied by a production system that can change with calendar year, and each has a distinct schedule of emissions, capture or uptake. Read the supplier/timing pair under each carbon route before comparing its reference and service. DACCS takes carbon from ambient air. BECCS couples biomass uptake to energy generation "
        "and storage; the forest reference matters. Coastal ERW changes ocean chemistry and "
        "subsequently draws down atmospheric CO₂. Cement capture mainly avoids release of "
        "mineral and fossil carbon; its non-fossil fuel fraction can also contribute removal. "
        "Geological storage alone does not establish atmospheric removal. Introduce the service "
        "and no-project reference directly on each carbon lane. Rock is a reactant for ERW, not "
        "the source of the atmospheric carbon being removed.",
        "key": "carbon-atlas",
    },
    {
        "title": "Follow carbon, materials and energy to storage",
        "phase": "Foundations",
        "seconds": 150,
        "cue": "Flip through the four process maps. Trace carbon first, then materials and energy, including outputs and losses.",
        "notes": 'Use the tabs to trace CO₂, materials/fuels, electricity and delivered heat through all four cases. The ecoinvent wordmark and cylinder icon identify the background database. Shaded input boxes are examples of links to its supply-chain unit processes, including purchased electricity, materials, fuels, chemicals, water and freight. The project design, CO₂ routing and capture/uptake assumptions remain analyst-defined foregrounds. Shading is a data-source key, not another physical flow or impact credit; no inputs, masses or scores have changed. Arrow widths are schematic; labels show physical quantities, never mass inferred from LCIA. DACCS uses low-temperature solid-sorbent temperature-vacuum swing adsorption (TVSA): 0.720 MWh direct capture electricity plus 1.134 MWh for a COP-3 heat pump delivering 12.24 GJ per net stored tonne. COP 3 is an adapted proxy, not a measured Northern European seasonal value. The separate 139 kWh conditioning/transport/injection total is counted once. BECCS distinguishes internal capture heat, exported electricity/heat, uncaptured stack CO₂ and transport losses; retain its standing-forest and equivalent-energy reference. ERW uses olivine-rich rock: 1.25 t deployed has 1 t eventual gross atmospheric uptake potential, not guaranteed net storage. Dissolution and air–sea exchange have distinct clocks. Diesel exhaust from machinery and haulage is shown without an invented CO₂ mass; its supplier impacts remain in the LCA. Cement is normalized to 1 t physically stored after sequential 5% liquefaction and 1.44% transport losses. Its full captured stream includes calcination, fuel and recaptured capture-boiler carbon. In 2025 this corresponds to 1.135 t clinker; compare CCS with BAU producing exactly that clinker output. All cement static scores and signed contributions use the matching snapshot storage factor; temporal inventory and FaIR differences use the complete 2035–2064 campaign storage factor, including pre-operation events. This is linear unit conversion of reviewed results, not a new LCA/FaIR solve. The 2025 gas boiler gives way to the source heat-pump configuration in the future cases; keep that foreground change explicit. Capture electricity and gas shown here are totals per stored tonne; published per-captured-tonne coefficients have already been scaled. Approximate chalk slurry is the previously approved public quantity scaled to this basis, not pure dry limestone. Fossil/mineral and non-fossil carbon remain distinct, and avoided fossil release is not atmospheric removal. All diagrams have outgoing CO₂ arrows to an atmosphere destination and retain linked inventory sources; PDF export prints one page per case.',
        "key": "supply-chain",
    },
    {
        "title": "What does a present-day score tell us?",
        "phase": "Current static",
        "seconds": 210,
        "cue": "Read the four panels in the same order; explain their references and units.",
        "notes": "Show four current-static panels. DACCS/BECCS use the reviewed SETAC case results. "
        "Cement is CCS minus BAU for the same clinker service, not a negative air-removal "
        "credit assigned to captured fossil carbon. ERW is newly calculated from the corrected "
        "foreground and the local REMIND-EU SSP2-PkBudg1000 2025 matrix. The source backgrounds "
        "and references remain documented; they have not been made identical by relabelling. An "
        "ordinary aggregate GWP100 score retains neither a common calendar endpoint nor the "
        "emission/removal sequence. Mention energy and transport hotspots while reading the "
        "panels rather than adding a separate hotspot slide.",
        "key": "current",
    },
    {
        "title": "Would today’s supply chain describe a future project?",
        "phase": "Discussion pause 1 · 3 minutes",
        "seconds": 180,
        "cue": "Give 30 seconds to think, take two responses, then move from today’s suppliers to future "
        "systems.",
        "notes": "Three minutes: thirty seconds to think, two short responses, then a bridge. Imagine a "
        "project beginning in 2035. Which present-day assumptions would be fragile over its "
        "life? Look for electricity and heat, industrial technologies, process efficiency, "
        "scale and coproduct markets. Current-static LCA remains useful for baseline hotspots. "
        "The next step adds conditional future production systems.",
        "key": "pause-current",
    },
    {
        "title": "The same year can mean very different supply systems",
        "phase": "Scenarios and prospective LCA",
        "seconds": 180,
        "cue": "Compare the two actual 2050 pathway values, then connect each project to the suppliers "
        "it needs.",
        "notes": 'The two plotted curves reuse the stored REMIND-EU / SSP2 global net CO₂ trajectories. Both share about 43.2 Gt/year in 2025. In 2050 the NPi path is about 32.2 and the PkBudg1000 path about 9.2 Gt/year, a gap of 23.0 Gt/year. Relative to that shared 2025 level, the decreases are about 26% and 79%; these percentages describe global net emissions, not a reduction factor to multiply through an LCA. The values are read from stored source rows without interpolation. NPi and the carbon-budget configuration condition different investments and technology deployment, but this is not a prediction or a controlled attribution of every difference to policy. The global curves provide context; regional and sector-specific trajectories inform the actual future suppliers. DACCS energy burdens may fall with cleaner power and heat. BECCS electricity and heat credits can shrink when the displaced energy becomes cleaner. ERW grinding and transport depend on power and haulage technology. Cement depends on kiln fuels, capture heat/electricity and design. These are qualitative mechanisms, not newly calculated technology scores. The four cases keep their references and normalized services. The next slide explains how an IAM generates such conditional pathways; the scenario-layer and premise slides then explain the encoding and inventory translation.',
        "key": "pathways",
    },
    {
        "title": "IAMs connect economies, land, resources and climate",
        "phase": "Scenarios and prospective LCA",
        "seconds": 165,
        "cue": "Trace cross-sector demands and constraints, then identify the IAM families and distinguish their scope from this lecture’s REMIND-EU results.",
        "notes": 'Follow three columns: assumptions, linked sectors and constraints, conditional outputs. The central map now deliberately extends beyond energy. Economy, demand, consumption, trade and investment interact with energy/industry; land, food, agriculture and forestry; transport/buildings; and water/material resources. Their activities and interactions lead to emissions and environmental responses, including climate and carbon-cycle processes. Coupled modules may be inside one model or linked externally. This is a conceptual map of IAM domains, not an assertion that every IAM contains every module or feedback shown. IMAGE and GCAM documentation motivate the broad coverage; REMIND-MAgPIE illustrates energy-economy and land-use model coupling. Do not imply all IAMs solve a single perfect-foresight welfare optimization: algorithms and linkage architectures differ. Cross-sector competition matters for the lecture: bioenergy can compete for land/water, electrification changes electricity demand, and industrial heat/material routes affect suppliers. The model strip identifies six widely used families: REMIND-MAgPIE, IMAGE, MESSAGEix-GLOBIOM, GCAM, AIM/CGE and WITCH. Original logos are copied unchanged and linked to model/team sites. The MAgPIE and MESSAGEix marks identify components of model families; IMAGE uses the PBL host mark and GCAM uses the UMD partner mark, explicitly captioned as team marks, rather than fabricated model logos. Logo provenance and hashes are in data/iam_logos.json. This is a recognition strip, not the complete list of IAMs and not a claim that all six generated the lecture results: the lecture retains REMIND-EU. The left graph is the shared SSP2 population input. The right graph remains the stored MAGICC7 global-mean temperature medians, relative to 1850–1900, for NPi/PkBudg1000. These are background scenario trajectories, not warming caused by the four project LCAs. Dataset vintage and numerical results remain unchanged. References: PBL IMAGE framework, https://models.pbl.nl/image/IMAGE_framework; GCAM documentation, https://jgcri.github.io/gcam-doc/; Baumstark et al. (2021), DOI 10.5194/gmd-14-6571-2021.',
        "key": "iam",
    },
    {
        "title": "Scenarios combine development stories and climate assumptions",
        "phase": "Scenarios and prospective LCA",
        "seconds": 165,
        "cue": "Distinguish the five SSP stories from the five AR6 emissions examples, then explain the IPCC’s assessment role and this lecture’s scenario codes.",
        "notes": 'Start with the compact scenario-layer visual reused from the workshop. The left list summarizes all five Shared Socioeconomic Pathways: SSP1 sustainability; SSP2 middle-of-the-road development; SSP3 regional rivalry; SSP4 inequality; SSP5 fossil-fuelled development. These describe socioeconomic conditions, not a unique emission trajectory or a forecast. The centre branches SSP1 into two climate pathways to show the distinction explicitly: there is no one-to-one mapping of the five stories to the five illustrative AR6 WGI scenarios. The right list uses the AR6 WGI core illustrative emissions set: SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5, from very low to very high emissions. The suffix is an approximate radiative-forcing level in 2100, expressed in W/m², not a temperature in degrees Celsius, a carbon price or a pathway probability. SSP1 appears twice and SSP4 is absent from that illustrative set; other combinations exist and require feasibility checks in their model/experiment. RCP names belong to the earlier forcing-pathway framework; an SSPx-y label combines a socioeconomic storyline and a forcing pathway, and similar numeric labels are not proof of identical physical trajectories across generations. Do not relabel the lecture NPi/PkBudg1000 results as any of those five AR6 scenarios: these are separate model-specific policy configurations under SSP2 and REMIND-EU. The worked example retains NPi implemented national policies versus a PkBudg1000 carbon-budget constraint, without inferring an exact AR6 warming category. Research teams develop IAM scenarios and climate simulations. The IPCC assesses the published evidence: WGI physical climate science; WGII impacts, adaptation and vulnerability; WGIII mitigation options/pathways. The IPCC is neither the developer of this premise package nor a provider of technology-specific LCA scores. No likelihood ranking of the five scenarios is implied. Sources: IPCC AR6 WGI Chapter 1, Cross-Chapter Box 1.4 and SPM Box SPM.1/Figure SPM.4; IPCC Special Report on 1.5°C Chapter 2 for socioeconomic SSP narratives; IPCC working-groups overview. All are linked on the slide. No scenario inputs or project results changed.',
        "key": "scenario",
    },
    {
        "title": "Trace a scenario change into the LCA result",
        "phase": "Scenarios and prospective LCA",
        "seconds": 210,
        "cue": "Switch the scenario and material selector; connect the changing suppliers to all four "
        "projects.",
        "notes": "Reuse the SETAC IAM-to-premise chart, including the actual market extracts. Show how "
        "electricity, heat and material routes change. State the voltage and market boundaries. "
        "Map the implications back to DACCS, BECCS, ERW and cement capture. The charts are "
        "stored extracts; no scenario build runs in the web application.",
        "key": "suppliers",
    },
    {
        "title": "Future supply chains change both burdens and credits",
        "phase": "Scenarios and prospective LCA",
        "seconds": 240,
        "cue": "Read 2025, 2035 and 2050; switch the future bar scenario while keeping both net-score diamonds visible.",
        "notes": "Compare the same four cases at 2025, 2035 and 2050. The 2025 bar and black diamond retain each case's documented current reference: DACCS/BECCS and cement use their existing NPi current-static source; ERW retains its existing PkBudg1000 current snapshot. The radio selector changes the contribution bars for the two future years only, with SSP2-PkBudg1000 explicitly selected and labelled as the default. Hollow grey diamonds show NPi net scores and filled teal diamonds show PkBudg1000 net scores at both 2035 and 2050 regardless of which bars are selected. Markers are shifted slightly left/right inside each ordinal year slot for visibility; these are not extra dates. The large number is labelled as the selected scenario's 2050 net score. Hover labels expose the scenario and exact net/contribution values. The new DACCS/BECCS/ERW 2035 and alternate-scenario results were calculated from the unchanged foreground workbooks and exact year-matched background matrices, not by interpolating displayed LCIA scores. The PkBudg1000 archive is the existing 2.5.4 build; NPi retains the original source's read-only annual cache since its original archive is absent locally. Forward static LCAs independently check the complete signed foreground/root attribution, and all existing 2050 CDR scores and the PK ERW score are reproduced to numerical precision. The historical source builds differ, so the scenario comparison is not a controlled policy-only experiment. Cement uses reviewed 2035/2050 NPi and PkBudg1000 bundles, each as CCS minus BAU for matching clinker output per physical stored tonne. The year-specific storage normalization was checked identical across the two policy configurations; do not substitute a lifetime denominator. Only foreground CO₂ is labelled fossil/non-fossil. All supplier contributions retain full upstream effects, including biomass carbon; opposite signs remain separate. All three bars close to the selected net scores, and both scenario markers retain their independent source totals. Cleaner suppliers can reduce burdens and can reduce displaced-energy credits. These are static snapshots, not a new time-explicit cohort, FaIR run or harmonized technology ranking. PDF export resets to the labelled PkBudg1000 default and includes both scenario markers. Provenance and source hashes are in data/static_scenario_results.json and the reproduction script calculate_static_scenarios.py.",
        "key": "future",
    },
    {
        "title": "Is one future snapshot enough for a long-lived system?",
        "phase": "Discussion pause 2 · 3 minutes",
        "seconds": 180,
        "cue": "Discuss both delayed uptake and electricity/heat suppliers changing over the operating life.",
        "notes": "Three minutes. Hold production conditions fixed for the thought experiment: two "
        "projects have equal GWP100 totals but one removes CO₂ fifty years later. What "
        "information is missing? Expected answers include construction before operation, forest "
        "regrowth, dissolution, atmospheric equilibration and replacement schedules. Then relax "
        "the fixed-background assumption: a plant can buy electricity and heat from changing "
        "supply mixes throughout its operating life. Even unchanged annual foreground demand "
        "can have different upstream impacts in different years. Match each dated demand to "
        "the scenario's year-specific suppliers rather than applying one future snapshot to "
        "the entire operating period. The supplier strip is conceptual, not a quantified "
        "decarbonization trajectory or an assumption that every supplier improves. A future "
        "snapshot, evolving background and event timing are separate modelling choices.",
        "key": "pause-future",
    },
    {
        "title": "Equipment and carbon follow different clocks",
        "phase": "Time-explicit LCA",
        "seconds": 210,
        "cue": "Read each pair of equipment and carbon lanes, then follow the carbon beyond operation.",
        "notes": "Construction can precede operation. The reviewed BECCS harvests initiate long regrowth "
        "tails; shared pre-decision forest history cancels against its reference. Geological "
        "storage continues beyond plant operation. Coastal dissolution and atmospheric uptake "
        "are distinct clocks. The ERW timing profile is assumed and literature-informed, not "
        "field-calibrated. ERW grinding and spreading now operate for twenty years, 2030–2049; "
        "this is not an uptake cutoff. Its "
        "uncertain dissolution and subsequent uptake can extend for decades or centuries after "
        "each annual deployment. The connected arrows are schematic, not a predicted completion date. "
        "Geerts et al. (2025) and He & Tyka (2023) distinguish mineral dissolution from air–sea "
        "exchange.",
        "key": "clocks",
    },
    {
        "title": "From scenarios to dated supply chains",
        "phase": "Time-explicit LCA",
        "seconds": 210,
        "cue": "Follow the data handoff, then explore the four actual temporal-routing graphs.",
        "notes": "Reuse the SETAC annual-matrix stacks in a two-pane premise-to-TRAILS workflow. Dated routing expands "
        "explicit foreground branches, and year-specific matrix solves retain the remaining "
        "supply chain. Stopping graph expansion does not delete the residual inventory. Keep "
        "demand year, matrix year, biosphere-event year and response year distinct.",
        "key": "trails",
    },
    {
        "title": "What drives the GWP score, and when?",
        "phase": "Time-explicit LCA",
        "seconds": 180,
        "cue": "Read annual signed areas against the left axis and the red cumulative line against the right axis.",
        "notes": "The cumulative curve sums the complete annual inventory, including contributions "
        "before the visible -5-year window. Do not restart the sum at zero at the display "
        "boundary. The selector and separate cumulative-area graphs are removed. Annual signed "
        "areas connect the unchanged annual values continuously rather than using stair steps, with a thick red "
        "cumulative net line on the right-hand axis. Axis zeros are aligned; their different "
        "units remain explicit. Both the primary annual scale and secondary cumulative scale "
        "are shared across all four panels, with outward-rounded bounds covering every visible "
        "signed stack. The cumulative lower bound is the requested -1000 kg CO2-eq; its "
        "+500 upper bound preserves zero alignment. X-axis labels show calendar years only: "
        "2030/2080/2130 for the three CDR cases and 2035/2085/2135 for cement. All four x-axes end at +100 years, while the "
        "complete inventory and tails remain in the data and totals. The ERW model retains all dated foreground uptake; upstream supplier events "
        "are represented at fixed depth one with full residual matrix solves. The other cases "
        "retain their reviewed routing assumptions. Different temporal models are disclosed "
        "with their sources. Compare annual rates and their accumulated balance on the same graph. "
        "Dating GWP100 is not yet dynamic climate characterization. Signed stacks now show "
        "responsible root-activity types, including both signs within a type. The red curve "
        "is cumulative net GWP100; the separate black annual net line is removed. DACCS/BECCS retain the reviewed responsible-root series; "
        "ERW roots are extracted from the same depth-one calculation and match each stored "
        "annual score; cement uses the released foreground-stage attribution, CCS minus BAU, "
        "never adding the alternative flow view. Cumulative components include all years before "
        "the displayed window. ERW here remains the explicitly fast illustrative 10-year/1-year "
        "reference; the later sensitivity page opens with 100-year dissolution and a 5-year "
        "lag, not a field estimate. All annual activity and contributions are divided by the "
        "complete project's physical service, rather than treating one tonne per year as "
        "the functional unit. DACCS/BECCS already use the reviewed per-net-tonne fields: "
        "their full-cohort storage denominators are 1,944,000 t and 149,394.49520357835 t, "
        "respectively. Cement already uses its campaign clinker-to-physical-storage factor "
        "for matching-output CCS minus BAU. These normalized results must not be divided "
        "by storage a second time or scaled to force a -1000 kg CO2-eq result. ERW's entire "
        "20-year campaign is 1.25 t rock with 1 t eventual gross uptake potential, modelled "
        "with full reference realization on this slide. Its panel retains 'modelled uptake' "
        "rather than claiming verified permanent storage or net removal. The common unit "
        "banner and all panel labels make the whole-lifetime normalization visible. The "
        "temporal palette separates actual biogenic uptake, avoided fossil/mineral kiln CO2, "
        "and avoided biogenic kiln CO2 release. Only the direct clinker CO2 portion is replaced "
        "using the reviewed public temporal carbon display; no full-system flow decomposition "
        "is mixed into supplier roots. Small remaining clinker-root effects retain a separate "
        "residual and annual closure. Avoided biogenic release is not newly dated forest growth. "
        "Capture was previously misclassified as Materials + equipment. Its stage combines "
        "supplies and an avoided-heat-production credit; it now has a Capture operation + heat "
        "credit label. Its lifetime CCS-minus-BAU net is about -5.54 kg CO2-eq per stored "
        "tonne, combining positive and negative year-specific pieces. Kiln fuels are grouped "
        "with fuel/biomass supply. Remaining raw-material root differences sum to +2.37 kg "
        "CO2-eq per stored tonne, with -0.49 negative and +2.86 positive pieces. These are "
        "dated CCS-minus-BAU differences, not physical carbon removal by equipment. The "
        "coarse inherited stage export cannot identify each supplier behind a particular "
        "raw-material-year difference; routing convergence remains untested. No new material-"
        "removal mechanism, inventory or climate response is inferred. Electricity + heat "
        "has separate positive and negative area labels; the negative area is hatched. For "
        "DACCS the earlier annual net-sign split was misleading: within the same electricity "
        "root, substantial positive emissions and negative biomass-related effects offset "
        "one another. A reproduction of the unchanged depth-four inventory now aggregates "
        "characterized elementary flows by root/year/flow before separating signs. This "
        "cancels internal temporal-correction entries before sign classification. The two "
        "areas retain the electricity activity label rather than displaying upstream CO2 "
        "origins as separate categories. Their sum reproduces every original annual root net "
        "to about 1.3e-13 kg CO2-eq/t stored. In 2042 the positive part is +10.16 and the "
        "negative part -10.30, giving the original -0.14 net. Capture/heat-pump electricity "
        "demand is constant across 2030–2049; the normalized demand is about 58.21 kWh in "
        "each year, summing to 1.1643 MWh across this future cohort's one-tonne service. "
        "This is not a plant-capacity decline. Positive supply-chain impacts decline over "
        "the scenario, while biomass uptake increasingly offsets them; negative effects can "
        "continue after operation ends. Other cases retain their published root/stage "
        "aggregation, so gross positive/negative area magnitudes are not a harmonized "
        "cross-technology ranking. All net and cumulative results remain unchanged. "
        "The ERW cumulative curve has a translucent timing-scenario envelope for 10/1, 30/5 "
        "and 100/5-year dissolution/air-sea timescale combinations. This is not a confidence "
        "interval or full uncertainty range: supplier inventory, total rock and full reference "
        "realization are held fixed. Annual areas retain the fast reference and the red line "
        "retains its original cumulative sum; the band varies foreground CO2 uptake timing "
        "using the same twenty annual batches. FaIR is not recalculated by this band. The "
        "10-year/1-year case is illustrative, not a consensus field window. Foteinis et al. "
        "(2023, doi:10.1021/acs.est.2c08633) used a ten-year dissolution assumption for their "
        "10-micrometre base case. Geerts et al. (2025, doi:10.5194/bg-22-355-2025) discuss "
        "10–500-year full dissolution under field conditions, depending on grain size. He & "
        "Tyka (2023, doi:10.5194/bg-20-27-2023) find substantial air-sea equilibration over "
        "3–4 years at many sites and 8–10 at some, with much longer deep-ocean return tails. "
        "Our one-year lag parameter is an exponential kernel timescale, not a fixed one-year "
        "wait or complete equilibration within one year. Do not directly translate those "
        "published equilibration horizons into fitted exponential timescales.",
        "key": "inventory",
    },
    {
        "key": "pause-gwp",
        "title": "Same GWP100. Same climate outcome?",
        "phase": "Discussion pause · climate metrics",
        "seconds": 180,
        "cue": "Use the four timeline diagrams to ask whether dated GWP100 scores answer a calendar-based climate question.",
        "notes": "After the dated GWP areas, ask what the metric still discards. Four native SVG "
        "diagrams form a 2-by-2 grid, with no separate overview graph. The first uses "
        "two equal positive fossil-CO2 emissions: one tonne in 2030 or in 2080. With fixed "
        "GWP100 each scores 1,000 kg CO2-eq. Their accounting windows are 2030–2130 and "
        "2080–2180, while the common study endpoint is 2100. Bars depict characterization "
        "windows, not atmospheric lifetimes or calculated climate trajectories. Ask what can "
        "be concluded about effects before that endpoint. Allow thirty seconds to think, "
        "invite responses, then use the four visible timeline hints. Placing fixed-factor scores along a "
        "calendar axis does not make their characterization time-dependent. GWP compares "
        "integrated radiative forcing over a chosen relative horizon; it does not specify "
        "peak or endpoint warming. Card one merges the emission-date and moving-window "
        "arguments into one question about effects before the shared 2100 endpoint; "
        "do not restore the earlier redundant separate endpoint card. Card two asks "
        "whether immediate versus delayed CO2 removal can be distinguished by an "
        "aggregate zero score. It shows +1 and minus 1 tonne "
        "in 2030 versus +1 tonne in 2030 and minus 1 in 2080; its shaded gap is elapsed "
        "time, not calculated forcing. The next slide supplies the climate-response "
        "demonstration, so solicit predictions rather than duplicate that explanation. "
        "Card three contrasts simultaneous 2030 CH4-like and CO2-like pulses scaled "
        "to equal illustrative forcing areas over 100 years. Equal GWP100 scores do "
        "not mean equal emitted masses or equal forcing at each date. The early "
        "methane-like effect fades while the CO2-like tail persists beyond 2130. "
        "The curves are hand-authored illustrative shapes, not fitted gas impulse "
        "responses, temperature curves, FaIR results or scenario calculations. "
        "The fourth contrasts schematic indexed CO2, CH4 and N2O background concentrations "
        "with fixed CH4/N2O GWP100 factors. The paths are illustrative, not the lecture's "
        "REMIND scenario or a numerical forecast; neither magnitude nor direction of GWP "
        "change is implied. Background gas concentrations affect marginal radiative "
        "efficiencies, including that of the CO2 reference in the denominator. Gas "
        "lifetimes and climate-carbon cycle feedbacks also depend on the background. "
        "A fixed reference remains a valid reporting convention, but cannot by itself "
        "represent the physical response in an evolving future atmosphere. For that "
        "question, use a consistent scenario background for the gas and the reference. "
        "GWP remains useful for its defined task; choose a metric for the actual "
        "question. Bridge to the following delayed-removal experiment, then climate response "
        "and CO2-pulse-equivalence. No new technology results are calculated. Sources: IPCC "
        "AR6 WGI Chapter 7, section 7.6; Levasseur et al. (2010), doi:10.1021/es9030003; "
        "Reisinger, Meinshausen and Manning (2011), doi:10.1088/1748-9326/6/2/024020. "
        "All four diagrams are visible in live and PDF views. They depict emission "
        "pulses, accounting windows, schematic gas forcing and illustrative backgrounds, "
        "not new physical climate-model results.",
    },
    {
        "title": "Later removal does not erase the earlier warming",
        "phase": "Climate response",
        "seconds": 180,
        "cue": "Emit one tonne in 2030, wait, then remove one tonne. Read the mass balance and the "
        "climate history separately.",
        "notes": "A deliberately simple CO₂-only thought experiment, not one of the four full project "
        "inventories: +1 t in 2030 and −1 t in 2030, 2050 or 2080. Select same year first, then "
        "20 and 50 years later. Same-year removal is the default in live and PDF views; "
        "both emission and removal annotations remain visible, vertically separated. "
        "In every selection the aggregate GWP100 mass balance is zero, "
        "since the CO₂ characterization factor is the same for positive and negative pulses. "
        "The shaded forcing area shows the intervening effect: later uptake reduces subsequent "
        "forcing but does not undo the earlier time-integrated warming influence. The curve is "
        "a marginal superposition of stored FaIR CO₂ pulse responses under one background, not "
        "a fresh nonlinear coupled run. A negative forcing difference late in the curve is "
        "possible; it does not erase earlier positive forcing. Keep the reference as no added "
        "pulses. Pulse-equivalence is introduced only after the audience has seen the full "
        "project climate responses. Its median-area toy value is now on the dedicated metric "
        "slide, not on this introductory plot.",
        "key": "delay",
    },
    {
        "title": "Follow all four climate responses through time",
        "phase": "Climate response",
        "seconds": 210,
        "cue": "Move the shared calendar window and compare each signed area while the vertical scales stay fixed.",
        "notes": "The branching diagram passes dated TRAILS emissions by gas into paired "
        "FaIR scenarios, then into the climate response. These four plots show forcing. "
        "One IAM source branches into the economy and atmospheric pathways, making the consistency rule explicit: use the same IAM "
        "scenario for premise's evolving LCA suppliers and the climate-background pathway. "
        "In these emissions-driven FaIR runs we supply background GHG emissions; FaIR "
        "calculates the resulting atmospheric concentrations. The project inventory is "
        "a separate dated perturbation added to that background, and the response is "
        "with-project minus without-project. Align model, pathway and scenario version, "
        "not just similar scenario labels. The retained native case results have their "
        "documented variants, including ERW's SSP2-EU21 atmosphere; this diagram explains "
        "the consistency requirement and does not claim new harmonized calculations. "
        "A two-handle calendar slider replaces the three project-age radio choices. Its "
        "default is 2030–2050 within the available 2030–2200 range, with one-year steps "
        "and at least a one-year window. Both "
        "handles control every plot's absolute calendar axis and the signed integrated "
        "forcing shown above it in pW year per square metre. Cement retains its 2035 "
        "project start; the other cases start in 2030. Their native dates are not rebased. "
        "The full stored trajectories and fixed per-case vertical scales remain unchanged. "
        "Area is calculated by trapezoidal integration over the selected window, with "
        "linear interpolation at the exact calendar boundaries, including half-year data. "
        "The translucent fill represents signed forcing; negative area means less forcing "
        "than the reference over that window. These are areas of the displayed stored "
        "median curves (cement uses CCS median minus BAU median), not ensemble quantiles "
        "of integrated responses, GWP100 scores, temperature effects or CO2 equivalents. "
        "The next slide explains configuration-level pulse normalization. ERW forcing "
        "is still the stored fast "
        "illustrative 10-year dissolution / 1-year lag reference, explicitly labelled, not a "
        "site forecast. The separate slow uptake sensitivity does not rerun FaIR.",
        "key": "response",
    },
    {
        "title": "CO₂-pulse-eq: match effects over a declared window",
        "phase": "Climate response",
        "seconds": 210,
        "cue": "Trace each project response to one common calendar window, then ask what mass of a dated "
        "CO₂ pulse matches the signed area.",
        "notes": "Apply the area-matching concept to DACCS, BECCS, ERW and cement plus CCS, "
        "using exactly the stored project curves from the preceding slide. The solid "
        "coloured curve is the project response; the dashed curve is a dated CO2 pulse "
        "scaled to the same signed area. Start with the 2020–2100 window and 2030 pulse, "
        "then change the endpoint and pulse year independently. Project inventories and "
        "their native dates never change. The displayed masses are illustrative ratios "
        "of areas of median trajectories, not configuration-first ensemble equivalents. "
        "Proper ensemble results require ratios within each FaIR configuration before "
        "summarizing. Areas use exact interpolated calendar boundaries, including native "
        "half-year time coordinates. The released +1 t reference curves are divided by "
        "1000 to obtain a per-kg response; the 2030 curve is checked against the SETAC "
        "per-kg export after recovering its half-year coordinates. ERW uses a distinct "
        "REMIND SSP2-EU21-PkBudg1000 climate background, so 39 matching reference curves "
        "were generated with its exact reviewed FaIR inputs, 841 configurations and "
        "TRAILS 1.1.1. Other cases retain their released SSP2-PkBudg1000 reference. "
        "Reference pulses range from 2005 to 2195, supporting three increasing five-year "
        "controls within 2000–2200. Negative equivalent masses indicate lower integrated "
        "forcing, not physical removals or storage. Equal areas still have different "
        "trajectories. Native foregrounds, services and climate variants are retained; "
        "this is not a harmonized technology ranking. Begin with the first tab's "
        "response → area → pulse mapping, then use the second tab's interactive overlays. "
        "PDF and the closing score table use 2020/2030/2100. No project LCI or stored "
        "project FaIR response was recalculated.",
        "key": "pulse-equivalence",
    },
    {
        "title": "Why coastal uptake arrives after deployment",
        "phase": "Interpretation",
        "seconds": 180,
        "cue": "Link grinding to upfront burdens and coastal chemistry to delayed uptake.",
        "notes": "Coastal ERW retains the Foteinis et al. source foreground with the documented "
        "corrections. Medium-voltage comminution, exact ecoinvent 3.12 truck names and "
        "duplicate supplier aggregation are now checked by a real import. Keep ocean nickel in "
        "its receiving compartment; its mobility is a conservative sensitivity. Dissolution, "
        "alkalinity transport and air-sea equilibration require site evidence. The "
        "cross-section is conceptual: neither scale nor reaction extent is measured at a site. "
        "Ask which of dissolution, alkalinity transport or air–sea exchange limits realized "
        "atmospheric uptake. Literature does not support a universal twenty-year deadline: "
        "marine olivine dissolution may take years to centuries; subsequent air–sea uptake has "
        "its own site-dependent delay and efficiency. The illustrative clocks are sensitivities "
        "rather than field estimates.",
        "key": "coast",
    },
    {
        "title": "The same rock deployment can have a much slower uptake profile",
        "phase": "Interpretation",
        "seconds": 210,
        "cue": "Change one ERW timing assumption at a time; the other three panels stay fixed.",
        "notes": "The three controls change only the ERW foreground uptake profile; DACCS, BECCS and "
        "cement remain fixed. The baseline ERW upstream climate burden comes from calculated "
        "inventory results, not the earlier fixed published 51 kg screening footprint. Holding "
        "that background fixed isolates timing. Duration is not a matched particle-size "
        "scenario: changing particle size would require changing energy and mineral kinetics "
        "together. Realization is additional to the source’s already conservative potential. "
        "This page now opens with a deliberately slow 100-year dissolution / 5-year air–sea-lag "
        "sensitivity, to make post-deployment uptake visible. It is not a new claim about the "
        "source site, and its kinetic assumptions are not propagated into the stored "
        "fast-reference FaIR curve.",
        "key": "erw-sensitivity",
    },
    {
        "title": "Choose the inventory model, then the climate question",
        "phase": "Interpretation",
        "seconds": 180,
        "cue": "Compare the questions answered by each lens, using the same four rows.",
        "notes": "Three distinct questions: current suppliers identify present hotspots; a prospective "
        "snapshot changes production conditions; time-explicit LCA preserves dates, and a "
        "climate model plus declared metric evaluates their consequences. For all four cases "
        "choose the service and reference first. A dated GWP100 series is not a response "
        "trajectory. CO₂-pulse-eq summarizes signed integrated forcing over a stated calendar "
        "window against a dated reference pulse; keep the trajectory alongside it. The "
        "numerical source snapshots and native temporal cohorts differ in lifetimes and "
        "backgrounds, so do not interpret their score differences as timing alone.",
        "key": "lenses",
    },
    {
        "title": "From a project question to a dated climate result",
        "phase": "Tooling and sources",
        "seconds": 75,
        "cue": "Trace one project from evidence through future suppliers, dated inventory, climate "
        "response and declared metric.",
        "notes": "The workflow separates analyst choices from tool roles. Start with service, "
        "counterfactual and site/technology evidence. ecoinvent supplies linked unit-process "
        "data; IAMs supply conditional trajectories; premise translates selected scenario "
        "signals into future inventory coefficients. TRAILS routes the dated foreground through "
        "changing backgrounds and constructs a species-resolved inventory. FaIR converts that "
        "perturbation into forcing/temperature under a stated climate background. The analyst "
        "then chooses the calendar window/reference pulse and interprets the trajectory and "
        "equivalent together. A tool cannot supply missing ERW uptake evidence or choose a land "
        "counterfactual for you.",
        "key": "workflow",
    },
    {
        "title": "Where to start with your own study",
        "phase": "Tooling and sources",
        "seconds": 30,
        "cue": "Choose a task, explain the resource's purpose, and identify the first practical step.",
        "notes": "Four reading routes explain what to do with the references: define "
        "system boundaries and start building the foreground in Brightway, then frame the "
        "temporal/climate question using Levasseur and IPCC metrics; create prospective "
        "suppliers using ecoinvent system-model guidance and premise's first-scenario "
        "example; calculate temporal LCA using the TRAILS quickstart and climate response "
        "using FaIR's calibrated-ensemble example; adapt ERW using the reviewed workbook, "
        "source supporting inventory and a marine-weathering synthesis. Each card gives "
        "a purpose and concrete first step. The lower links return to four source lectures "
        "as worked examples. Official tool documentation links were checked directly. "
        "The references support study design and implementation; they do not replace "
        "site-specific uptake evidence or the choice of service/reference.",
        "key": "sources",
    },
    {
        "title": "Which dates could change the answer in your study?",
        "phase": "Open discussion · 20 minutes",
        "seconds": 1200,
        "cue": "Begin with Professor Park’s ERW project, then invite questions from students.",
        "notes": "Twenty minutes: begin with the lab’s ERW project and what would be needed to date the "
        "actual uptake, then invite questions about counterfactuals, horizons, IAM assumptions "
        "and implementation. The presenter’s discussion timer is separate from teaching. Keep "
        "the same four-case comparison available when returning to earlier slides.",
        "key": "discussion",
    },
    {
        "key": "thanks",
        "title": "Thank you",
        "phase": "Open discussion + closing",
        "timing_phase": "discussion",
        "seconds": 1200,
        "cue": "Thank Professor Park and the audience; leave your contact details visible.",
        "notes": "Use this results table as the backdrop for twenty minutes of open discussion. Thank Jooyoung Park, the graduate "
        "students and research group. Reuse the SETAC conclusion/contact/funding layout, "
        "adapted to the four Seoul cases. Recap future conditions, event dates and the "
        "fixed-window climate metric. The left pane now summarizes current 2025, future "
        "2035 and full time-explicit GWP100 scores plus approximate median-curve "
        "CO2-pulse-equivalents for 2020–2100 with a 2030 reference. It reuses the SETAC "
        "table/contact/funding composition and the exact readers used on the result slides. "
        "The final column scales each complete native-service response to match a negative "
        "one-tonne CO2 pulse in 2030 over 2020–2100, then multiplies by gross captured "
        "CO2 per service (including capture-to-storage losses), or eventual ERW uptake. "
        "It uses unrounded curve-area equivalents, not the rounded values shown in the table. "
        "This is approximate linear scaling of the displayed median curves, with the same "
        "operation dates and native backgrounds, not a new FaIR run or ensemble statistic. "
        "For cement it is flue-gas capture producing an avoided-emission benefit relative "
        "to equal-clinker BAU, not physical atmospheric removal. "
        "Operation-period labels are 2030–2049 for DACCS, BECCS and ERW, and 2035–2064 "
        "for cement; they do not truncate the full life-cycle GWP score. Three takeaways "
        "replace the former pulse-window box, with window/reference retained in the header. "
        "This slide adds no timed teaching segment.",
    },
]
# The reference-system slide duplicated the explanations on the process maps
# and result panels. Give its two minutes to those existing slides instead.
for _slide in SLIDES:
    if _slide["key"] in ("supply-chain", "current"):
        _slide["seconds"] += 60
# Remove the former slides 20–22; spend their 9.5 minutes on the retained
# timing discussion, four-case climate comparison and workflow synthesis.
SLIDES = [s for s in SLIDES if s["key"] not in {"coast", "erw-sensitivity", "lenses", "discussion"}]
for _slide in SLIDES:
    _slide["seconds"] += {"clocks":60,"pause-gwp":60,"response":120,
                          "pulse-equivalence":180,"workflow":105,"sources":45}.get(_slide["key"],0)
# Fit the introduction into the existing 70-minute teaching allocation.
for _slide in SLIDES:
    if _slide["key"] in {"cover", "response", "pulse-equivalence", "workflow"}:
        _slide["seconds"] -= 15
CORE_COUNT = len(SLIDES)
BACKUPS = [
    {
        "title": "The conventional and prospective matrix equations",
        "phase": "Backup · equations",
        "seconds": 0,
        "cue": "Show this only if the audience asks how the matrix calculation works.",
        "notes": "Production-positive/input-negative A solves Ax=f. B maps activity levels to elementary "
        "flows; characterization gives cᵀBA⁻¹f. A future scenario changes A, B and foreground "
        "assumptions, with consistent service scaling.",
        "key": "matrix-equations",
    },
    {
        "title": "Time-resolved inventory and dynamic characterization",
        "phase": "Backup · equations",
        "seconds": 0,
        "cue": "Separate the time indices before reading the sums.",
        "notes": "The general time-indexed system dates product and biosphere exchanges. The response "
        "formulation is a marginal convolution; FaIR can instead simulate the dated species "
        "perturbation in a defined scenario background. These are conceptual definitions, not "
        "claims about one internal solver.",
        "key": "temporal-equations",
    },
    {
        "title": "What is reused, calculated and assumed?",
        "phase": "Backup · evidence",
        "seconds": 0,
        "cue": "Use this to resolve questions about comparability and validation.",
        "notes": "The four-study comparison preserves native services, years and references. ERW static "
        "results and depth-one dated LCI/FaIR are newly calculated from the corrected imported "
        "foreground. IAM, SETAC, LCA-through-time and cement-webinar assets are reused without "
        "changing their source applications. Source hashes and retained limitations are "
        "recorded with the artifact.",
        "key": "provenance",
    },
    {
        "key": "pulse-equation",
        "title": "CO₂-pulse-equivalence: definition and reporting",
        "phase": "Backup · climate metric",
        "seconds": 0,
        "cue": "Read the numerator and denominator over the same window.",
        "notes": "Define CO₂-pulse-equivalence here as the integrated-radiative-forcing equivalent, "
        "following TRAILS fixed-window equivalence. Compare the inventory perturbation and a "
        "reference CO₂ pulse under the same climate background over exactly the same calendar "
        "window. Normalize the inventory’s signed integrated forcing by forcing per kilogram of "
        "the dated reference pulse. In a full calculation, take the ratio within each FaIR "
        "configuration before summarizing ensemble quantiles. This differs from simply summing "
        "annual GWP100 scores: ordinary GWP100 gives every event a fresh 100-year horizon, so "
        "late uptake can cancel early emissions in the aggregate despite interim warming. The "
        "common window retains the event dates and remaining time to the endpoint. Show the "
        "next visual as a methodological mapping for all four projects, not newly computed "
        "four-case pulse-equivalent results. Their native cohorts and source backgrounds "
        "differ; a controlled comparison requires a common scenario, calendar window and "
        "reference-pulse year. Negative values indicate lower integrated forcing than the "
        "reference, not physical tonnes removed. Equal areas do not guarantee identical forcing "
        "or temperature paths, permanent storage, or neutrality at every date. State "
        "background, start, end and pulse year with every score. This is not GWP* or a "
        "universal replacement for GWP. The preceding two-pulse example illustrates the timing "
        "pitfall without introducing a new technology ranking. Sources: Levasseur et al. "
        "(2010), DOI 10.1021/es9030003; TRAILS theory, fixed-window CO2 pulse equivalence; "
        "SETAC pulse-equivalence teaching slide.",
    },
    {
        "key": "erw-timing-evidence",
        "title": "ERW uptake is not bounded by a plant lifetime",
        "phase": "Backup · ERW timing",
        "seconds": 0,
        "cue": "Compare the three uptake clocks at year twenty; distinguish sensitivity from field "
        "evidence.",
        "notes": "Marine olivine dissolution and air–sea equilibration are distinct processes. Geerts et "
        "al. (2025) describe dissolution over years to centuries and unresolved field controls. "
        "He & Tyka (2023) show location-dependent equilibration after alkalinity addition; that "
        "does not establish mineral dissolution times. The plotted shrinking-core/exponential "
        "profiles are analyst sensitivities using unchanged uptake potential and deployment "
        "burdens. They are not a particle-size optimization or a confidence interval. The "
        "stored reference FaIR curve uses 10-year dissolution/1-year lag; the separate explorer "
        "opens with 100-year/5-year sensitivity. No universal twenty-year completion date is "
        "supported.",
    },
    {
        "key": "root-attribution",
        "title": "How root-activity contributions reconcile to the score",
        "phase": "Backup · attribution",
        "seconds": 0,
        "cue": "Trace one supplier through its upstream chain, then explain the sign-preserving "
        "grouping.",
        "notes": "DACCS/BECCS responsible roots come from the reviewed SETAC tables. ERW first-tier "
        "static intensities are independently checked against the original static score; "
        "depth-one temporal roots reproduce the stored annual inventory within 0.001 kg CO2-eq. "
        "Cement uses matching CCS-minus-BAU subprocess differences for static and released "
        "foreground-stage contributions for temporal. The alternative elementary-flow "
        "decomposition is not added. Positive and negative root-year scores remain separate "
        "within each type; full histories, including pre-window events, remain in cumulative "
        "curves. Static and temporal totals use native services but different lifetime/cohort "
        "treatments.",
    },
]
BACKUPS.extend([
    {
        "key": "ssp-narratives",
        "title": "Five SSPs: the development stories behind the labels",
        "phase": "Backup · SSP narratives",
        "seconds": 0,
        "cue": "Compare institutions, demand and technology before adding climate policy.",
        "notes": "Adapted from the IAM workshop SSP1–SSP3 and SSP4–SSP5 narrative lessons. "
        "SSP1 combines inclusive development and resource efficiency; SSP2 continues uneven historical trends; "
        "SSP3 emphasises security and regional fragmentation; SSP4 concentrates capabilities among elites; "
        "SSP5 combines strong development with fossil-intensive demand. The qualitative mitigation/adaptation "
        "challenge pairs are low/low, medium/medium, high/high, low/high and high/low respectively. "
        "These describe relative socioeconomic challenges, not guaranteed policy outcomes or a ranking of "
        "scenario probabilities. Some SSP/forcing combinations are infeasible in particular models. "
        "Sources: O’Neill et al. (2017), DOI 10.1016/j.gloenvcha.2015.01.004; IPCC SRCCL Box SPM.1.",
    },
    {
        "key": "climate-trajectories",
        "title": "RCPs and emissions pathways: read the whole trajectory",
        "phase": "Backup · climate trajectories",
        "seconds": 0,
        "cue": "Separate forcing levels from emissions histories and temperature responses.",
        "notes": "Adapted from the IAM workshop RCP forcing lesson and the AR6 illustrative set on slide 10. "
        "CMIP5 RCP2.6 peaks near 3 W/m² then declines; RCP4.5 and RCP6.0 stabilise without overshoot "
        "after 2100; RCP8.5 keeps rising. RCPs do not define unique socioeconomic narratives. "
        "The AR6 examples combine SSP stories with forcing pathways; 1.9 and 7.0 are not members of "
        "the original four-RCP set. CO₂ trends describe global net anthropogenic emissions, not all "
        "greenhouse gases and not an individual plant. The suffix is approximate forcing in 2100, "
        "not GMST or an exact equivalence between framework generations. Equal endpoint forcing "
        "does not imply equal peak temperature or cumulative impacts. The lecture's warming labels "
        "refer instead to its own stored MAGICC7 median GMST in 2100: SSP2-NPi 2.5689 °C and "
        "SSP2-PkBudg1000 1.7560 °C above 1850–1900. They are not renamed AR6 illustrative scenarios. "
        "Sources: van Vuuren et al. (2011), DOI 10.1007/s10584-011-0148-z; IPCC AR6 WGI Box SPM.1/Figure SPM.4.",
    },
])
# The origin view is an alternative partition; it is never added to stage roots.
for _slide in SLIDES:
    if _slide["key"] in ("current", "future"):
        _slide["notes"] += (
            " Display fossil CO₂ and non-fossil CO₂ only for explicit foreground exchanges. "
            "Each supplier contributes its complete upstream GWP at the foreground boundary, "
            "grouped by root activity type. Biomass uptake and combustion in DACCS electricity "
            "supply remain inside the electricity contribution; do not display those upstream flows "
            "separately or add a flow decomposition to the root totals. DACCS/BECCS use a new "
            "signed first-tier extraction with direct foreground exchanges separated, matching the "
            "stored 2025 and 2050 totals to numerical precision. The background reconstruction "
            "and original static solve independently validate the decomposition. ERW retains its "
            "checked first-tier supplier intensities and direct uptake. Cement uses released "
            "foreground CO₂ and matched provider/subprocess scores, CCS minus BAU; a negative "
            "fossil CO₂ difference means avoided release, not atmospheric removal. Other direct "
            "GHGs (including BECCS CH₄ and N₂O) stay separate from CO₂. Positive and negative "
            "root contributions remain separate, with a shared palette/scale and net diamonds. "
            "No all-supply-chain CO₂-origin view is available on the displayed result slides. "
            "Locations: DACCS/BECCS Northern Europe (ENC), no specific physical plant site; "
            "ERW a generic European coastal RER foreground, without field-calibrated uptake; "
            "cement Aalborg, Denmark with North Sea storage. Current static uses 2025 and the "
            "prospective comparison adds 2035 and 2050. Time-explicit DACCS/BECCS operate 2030–2049; "
            "ERW grinding/spreading also operate 2030–2049 in twenty equal batches; cement operates 2035–2064. "
            "Static snapshots collapse the same total rock service into their selected year's background."
        )
    elif _slide["key"] in ("inventory", "erw-sensitivity"):
        _slide["notes"] += (
            " The time-explicit contribution chart uses responsible foreground root types, "
            "with each supplier retaining its full upstream effects. Cement keeps its released "
            "foreground-stage attribution; no full-chain elementary-flow origin breakdown is "
            "shown. The ERW sensitivity shows net balances while changing only ERW uptake. "
            "Upstream biosphere uptake/emissions are not separately overlaid on root totals."
        )
    elif _slide["key"] == "response":
        _slide["notes"] += (
            " Cement's purple forcing curve remains a combined response including fossil/mineral "
            "and non-fossil carbon and other greenhouse gases. The coloured origin key names the "
            "mechanisms, not separately calculated FaIR response curves. The released medians do "
            "not provide an origin decomposition; no split is fabricated."
        )

# The source decks supply teaching explanations, not replacement result bundles.
_TEACHING_UPDATES = {
    "suppliers": (
        "Trace the DACCS electricity roots, then open Explore supply mixes if useful.",
        "The first tab adapts the IAM workshop's transformation coverage and result tracer. "
        "Its middle card now shows the unchanged premise project mark and the official ecoinvent wordmark "
        "beside database icons: ecoinvent 3.12 cut-off supplies the linked background unit processes; "
        "premise maps IAM signals, changes selected processes/markets and relinks suppliers. This is "
        "a teaching diagram of the existing workflow, not a build performed during the lecture. "
        "Follow the regional scenario signal, premise mapping/relinking, foreground input and "
        "observed LCIA contribution. The two bars sum the complete direct ENC medium-voltage "
        "electricity supplier roots in the checked Seoul extracts, including pipeline-extension "
        "electricity. They are not the entire DACCS score or an elementary-flow carbon split. "
        "The 2025 NPi and 2050 PkBudg1000 points differ in year and pathway and their background "
        "package vintages; do not attribute the difference to climate policy alone. Isolating "
        "policy requires matched-year, matched-model comparisons. Each root score combines "
        "the demanded input amount with its complete supplier intensity; it is not a per-kWh "
        "electricity intensity. Changes can reflect demand as well as supply. Foreground parameters still "
        "need study-specific evidence. The second tab preserves SETAC's interactive market "
        "extracts. PDF uses the first tab; mix exploration remains available live.",
    ),
    "clocks": (
        "Read the relative timeline, then follow the carbon beyond the operating-input strips.",
        "The integrated equipment lane adapts the cement component-calendar principle without importing "
        "CCUS-only electrolyzer, hydrogen or methanol equipment into these CCS cases. It "
        "distinguishes recurring DAC sorbent inputs, plant and machinery timing, and longer "
        "carbon uptake tails. Build-up before Start and dismantling after operation are now "
        "explicit equipment stages. Their widths are schematic and do not add quantified "
        "construction or end-of-life inventories where source data are absent. The relative timeline remains at the bottom with an "
        "explicit scale break after year thirty, leaving more space for the operating period. "
        "ERW has been recalculated as a twenty-year supply chain, 2030–2049. Twenty equal annual "
        "batches sum to the same 1.25 t rock and 1 t eventual gross reference uptake potential; "
        "normalization does not multiply the functional unit by twenty. The new campaign workbook "
        "distributes processing inputs over years 0–19 and convolves each batch's dissolution, "
        "nickel upper-bound release and atmospheric uptake profile. Each operating year's full "
        "residual supply chain is solved in its annual interpolated background. Responsible-root "
        "LCIA series close against twenty independent annual static calculations within 0.001 kg "
        "CO2-eq; FaIR was rerun using unchanged background/configuration input files. The two "
        "connected amber arrows depict mineral dissolution/alkalinity transport and subsequent "
        "air–sea uptake from overlapping batches; their drawn extent is qualitative and not a "
        "site-calibrated completion time. The earlier single-batch results are retained only as "
        "source provenance. The displayed dated inventories, uptake sensitivity and climate curves "
        "now consume data/erw_campaign.json. "
        "Source LCA describes quarrying, comminution and coastal spreading (Foteinis et al., "
        "2023, doi:10.1021/acs.est.2c08633). "
        "BECCS regrowth starts after each harvest, overlapping operation rather than waiting "
        "until the last harvest. Separate capture-plant construction remains unquantified "
        "where it is unquantified in the reviewed cement inventory; an assumed schedule is "
        "not evidence of a quantified burden. The carbon timeline remains schematic and the "
        "other source cohorts and full regrowth histories remain unchanged.",
    ),
    "trails": (
        "Follow scenario data into TRAILS, then explore actual temporal-routing graphs from level zero to four.",
        "The left pane combines REMIND-EU scenario evidence and ecoinvent 3.12 cut-off inventories. "
        "premise transforms suppliers and exports year-indexed technosphere and biosphere resources. "
        "The 3D drawing stacks two inventory dimensions over scenario years; the package need not "
        "store dense 3D arrays. The analyst additionally supplies foreground inventories and temporal "
        "distributions. TRAILS interpolates annual backgrounds, routes dated demands and solves "
        "remaining demand in each assigned year. The right pane now embeds actual model.graph "
        "exports from new TRAILS 1.1.1 temporal_routing runs, with fixed max_depth=4, no adaptive "
        "cutoff and one normalized service at level zero. These are not hand-drawn schematics. "
        "The functional unit is at the bottom in both views and upstream levels expand upward. The viewer initially downloads only the level-zero-to-three projection. Level four is fetched once, on demand, when the presenter selects it; this changes only display/loading and retains the same full routing export. Uniform edges use width 1.25 for visibility. The routed foreground itself now has an integrated stored-CO2 functional-unit activity for DACCS, BECCS and cement. BECCS's capture module is consolidated into that root, so annual displaced heat and electricity are upstream of the capture-and-storage activity. DACCS's two service wrappers and cement's CCS/reference cohort wrappers are consolidated. Supplier-demand streams, direct biosphere profiles and reference production factors are checked before and after consolidation. Cement's 120 instantaneous emission carriers are folded into their owning activities; separate historical biomass-carbon profiles remain distinct and carry fuel-specific names. A carbon-history service node is anchored at fuel use; its biosphere kernel retains uptake before that year. Readable process names replace internal namespace/pathway identifiers in the audience view while original identities remain in the checked graph data. All branch selectors now list direct first-level inputs, with annual cement stages grouped for selection and CCS versus reference kept distinct. Branch filtering retains selected descendants and their exact paths back to the functional unit. Dated activity bands carry readable names with collision handling; more labels appear as zoom separates them. Each calendar node and each signed edge is retained in the default dated view; hover/click "
        "shows process, product, location and year. The optional activity overview groups calendar "
        "replicas transparently and changes only the display. Depth and branch controls filter the "
        "view, not the exported graph. Pan, zoom and the full-graph link help inspect large cases. "
        "Public graph files omit all coefficient/edge amounts to avoid publishing private engineering "
        "inputs or licensed background exchanges; edges have uniform width and negative demand is "
        "dashed. The output is a technosphere demand-routing graph, not an elementary-flow graph or "
        "GWP Sankey; biosphere timing is retained in the dated inventory calculated downstream. "
        "DACCS and BECCS retain their reviewed foreground/cohort timing; BECCS needs 83 additional "
        "annual background years for future forest operations. ERW uses its twenty-year campaign "
        "and the full 2005–2100 scenario package for four-level inspection; its reviewed scores "
        "retain their fixed depth one. Cement has an explicit added foreground root that demands "
        "CCS minus equal-clinker BAU per one tonne physically stored, using the reviewed campaign "
        "storage conversion. Its original September background archive is unavailable locally, "
        "so this new fixed-depth routing view uses October's REMIND-EU archive with the unchanged "
        "reviewed foreground. It is not the released adaptive score graph. No existing LCI, LCIA "
        "or FaIR output is replaced. All source hashes and graph-generation settings accompany "
        "the exports. PDF retains an actual DACCS graph snapshot and the complete left workflow.",
    ),
    "erw-sensitivity": (
        "Change one uptake assumption; then distinguish the uncertainty layers this screen does not sample.",
        "The additional tab adapts IAM limitations, the cement uncertainty appendix and the "
        "SETAC forest sensitivity. Separate scenario assumptions, foreground/reference "
        "choices, temporal profiles and climate-model parameters. FaIR configurations do not "
        "cover uncertainty in the LCI, future policy, biomass reference, forest-carbon losses "
        "or ERW site performance. The ERW controls perturb foreground uptake only and do not "
        "recompute FaIR. The existing illustrative forest correction is not imported as a "
        "calibrated parameter or propagated into climate results. Scenario alternatives are "
        "conditional experiments, not probabilities. PDF retains the ERW timing sensitivity.",
    ),
    "lenses": (
        "Choose an inventory model, then a climate question. Ask whether a stable ranking still hides a delay.",
        "This adapts the cement webinar's distinction between inventory approaches and climate "
        "assessment and the long lecture's method-choice guidance. Current, prospective and "
        "time-explicit inventories are one set of choices; fixed GWP100 factors, climate "
        "trajectories and dated pulse equivalence answer different assessment questions. "
        "Time-explicit inventory does not require replacing GWP100 in every application. "
        "Dynamic characterization needs dated gas inventories. The cement webinar shows "
        "that timing can inform the magnitude and arrival of benefits even when the preferred "
        "option stays unchanged. Do not imply time always reverses a ranking or that the "
        "four Seoul services can be ranked against one another. Choose temporal detail based "
        "on mechanisms that could affect the interpretation or decision, with its data and "
        "validation requirements made explicit.",
    ),
    "discussion": (
        "Start with ERW timing evidence, then ask which reference or non-climate effect could change a decision.",
        "Retain the open twenty-minute discussion. Ask how the lab would date ERW uptake, "
        "then connect each case to missing data and candidate non-climate pressures: DACCS "
        "energy and water; BECCS land and biodiversity; ERW trace-metal mobility and local "
        "ecosystems; cement fuels and materials. These are discussion prompts, not calculated "
        "indicator results or claims that a specific trade-off dominates. The climate-focused "
        "case results do not constitute a complete environmental assessment.",
    ),
}
for _slide in SLIDES:
    if _slide["key"] in _TEACHING_UPDATES:
        _cue, _notes = _TEACHING_UPDATES[_slide["key"]]
        _slide["cue"] = _cue
        _slide["notes"] = _notes

ALL_SLIDES = SLIDES + BACKUPS
SLIDE_INDEX = {s["key"]: i for i, s in enumerate(ALL_SLIDES)}
CHAPTERS = [
    (label, SLIDE_INDEX[key])
    for label, key in [
        ("Opening", "cover"),
        ("Current", "current"),
        ("IAMs + future", "pathways"),
        ("Time-explicit", "clocks"),
        ("Climate", "pause-gwp"),
        ("Synthesis", "workflow"),
    ]
]
assert sum(s["seconds"] for s in SLIDES if s.get("timing_phase") != "discussion") == 4200


def _discussion(number):
    question = (
        "A project starts in 2035 and operates for twenty years. Which assumptions in today’s snapshot would you question?"
        if number == 1
        else "Two projects have the same aggregate score. One removes CO₂ today; the other removes it fifty years later. What is missing?"
    )
    prompts = (
        [
            "Electricity + heat",
            "Biomass + land",
            "Grinding + transport",
            "Kiln + capture energy",
        ]
        if number == 1
        else [
            "Capture during operation",
            "Forest regrowth",
            "Dissolution + air–sea exchange",
            "Construction + avoided emissions",
        ]
    )
    return stack(
        html.Div("THINK · SHARE · DISCUSS", className="discussion-label"),
        html.Div(question, className="discussion-question"),
        *([
            html.Div([
                html.Div([
                    html.Strong("The background economy changes, too"),
                    html.Span("Electricity + heat mixes can evolve during operation."),
                ], className="operating-background-message"),
                html.Div([
                    html.Span([html.Strong("Early operation"), html.Span("Electricity + heat suppliers")]),
                    html.B("→", **{"aria-hidden": "true"}),
                    html.Span([html.Strong("Later operation"), html.Span("Year-specific suppliers")]),
                ], className="operating-background-timeline"),
            ], className="operating-background-hint"),
        ] if number == 2 else []),
        discussion_cases(prompts),
        text(
            "30 seconds to think · two or three responses · 3 minutes total", "source"
        ),
    )


def _time_view(print_mode):
    return stack(
        html.Div("Whole-project activity per 1 t CO₂ stored",className="inventory-functional-unit"),
        attribution.temporal_panels(live=not print_mode),
        attribution.legend(cumulative=True,include_net=False,temporal=True),
    )


def _erw_explorer(print_mode):
    controls = (
        html.Div(
            "Dissolution: 100 y · Air–sea lag: 5 y · Realization: 100%",
            className="print-selection",
        )
        if print_mode
        else html.Div(
            [
                html.Label(
                    [
                        "ERW dissolution duration",
                        dcc.Dropdown(
                            id="erw-duration",
                            options=[10, 30, 100],
                            value=100,
                            clearable=False,
                            searchable=False,
                        ),
                    ]
                ),
                html.Label(
                    [
                        "Air–sea delay scale",
                        dcc.Dropdown(
                            id="erw-lag",
                            options=[
                                {"label": "None", "value": 0},
                                {"label": "1 year", "value": 1},
                                {"label": "5 years", "value": 5},
                            ],
                            value=5,
                            clearable=False,
                            searchable=False,
                        ),
                    ]
                ),
                html.Label(
                    [
                        "Uptake realization",
                        dcc.Dropdown(
                            id="erw-efficiency",
                            options=[
                                {"label": "100%", "value": 1},
                                {"label": "80%", "value": 0.8},
                                {"label": "50%", "value": 0.5},
                            ],
                            value=1,
                            clearable=False,
                            searchable=False,
                        ),
                    ]
                ),
            ],
            className="erw-controls",
        )
    )
    return stack(
        controls,
        compare.time_panels(duration=100, lag=5, end=170, live=not print_mode),
        html.Div(
            "Dissolution and air–sea delay change when uptake occurs. Realization changes how much uptake occurs.",
            className="callout timing-control-caption",
        ),
        text(
            "Timing sensitivity around the calculated ERW foreground. Fixed deployment and upstream inventory; no matched particle-size or site-performance claim.",
            "source",
        ),
    )


def _pulse(print_mode):
    return stack(
        html.Div(
            [
                html.Div(
                    [
                        html.Span("2030 · EMIT"),
                        html.Strong("+1 t CO₂"),
                        html.Small("A pulse enters the atmosphere"),
                    ],
                    className="pulse-step emit",
                ),
                html.Div(
                    [
                        html.Span("WHILE WE WAIT"),
                        html.Strong("A warming influence persists"),
                        html.Small("The atmosphere responds before removal"),
                    ],
                    className="pulse-step wait",
                ),
                html.Div(
                    [
                        html.Span("REMOVE AT THE SELECTED DATE"),
                        html.Strong("−1 t CO₂"),
                        html.Small("Later uptake changes the subsequent response"),
                    ],
                    className="pulse-step remove",
                ),
            ],
            className="pulse-sequence",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Strong("Aggregate GWP100: 0 kg CO₂-eq"),
                        html.Span("+1 t minus 1 t, regardless of the delay"),
                    ],
                    className="pulse-mass-balance",
                ),
                html.Div("Removal: 2030 · same year", className="print-selection")
                if print_mode
                else dcc.RadioItems(
                    id="pulse-delay",
                    options=[
                        {"label": "2030 · same year", "value": 0},
                        {"label": "2050 · 20 years later", "value": 20},
                        {"label": "2080 · 50 years later", "value": 50},
                    ],
                    value=0,
                    inline=True,
                    className="segmented",
                ),
            ],
            className="pulse-controls-row",
        ),
        compare.graph(
            compare.pulse_timing_figure(), None if print_mode else "pulse-timing-chart"
        ),
        text(
            "Radiative forcing changes Earth’s energy balance, not its temperature directly. Orange: warming influence; teal: cooling influence. Marginal FaIR pulse illustration relative to adding neither pulse.",
            "source",
        ),
    )


def _horizon(print_mode):
    control = (
        html.Div("Calendar window: 2030–2050", className="print-selection")
        if print_mode
        else html.Div([
            html.Div([html.Strong("Visible calendar window"),
                      html.Output("2030–2050",id="response-window-label")],className="response-window-heading"),
            dcc.RangeSlider(id="response-horizon",min=2030,max=2200,step=1,
                            value=list(compare.RESPONSE_WINDOW),allowCross=False,pushable=1,
                            marks={y:str(y) for y in (2030,2050,2100,2150,2200)},
                            updatemode="drag",tooltip={"placement":"bottom","always_visible":False}),
        ],className="response-window-control")
    )
    return stack(
        teaching.fair_handoff(),
        control,
        compare.forcing_panels(live=not print_mode),
        text(
            "Below zero: less forcing than the reference. Areas integrate the displayed curves over the selected calendar window in pW·year/m²; the inventory is unchanged.",
            "source",
        ),
    )


def _workflow():
    return workflow_map()


def _supplier_lesson(print_mode=False):
    return html.Div([
        html.Div([
            tool_link("premise", "premise documentation ↗"),
            html.A("Open scenario explorer ↗", href="/scenarios/", target="_blank",
                   rel="noopener noreferrer", className="scenario-explorer-link"),
        ], className="supplier-lesson-links"),
        teaching.lesson_switch("Scenario to inventory", [
            ("Explore supply mixes", short._premise(print_mode)),
            ("Trace an input", teaching.supplier_trace()),
        ], print_mode=print_mode),
    ], className="supplier-lesson")


def _pulse_views(print_mode, pulse_view):
    if print_mode:
        return pulse_lesson.explorer(True) if pulse_view=="cases" else pulse_lesson.method_overview(True)
    return teaching.lesson_switch("Pulse equivalence",[
        ("How the comparison works",pulse_lesson.method_overview()),
        ("Match the four case areas",pulse_lesson.explorer()),
    ])


def content(index, print_mode=False, process_case=None, pulse_view=None):
    key = ALL_SLIDES[index]["key"]
    renderers = {
        "about": presenter_introduction,
        "why-time": temporal_introduction,
        "carbon-atlas": lambda: stack(
            carbon_atlas(),
            text(
                "We follow these same services and references through current static, prospective static and time-explicit LCA.",
                "source",
            ),
        ),
        "supply-chain": lambda: process_carousel(process_case),
        "current": lambda: stack(
            html.Div(
                "GWP100 puts each greenhouse gas on a CO₂-equivalent scale using its effect over 100 years, then adds the life-cycle contributions.",
                className="metric-explainer",
            ),
            attribution.static_panels(
                years=(2025,), default_view="activities", co2_terms=True
            ),
            attribution.legend(net="diamond", co2_terms=True),
            compare.evidence_note(),
        ),
        "pause-current": lambda: _discussion(1),
        "pathways": lambda: stack(
            pathway_story(),
            text(
                "Global pathways motivate future systems; sector-specific trajectories are translated into inventory changes on the following slides.",
                "source",
            ),
        ),
        "iam": lambda: stack(
            iam_systems(),
            text(
                "Reused IAM workshop visual · conditional pathways reflect the systems and assumptions included.",
                "source",
            ),
        ),
        "scenario": lambda: scenario_layers(SLIDE_INDEX["ssp-narratives"], SLIDE_INDEX["climate-trajectories"]),
        "ssp-narratives": lambda: ssp_narratives(SLIDE_INDEX["scenario"], SLIDE_INDEX["climate-trajectories"]),
        "climate-trajectories": lambda: climate_trajectories(SLIDE_INDEX["scenario"], SLIDE_INDEX["ssp-narratives"]),
        "suppliers": lambda: _supplier_lesson(print_mode),
        "future": lambda: attribution.future_comparison(print_mode),
        "pause-future": lambda: _discussion(2),
        "clocks": lambda: stack(
            teaching.clocks(print_mode),
            text(
                "Illustrative lifecycle structure. Native cohorts: 2030 DACCS/BECCS/ERW; 2035 cement. Numerical inventories retain original dates and complete tails.",
                "source",
            ),
        ),
        "trails": lambda: teaching.routing_lesson(print_mode),
        "inventory": lambda: _time_view(print_mode),
        "pause-gwp": lambda: gwp_discussion(print_mode),
        "delay": lambda: _pulse(print_mode),
        "response": lambda: _horizon(print_mode),
        "pulse-equivalence": lambda: stack(
            _pulse_views(print_mode,pulse_view),
            text(
                [
                    html.A(
                        "TRAILS · fixed-window CO₂ pulse equivalence",
                        href="https://trails.readthedocs.io/en/latest/theory.html#fixed-window-co2-pulse-equivalence",
                        target="_blank",
                    ),
                    " · ",
                    html.A(
                        "Levasseur et al. (2010)",
                        href="https://doi.org/10.1021/es9030003",
                        target="_blank",
                    ),
                ],
                "source",
            ),
        ),
        "coast": lambda: stack(
            coastal_scene(),
            text(
                [
                    html.A(
                        "Foteinis et al. (2023)",
                        href="https://doi.org/10.1021/acs.est.2c08633",
                        target="_blank",
                    ),
                    " · ",
                    html.A(
                        "Geerts et al. (2025)",
                        href="https://doi.org/10.5194/bg-22-355-2025",
                        target="_blank",
                    ),
                    " · ",
                    html.A(
                        "Zhou et al. (2025)",
                        href="https://doi.org/10.1038/s41558-024-02179-9",
                        target="_blank",
                    ),
                ],
                "source",
            ),
        ),
        "erw-sensitivity": lambda: teaching.lesson_switch(
            "Sensitivity and uncertainty", [
                ("Test ERW uptake timing", _erw_explorer(print_mode)),
                ("What this test does not cover", teaching.uncertainty_map()),
            ], print_mode=print_mode,
        ),
        "lenses": teaching.method_choices,
        "workflow": _workflow,
        "sources": _sources,
        "thanks": thank_you,
        "erw-timing-evidence": erw_timing,
        "root-attribution": root_attribution,
        "discussion": lambda: stack(
            html.Div(
                "Which missing assumption could change the decision?",
                className="discussion-question",
            ),
            html.Div(
                "Beyond climate: would land, water, resource use or ecosystem effects change your choice?",
                className="discussion-beyond",
            ),
            discussion_cases(
                [
                    "Energy timing · water demand",
                    "Forest reference · land + biodiversity",
                    "Uptake kinetics · nickel + ecosystems",
                    "Capture timing · fuels + material demand",
                ]
            ),
            text(
                "Begin with the lab’s ERW study: service, reference, uptake evidence and assessment window.",
                "source",
            ),
        ),
        "matrix-equations": lambda: equation(
            [
                html.Div("A x = f     →     x = A⁻¹ f"),
                html.Div("s = cᵀ B A⁻¹ f"),
                html.Div("s(σ, y) = cᵀ B(σ, y) A(σ, y)⁻¹ f(y)"),
            ],
            [
                ("A, B", "Technosphere and biosphere exchanges"),
                ("f, x", "Final demand and process scaling"),
                ("c, s", "Characterization factors and impact score"),
            ],
            "A prospective snapshot changes coefficients and foreground assumptions; keep the service consistent.",
        ),
        "temporal-equations": lambda: html.Div(
            [_dated_equations(), _climate_equations()], className="backup-equation-pair"
        ),
        "provenance": lambda: stack(
            cards(
                [
                    (
                        "Reused",
                        "IAM workshop visuals; SETAC/lca-time CDR results; reviewed cement webinar.",
                    ),
                    (
                        "Calculated",
                        "ERW current/future snapshots, depth-one dated LCI and FaIR response.",
                    ),
                    (
                        "Assumed",
                        "Coastal uptake kinetics and retained proxies; source-specific references and cohorts.",
                    ),
                ]
            ),
            text(
                "Source hashes, normalization, linking checks and remaining limits are recorded with the ERW artifacts. No background inventories are distributed.",
                "source",
            ),
        ),
        "pulse-equation": lambda: stack(
            equation(
                [html.Div("MCO₂-pulse-eq = Mref × ∫ ΔRFLCA(t) dt / ∫ ΔRFpulse(t) dt")],
                [
                    ("Same limits", "Integrate both responses from t₀ to t₁"),
                    ("Reference", "CO₂ pulse mass Mref at declared year tp"),
                    ("Ensemble", "Compute a ratio per configuration, then summarize"),
                ],
                "Signed integrated forcing, conditional on climate background, pulse year and window.",
            ),
            text(
                "Negative: reduced integrated forcing relative to the reference. Equal area does not imply identical temperature paths, physical removal or permanent storage.",
                "source",
            ),
        ),
    }
    component = _rewrite(renderers[key]())
    return warming_labels(component) if index >= SLIDE_INDEX["scenario"] else component


def render_slide(index, *, print_mode=False, process_case=None, pulse_view=None):
    index = int(index)
    if not 0 <= index < len(ALL_SLIDES):
        raise IndexError(index)
    meta = ALL_SLIDES[index]
    # On comparison pages the panels already identify the four cases.
    show_ribbon = meta["key"] in {
        "pause-current",
        "pause-future",
        "delay",
        "coast",
        "workflow",
        "sources",
    }
    if index == 0:
        children = _cover()
    elif meta["key"] == "thanks":
        children = [thank_you()]
    else:
        children = [
            html.Div(
                [
                    html.Div(meta["phase"], className="slide-eyebrow"),
                    html.H1(meta["title"]),
                ],
                className="slide-heading",
            ),
            *([case_ribbon()] if show_ribbon else []),
            html.Div(content(index, print_mode, process_case,pulse_view), className="slide-body"),
        ]
    children.append(
        html.Div(
            f"{index + 1:02d} / {CORE_COUNT:02d}" if index < CORE_COUNT else "Backup",
            className="slide-number",
        )
    )
    component = html.Section(
        children,
        className=f"slide setac-slide snu-slide snu-slide-{index} story-slide"
        + (" cover-slide" if index == 0 else "")
        + (" closing-slide" if meta["key"] == "thanks" else "")
        + (" with-case-ribbon" if show_ribbon else ""),
        **{"aria-label": meta["title"], "data-slide-key": meta["key"]},
        **({"data-pulse-view":pulse_view or "method"} if meta["key"]=="pulse-equivalence" else {}),
    )
    component = clean_audience_footer(component)
    return _print_safe(component) if print_mode else component


def presenter_slides():
    """Use concise authored bullets; retain detailed scientific context in source."""
    slides = []
    elapsed = 0
    for index, meta in enumerate(ALL_SLIDES):
        notes = POINTS[meta["key"]]
        if not 4 <= len(notes) <= 5:
            raise ValueError(f"Expected four or five speaker bullets for {meta['key']}")
        timing_phase=meta.get("timing_phase","teaching")
        start = 0 if timing_phase == "discussion" else elapsed
        end = start + meta["seconds"]
        slides.append({
            **{k: meta[k] for k in ("key", "title", "seconds")},
            "notes": notes,
            "timing_phase":timing_phase,
            "start_seconds": start,
            "end_seconds": end,
        })
        if index < CORE_COUNT and timing_phase != "discussion":
            elapsed = end
    return slides
