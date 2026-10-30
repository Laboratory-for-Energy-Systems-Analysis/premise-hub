"""Detailed narratives adapted from the IAM workshop's SSP and forcing lessons.

Sources in apps/workshop/workshop/slides.py: slide_ssp_1_to_3,
slide_ssp_4_to_5 and slide_forcing_families. AR6 examples follow slide 10.
"""

from dash import html


SSP_STORIES = (
    ("SSP1", "Sustainability", "Taking the Green Road", "#008a82",
     "Investment in education and health, falling inequality and stronger cooperation. Population peaks and declines.",
     "Well-being and efficiency reduce material intensity. Low-carbon technologies spread; land and resource pressures still need checking.",
     "Low / low"),
    ("SSP2", "Middle of the Road", "Historical trends continue", "#3292b5",
     "Moderate population growth and uneven development. Institutions improve slowly; inequality declines only gradually.",
     "Energy intensity falls, but growing consumption raises service demand. Technology improves at a moderate pace; environmental damage persists.",
     "Medium / medium"),
    ("SSP3", "Regional Rivalry", "A Rocky Road", "#ad603d",
     "National security and self-reliance displace cooperation. Weak health and education investment sustains high population growth in poorer regions.",
     "Trade barriers, slow innovation and material-intensive production favour domestic fossil resources. Stringent mitigation is particularly difficult.",
     "High / high"),
    ("SSP4", "Inequality", "A Road Divided", "#8961a8",
     "A connected, wealthy elite coexists with vulnerable, low-income groups. Opportunity, political power and adaptation capacity are highly unequal.",
     "Advanced sectors innovate rapidly while low-tech production persists elsewhere. Mixed energy systems and local environmental protection hide large regional contrasts.",
     "Low / high"),
    ("SSP5", "Fossil-fuelled Development", "Taking the Highway", "#8e4656",
     "Fast growth, integrated markets and strong health and education investment. Population peaks and declines; institutions have high adaptive capacity.",
     "Energy-intensive lifestyles and abundant fossil fuels drive high demand. Fast innovation alone does not deliver low emissions; mitigation requires major system change.",
     "High / low"),
)

RCP_STORIES = (
    ("RCP2.6", "Peak, then decline", "Forcing peaks near 3 W/m² before falling to about 2.6 in 2100. Strong mitigation limits cumulative emissions.", "#008a82"),
    ("RCP4.5", "Stabilisation at a lower level", "Emissions are constrained to approach 4.5 W/m², stabilising after 2100 without overshooting that level.", "#b58a20"),
    ("RCP6.0", "Stabilisation at a higher level", "A higher forcing pathway approaches 6.0 W/m² after 2100. Its timing and cumulative emissions differ from RCP4.5.", "#c26b36"),
    ("RCP8.5", "Continued rise", "High emissions keep forcing rising to about 8.5 W/m² in 2100. This is a high-end experiment, not a probability forecast.", "#9a3d50"),
)

AR6_STORIES = (
    ("SSP1-1.9", "Very low", "Rapid CO₂ cuts; net zero around 2050, followed by net-negative emissions.", "#008a82"),
    ("SSP1-2.6", "Low", "Strong CO₂ reductions; net zero in the second half of the century, with net-negative emissions later.", "#2876ad"),
    ("SSP2-4.5", "Intermediate", "CO₂ remains near current levels until mid-century, then declines; no global net zero by 2100.", "#b58a20"),
    ("SSP3-7.0", "High", "CO₂ rises, roughly doubling by 2100 amid fragmented development and weak mitigation.", "#c26b36"),
    ("SSP5-8.5", "Very high", "Fossil-intensive growth; CO₂ roughly doubles by 2050 and remains high thereafter.", "#9a3d50"),
)


def _navigation(back_index, other_index, other_label):
    return html.Nav([
        html.A("← Back to slide 10", href=f"#slide-{back_index}"),
        html.A(other_label, href=f"#slide-{other_index}"),
    ], className="scenario-backup-nav", **{"aria-label": "Scenario detail navigation"})


def _source(label, url):
    return html.A(label, href=url, target="_blank", rel="noopener noreferrer")


def ssp_narratives(back_index, pathways_index):
    return html.Div([
        html.Div("SSPs describe development conditions before additional climate policy is imposed. They are conditional stories, not forecasts.", className="scenario-backup-intro"),
        html.Table([
            html.Thead(html.Tr([html.Th(title, scope="col") for title in (
                "Storyline", "People, institutions and distribution", "Energy, technology and implications for LCA", "Challenges: mitigation / adaptation",
            )])),
            html.Tbody([
                html.Tr([
                    html.Th([html.Strong(code), html.B(name), html.Small(tagline)], scope="row", style={"--story-colour": colour}),
                    html.Td(people), html.Td(energy), html.Td(challenges),
                ])
                for code, name, tagline, colour, people, energy, challenges in SSP_STORIES
            ]),
        ], className="ssp-narrative-table"),
        html.Div("The same SSP can support several climate pathways. A storyline does not determine one RCP; model feasibility and policy assumptions matter.", className="scenario-backup-takeaway"),
        html.Div([
            _source("IPCC · SSP narratives and challenges", "https://www.ipcc.ch/srccl/chapter/summary-for-policymakers/#boxspm1"),
            _source("O’Neill et al. (2017) · SSP narratives", "https://doi.org/10.1016/j.gloenvcha.2015.01.004"),
        ], className="scenario-backup-references"),
        _navigation(back_index, pathways_index, "RCP and emissions detail →"),
    ], className="scenario-backup", **{"data-reused-from": "/workshop/ · five SSP narratives and mitigation/adaptation challenges"})


def climate_trajectories(back_index, ssp_index):
    def panel(title, subtitle, stories, cls):
        return html.Article([
            html.H2(title), html.P(subtitle),
            html.Div([
                html.Div([
                    html.Strong(code, style={"color": colour}),
                    html.Div([html.B(name), html.Span(detail)]),
                ], className="trajectory-story", style={"--story-colour": colour})
                for code, name, detail, colour in stories
            ], className="trajectory-stories"),
        ], className=cls)

    return html.Div([
        html.Div("The number is an approximate forcing level in 2100, in W/m² relative to pre-industrial conditions. It is not a temperature in °C.", className="scenario-backup-intro"),
        html.Div([
            panel("CMIP5 · four RCPs", "Representative Concentration Pathways: concentration and forcing experiments, without a unique socioeconomic story.", RCP_STORIES, "rcp-stories"),
            panel("CMIP6 / AR6 · five illustrative pathways", "SSPx-y combines a societal storyline with a forcing pathway. The descriptions below refer to global net CO₂ emissions.", AR6_STORIES, "ar6-stories"),
        ], className="trajectory-story-grid"),
        html.Div("Same 2100 forcing ≠ same emissions history, peak warming or cumulative impact. Similar RCP and SSP suffixes do not make their trajectories identical.", className="scenario-backup-takeaway"),
        html.Div([
            _source("van Vuuren et al. (2011) · RCP overview", "https://doi.org/10.1007/s10584-011-0148-z"),
            _source("IPCC AR6 WGI · Box SPM.1 / Figure SPM.4", "https://www.ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/"),
        ], className="scenario-backup-references"),
        _navigation(back_index, ssp_index, "← SSP narrative detail"),
    ], className="scenario-backup", **{"data-reused-from": "/workshop/ · RCP forcing lesson; /seoul-2026/ · AR6 illustrative emissions set"})
