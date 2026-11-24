from __future__ import annotations

import os

from dash import dcc, html

from . import results
from .asset_timing import biomass_profiles, stock_vintages
from .consensus import DISCUSSION_QUESTION, closing
from .fair_handoff import scenario_handoff
from .figures import (
    CASES, DEFAULT_END, PATHWAYS, REFERENCE_YEAR, WINDOW_MIN, WINDOW_START,
    forcing_figure, inventory_start, pulse_figure,
    pulse_value, regrowth_end, static_figure, static_score, temporal_figure,
)

TITLE = "Élimination du CO₂ : une ACV prospective et dynamique couplée à un modèle climatique"
SESSION = "Prise en compte du carbone biogénique en ACV : quel consensus ?"
# Confirmed by the presenting author; 1085 in the initial brief is the submitter.
ABSTRACT_NUMBER = "146"
UPLOAD_NAME = f"PrésentationMCV2026_{ABSTRACT_NUMBER}_Sacchi"


def number(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", "\u202f").replace(".", ",").replace("-", "−")


def metadata(title, phase, seconds, cue, notes):
    return dict(title=title, phase=phase, seconds=seconds, cue=cue, notes=notes)


SLIDES = [
    metadata(TITLE, SESSION, 25,
        "Annoncer la question : que devient le bilan du carbone biogénique lorsqu’on conserve les dates des flux ?",
        "Romain Sacchi, PSI. Présenter l’apport à cette session : les conventions sur les quantités et les références doivent être accompagnées d’un traitement explicite du temps. La comparaison BECCS–DACCS sert de démonstration. Les résultats MCV utilisent les systèmes de fond REMIND-EU avec millésimes de construction."),
    metadata("BECCS et DACCS : même service, deux chronologies", "01 / Systèmes et référence forestière", 65,
        "Suivre les deux voies jusqu’à une tonne stockée. Puis préciser la référence : forêt mature sur pied et énergie équivalente du marché.",
        "Le dénominateur est une tonne nette de CO₂ atteignant le stockage géologique après les pertes de transport ; les émissions de la chaîne restent dans le numérateur des indicateurs. Les deux voies captent environ 1,029 t et perdent 0,029 t lors du transport sur 2 000 km. BECCS utilise 0,630 t de granulés secs, 12,85 GJ de combustible ; l’absorption forestière est 1,143 t, les émissions résiduelles 0,114 t. La cogénération fournit sa chaleur de captage et exporte 0,564 MWh d’électricité et 0,249 GJ de chaleur, avec substitution de l’énergie du marché. DACCS utilise 3,086 kg de sorbant et 1,854 MWh d’électricité de captage, dont 1,134 MWh pour la pompe à chaleur fournissant 12,243 GJ de chaleur à COP 3. Ne pas additionner cette chaleur à une seconde source d’énergie. Les deux voies demandent encore 0,139 MWh pour compression et stockage. La référence maintient une forêt mature à stock constant : l’histoire commune avant décision s’annule, l’absorption supplémentaire est attribuée à la repousse après récolte. Ce choix conditionne les résultats et ne représente pas toutes les forêts."),
    metadata("En GWP100, le bilan de BECCS est plus négatif", "02 / ACV statique · systèmes de fond de 2025", 50,
        "Lire les losanges, puis rappeler que les barres additionnent des flux sans montrer leurs dates.",
        f"Les contributions positives sont au-dessus de zéro, les absorptions et crédits en dessous. Le losange donne le total : environ {number(static_score('BECCS'))} kg CO₂-eq pour BECCS et {number(static_score('DACCS'))} pour DACCS par tonne nette stockée. Ne pas confondre le bas de la pile négative avec le total. BECCS inclut la repousse, les émissions résiduelles, les pertes et les crédits d’énergie. Les absorptions biogéniques amont de DACCS sont héritées de ses fournisseurs, et ne sont pas un captage direct additionnel de l’installation. Les systèmes de fond sont ceux de 2025, SSP2-NPi, Europe du Nord. Le résultat ne précise pas quand l’effet climatique apparaît."),
    metadata("Le bilan est lisible… mais le temps a disparu", "03 / Déplier les dimensions temporelles", 45,
        "Partir du score agrégé à gauche, puis suivre les activités, leurs flux datés et le contexte économique et environnemental. Conclure par la question sur le CO₂ non fossile avant de présenter TRAILS.",
        "Nous avons comparé deux systèmes avec une ACV simple dont les contributions et le résultat sont interprétables. Mais ce bilan agrège les dates : il ne signifie pas que les processus physiques se produisent réellement tous au même instant. Le schéma déplie les dimensions qui se superposent dans la réalité : construction, exploitation et fin de vie ont leurs dates et durées ; émissions et absorptions suivent différents profils et concernent plusieurs gaz ; les fournisseurs d’énergie, matériaux et transports évoluent ; le fond atmosphérique et la réponse climatique changent ; les milieux récepteurs et les autres enjeux environnementaux évoluent également. Les profils, proportions et transitions sont schématiques, sans échelle quantitative ni prévision de scénario ; ce ne sont pas les résultats BECCS/DACCS ou FaIR. Les deux sorties de la somme à gauche identifient les systèmes, sans indiquer un classement supplémentaire. Pour le CO₂ non fossile, additionner des masses ne résout donc pas toute la question : quel bilan, à quelle date, dans quel monde ? La question dépasse le climat. Introduire ensuite le transfert des scénarios et des dates vers TRAILS, puis les inventaires et leur interprétation climatique. Ne pas prétendre que tous les autres impacts environnementaux dynamiques ont été calculés dans cette étude."),
    metadata("Des scénarios aux chaînes d’approvisionnement datées", "04 / Construire le modèle temporel avec TRAILS", 55,
        "Suivre le transfert des données à gauche, puis lire les échanges de construction, d’exploitation et de fin de vie dans le réseau daté à droite.",
        f"Les scénarios REMIND-EU et les inventaires ecoinvent alimentent premise, qui exporte les systèmes de fond prospectifs. Les matrices A et B sont indexées par année. Les millésimes IAM datent la construction des fournisseurs. TRAILS route la demande dans le temps puis résout la demande restante dans les matrices annuelles. Le réseau replie les activités de coordination de la cohorte dans la racine de 2030. Le premier niveau montre ainsi les échanges de construction en 2027–2029, d’exploitation en 2030–2049 et de fin de vie en 2050. Pour BECCS, les traitements de 2050 concernent les matériaux du transport et du stockage. La repousse après les récoltes se prolonge jusqu’en {regrowth_end()}. Le gazole affecté à la gestion forestière est réparti uniformément sur 83 années par récolte, de l’année de coupe à 82 ans après. La dernière récolte, en 2049, explique les liens jusqu’en 2131. Cette répartition est une hypothèse d’inventaire pour l’entretien du peuplement et des chemins forestiers. « Routage d’origine » rétablit les profondeurs de calcul TRAILS."),
    metadata("Le retrait biogénique se construit avec la repousse", "05 / Installations exploitées de 2030 à 2049", 105,
        "Montrer la repousse BECCS, puis le captage DACCS durant l’exploitation. La ligne rouge est un cumul comptable en GWP100.",
        f"Construction 2027–2029, exploitation 2030–2049 et fin de vie 2050. Chaque récolte BECCS déclenche un profil de repousse sur 83 ans ; la dernière classe annuelle est {regrowth_end()}. La référence est la forêt mature à stock constant. L’absorption historique commune s’annule : on attribue ici le retrait à la repousse future. DACCS capte pendant l’exploitation. Les profils amont peuvent précéder la mise en service ou suivre la fermeture. L’énergie garde séparément les contributions élémentaires positives et négatives, avant compensation dans chaque année et racine. Les autres catégories sont agrégées par racine et signe. Les bandes négatives d’énergie ne sont pas du captage direct supplémentaire. Les deux cas utilisent les mêmes échelles ; les zéros annuels et cumulés sont alignés. Le graphique couvre 2000–2130. La ligne rouge part du cumul déjà atteint en 2000. Les valeurs « GWP100 total » incluent les années hors du graphique et donnent environ {number(results.cohort_temporal_total('BECCS', 'per_tonne'))} et {number(results.cohort_temporal_total('DACCS', 'per_tonne'))} kg CO₂-eq. BECCS garde donc le GWP100 le plus négatif. Ce cumul n’est pas une courbe de température ou de forçage. Garder la vue empilée pendant l’exposé."),
    metadata("Même GWP100, même effet climatique ?", "06 / Ce que le bilan agrégé ne décrit pas", 65,
        "Suivre les quatre schémas, en insistant sur le retrait différé : un bilan nul ne décrit pas toute l’histoire climatique.",
        "Adaptation de la diapositive 17 de Séoul, après les inventaires datés. Quatre questions en une minute environ. 1 : deux émissions alternatives de +1 t de CO₂ en 2030 ou 2080 ont chacune le même GWP100, mais leurs fenêtres mobiles de 100 ans se terminent en 2130 ou 2180 ; la cible commune est 2100. Les bandes sont des horizons de caractérisation, pas des durées de vie atmosphériques. 2 : +1 et −1 t en 2030, ou +1 t en 2030 et −1 t en 2080, donnent tous deux zéro. Le délai ombré est une durée, pas un effet climatique calculé. Relier ce point à la référence forestière et à la repousse : dater le retrait biogénique rend visible ce que le bilan agrégé masque. 3 : des impulsions de type CH₄ et CO₂, de masses différentes, peuvent avoir le même forçage intégré sur 100 ans mais une persistance différente. Les courbes sont schématiques, pas des réponses calibrées, des températures ou des résultats FaIR. 4 : des concentrations de fond changeantes influencent les réponses marginales, y compris celle du CO₂ de référence. Les trajectoires indexées ne sont pas des prévisions REMIND et ne fixent ni le sens ni l’ampleur d’un changement de GWP. Le GWP100 reste une convention de référence valide ; dater ses résultats ne suffit pas à calculer une réponse climatique sur un calendrier commun. Passer ensuite à FaIR puis au CO₂-pulse-eq, avec un fond cohérent pour le projet et la référence. Sources : GIEC AR6 §7.6 ; Levasseur et al. 2010 ; Reisinger et al. 2011."),
    metadata("Du bilan daté à la réponse climatique", "07 / Inventaire TRAILS → modèle climatique FaIR", 65,
        "Suivre les deux branches du même scénario REMIND-EU jusqu’à FaIR. Montrer ensuite que le forçage diminue plus tôt pour le DACCS.",
        "Suivre d’abord la branche du haut. Le scénario REMIND-EU SSP2-PkBudg1000 fournit à premise les évolutions des chaînes d’approvisionnement. TRAILS les utilise pour établir un inventaire du projet par gaz et par année. La branche du bas part du même scénario et fournit à FaIR les émissions de fond. FaIR calcule les concentrations et la réponse climatique du scénario, puis calcule la différence entre les simulations avec et sans les flux du projet. L’ordonnée est la variation du forçage radiatif par tonne physique nette stockée sur la vie du projet. Une valeur négative réduit le forçage par rapport au scénario. La courbe est la médiane point par point de la réponse totale, tous gaz combinés au sein de chacune des 841 configurations. Ce n’est pas une somme de médianes par gaz. Le carbone biogénique n’est pas supposé climatiquement neutre à chaque instant. Le résultat dépend de la référence forestière et de la chronologie retenues. Le GWP100 reste calculable ; son total répond à une autre question que l’évolution de la réponse sur un calendrier commun."),
    metadata("CO₂-pulse-eq : exprimer l’effet d’un calendrier", "08 / Même forçage intégré qu’une impulsion datée", 150,
        "Garder 2020 et l’impulsion de 2030 fixes. Déplacer seulement la fin de 2100 à 2300 et annoncer les deux valeurs.",
        f"L’équivalent est la masse signée d’une impulsion de CO₂ en une année de référence qui donne le même forçage intégré sur la fenêtre choisie. Le numérateur et le dénominateur partagent scénario et fenêtre. Les rapports sont calculés dans chaque configuration FaIR avant d’en prendre la médiane ; on ne divise pas les aires des courbes médianes affichées. Fenêtre 2020–2100, impulsion 2030 : environ {number(pulse_value('BECCS'))} kg CO₂-pulse-eq pour BECCS et {number(pulse_value('DACCS'))} pour DACCS par tonne nette stockée. En 2020–2300 : environ {number(pulse_value('BECCS', 2300))} et {number(pulse_value('DACCS', 2300))}. DACCS garde le score le plus négatif aux deux bornes ; il n’y a pas d’inversion à 2300. Le GWP100 de la cohorte favorise BECCS, le critère de forçage intégré favorise DACCS. Le bilan physique direct BECCS ferme pourtant à −1 000 kg de CO₂. Environ 89 % de la repousse a eu lieu avant 2100, mais son année moyenne pondérée est 2081 : elle agit moins longtemps qu’un retrait de référence en 2030. La phrase « Autrement dit » inverse le score non arrondi : tonnes nettes à retirer et stocker = −1000 divisé par le score en kg CO₂-pulse-eq par tonne nette stockée. Au réglage par défaut : {number(-1000 / pulse_value('BECCS'), 2)} t pour BECCS et {number(-1000 / pulse_value('DACCS'), 2)} t pour DACCS. En 2020–2300 : {number(-1000 / pulse_value('BECCS', 2300), 2)} et {number(-1000 / pulse_value('DACCS', 2300), 2)} t. La mise à l’échelle conserve la chronologie du projet et suppose une réponse proportionnelle ; ce ne sont ni des tonnes brutes captées ni une élimination ponctuelle supplémentaire. La référence est un retrait en 2030, pas aujourd’hui. La fenêtre, la référence et les masses suivent les réglages ; si le score est nul ou réchauffant, aucun facteur positif ne permet d’égaler le retrait de référence. Le calcul FaIR conserve le signe de l’absorption évitée. Une même aire n’implique ni même trajectoire de température, ni même masse stockée. Cet indicateur explicite des choix de fenêtre et de référence ; il n’efface pas ces choix. Réserver les autres réglages aux questions."),
    metadata("Carbone biogénique : quel consensus sur le traitement du temps ?", "09 / Contribution à la discussion de la session", 75,
        "Montrer le changement de classement dans les deux lignes du tableau. Proposer la déclaration des flux datés comme point commun, puis poser la question à la salle.",
        "Qu’est-ce que cette comparaison apporte à la recherche d’un consensus sur le carbone biogénique ? "
        "Pour un même inventaire, le GWP100 favorise le BECCS tandis que le forçage intégré sur 2020–2100 favorise le DACCS dans les cas étudiés. "
        "Ce résultat éclaire les discussions autour d’ISO 14067, du GHG Protocol et de PEF. "
        "Il faut d’abord préciser les quantités de carbone et le scénario forestier sans projet, puis indiquer les dates des absorptions et des émissions. "
        "À partir de cet inventaire daté, on peut calculer un bilan conventionnel en GWP100 et, si la question le demande, "
        "une réponse climatique avec un scénario et un horizon explicites. "
        + DISCUSSION_QUESTION
        + " Remercier les coauteurs et le projet UPTAKE, puis ouvrir la discussion."
        " Pour les questions, le compte rendu du GHG Protocol du 21 septembre 2026 (p. 4) situe les travaux conjoints sur les flux biogéniques. "
        "L’encadré PEF renvoie au texte de 2021 (§4.4.10)."),
]
CORE_COUNT = len(SLIDES)
BACKUPS = [
    metadata("Référence forestière, unité fonctionnelle et calendrier", "Annexe / Hypothèses de la comparaison", 0, "Préciser ce qui est comparé avant d’interpréter les scores.",
        "Forêt mature à stock constant dans la référence ; pas de modélisation de croissance additionnelle du peuplement de référence. Énergie utile équivalente fournie par les marchés. Les résultats ne couvrent donc pas toutes les alternatives de gestion forestière. La quantité stockée est physique, après pertes au transport, avant déduction des émissions de cycle de vie."),
    metadata("Scénarios et fournisseurs futurs", "Annexe / REMIND-EU → premise → ecoinvent", 0, "Illustrer le scénario de fond avec le mix électrique.",
        "Extraction des nouveaux fonds : parts des marchés ENC, tous les cinq ans de 2025 à 2050. Pas d’interpolation des parts affichées. MAGICC7 décrit la température du scénario global, distincte de la perturbation du projet calculée par FaIR. Les scénarios sont conditionnels, pas des prévisions."),
    metadata("Sources, données et versions des modèles", "Annexe / Traçabilité", 0, "Ouvrir les sources et le manifeste MCV si nécessaire.",
        "Recalcul MCV avec les deux fonds REMIND-EU de 2005 à 2100 et leurs millésimes IAM. premise 2.6.0, TRAILS 1.1.1 et 841 configurations FaIR. Le manifeste dans apps/mcv_2026/data conserve les empreintes des fonds et des résultats."),
    metadata("Sensibilité illustrative aux pertes de carbone forestier", "Annexe / GWP100 uniquement", 0, "Présenter cette correction comme illustrative, sans l’appliquer aux courbes FaIR.",
        "Correction positive correspondant à 10 % de l’absorption brute de repousse. Ce n’est pas un modèle forestier recalculé ni une estimation calibrée des pertes de sol, racines et résidus. Elle n’est propagée ni à FaIR ni aux équivalents d’impulsion, faute de profil temporel spécifique."),
    metadata("Photovoltaïque et hydraulique en Europe du Nord", "Annexe / iam-preprocessor · parcs électriques", 0,
        "Comparer la croissance du photovoltaïque et la durée de présence des anciens millésimes hydrauliques.",
        "Les aires montrent les capacités en service à la fin de chaque année, regroupées par année de première mise en service. Les deux exemples utilisent la région REMIND-EU ENC dans SSP2-PkBudg1000. Le stock a été reconstitué par iam-preprocessor avec FLODyM à partir des trajectoires du scénario et des hypothèses de durée de vie et de parc initial. Le trait vertical repère 2050. L’âge moyen est pondéré par la capacité encore en service. Les millésimes servent ensuite à dater les échanges de construction dans le système de fond."),
    metadata("Véhicules électriques et pompes à chaleur en France", "Annexe / iam-preprocessor · mobilité et chaleur", 0,
        "Suivre les générations de véhicules et de pompes à chaleur au fil du renouvellement des parcs.",
        "Ces exemples viennent du même scénario REMIND-EU SSP2-PkBudg1000. Le panneau de gauche compte les véhicules légers électriques à batterie en service. Le panneau de droite exprime la puissance des pompes à chaleur en service. L’âge moyen de 2050 est pondéré par le nombre de véhicules à gauche et par la puissance à droite. Les cohortes anciennes disparaissent au fur et à mesure des retraits. Les résultats combinent les trajectoires de scénario avec les hypothèses de survie des actifs."),
    metadata("Deux rythmes d’absorption après la récolte", "Annexe / Premise → TRAILS · flux de biosphère", 0,
        "Comparer le chêne et l’épicéa à partir de la même récolte. Le maximum du profil du chêne arrive 20 ans plus tard.",
        "Premise cible le flux de biosphère « Carbon dioxide, in air » des inventaires de production et inscrit les profils dans la matrice B. Les deux profils ALIGNED du registre décrivent la repousse après récolte. Le chêne est modélisé sur 123,5 ans, avec 123 intervalles annuels et un dernier demi-intervalle. Son maximum se situe à 61,5 ans, contre 41,5 ans sur les 83 ans de l’épicéa. Les ordonnées expriment une part du CO₂ absorbé dans chaque profil, dont les poids somment à 100 %. Pour comparer les quantités totales absorbées, il faut lire les valeurs de l’inventaire. Les poids sont placés aux milieux des intervalles. TRAILS arrondit les décalages fractionnaires et regroupe les poids par année."),
]
ALL_SLIDES = SLIDES + BACKUPS


def prefix():
    return os.getenv("MCV_2026_REQUESTS_PREFIX", "/")


def text(value, className=""):
    return html.P(value, className=className)


def shared_image(filename, alt, className=""):
    return html.Img(src=prefix() + "shared/" + filename, alt=alt, className=className)


def callout(value):
    return html.Div(value, className="callout")


def graph(figure, identifier=None):
    props = dict(figure=figure, config={"displayModeBar": False, "responsive": True},
        responsive=True, className="chart", style={"height": "100%", "width": "100%"})
    if identifier:
        props["id"] = identifier
    return dcc.Graph(**props)


def score_card(case, value, unit):
    return html.Div([html.Span(case, className="small-label"),
        html.Strong(number(value), className="score"), html.Span(unit, className="score-unit")],
        className=f"score-card {case.lower()}")


def pulse_cards(end, *, start=WINDOW_START, reference=REFERENCE_YEAR):
    return [score_card(case, pulse_value(case, end, start=start, reference=reference),
        "kg CO₂-pulse-eq / t nette stockée") for case in CASES]


def pulse_configuration(start, reference, end):
    return [text(f"Impulsion de référence : {reference}", "emphasis"),
        text(f"Fenêtre : {start}–{end}", "muted")]


def pulse_window_labels(start, reference, end):
    return [html.Span(f"{label} : {year}", className=f"window-{key}")
        for label, key, year in (("Début", "start", start),
            ("Impulsion CO₂", "reference", reference), ("Fin", "end", end))]


def pulse_comparison(start=WINDOW_START, reference=REFERENCE_YEAR):
    rows = [html.Tr([html.Th("Fin de fenêtre"), html.Th("BECCS"), html.Th("DACCS")])]
    for end in (2100, 2300):
        rows.append(html.Tr([html.Td(str(end))] + [html.Td(
            number(pulse_value(case, end, start=start, reference=reference)) if end > reference else "—",
            className=f"{case.lower()}-text") for case in CASES]))
    note = "\n— : la fin doit suivre l’impulsion." if reference >= 2100 else ""
    return [html.Table(rows), text(f"kg CO₂-pulse-eq / t nette stockée\nDébut : {start} · impulsion : {reference}" + note, "source")]


def pulse_takeaway(start=WINDOW_START, reference=REFERENCE_YEAR, end=DEFAULT_END):
    sentences = []
    for case in CASES:
        score = pulse_value(case, end, start=start, reference=reference)
        if score < 0:
            inverse = html.Span([
                "Autrement dit, il faut retirer et stocker ",
                html.Strong(f"{number(-1000 / score, 2)} t nettes de CO₂"),
                f" pour égaler l’effet climatique d’un retrait de 1 t CO₂ en {reference}, sur {start}–{end}.",
            ], className="pulse-inverse")
        else:
            inverse = html.Span(
                "Avec ce bilan, augmenter le stockage ne permet pas d’égaler l’effet refroidissant d’un retrait de 1 t CO₂.",
                className="pulse-inverse",
            )
        sentences.append(text([html.Strong(case, className=f"{case.lower()}-text"),
            " : ", inverse], f"pulse-interpretation {case.lower()}"))
    return sentences


def _cover():
    return [
        html.Div([html.Div("MCV2026 · Lille · 25 novembre 2026", className="cover-kicker"),
            html.H1(TITLE), text("Carbone biogénique : du bilan des flux à leur effet climatique", "cover-subtitle")], className="cover-copy"),
        shared_image("cover-iam-trajectories.svg", "Trajectoires des scénarios REMIND-EU", "cover-iam-background"),
        html.Div([html.Div([html.A("Romain Sacchi", href="mailto:romain.sacchi@psi.ch", className="presenter-link"),
            ", Tom Terlouw, Karin Treyer, Alvaro Hahn Menacho, Arthur Jakobs et Christian Bauer",
            html.Div("Laboratoire d’analyse des systèmes énergétiques · Paul Scherrer Institut (PSI), Suisse", className="cover-affiliation")], className="cover-authors"),
            html.Span("11 h 30–13 h · Amphi B", className="cover-session")], className="presenter-line"),
        html.Img(src=prefix() + "assets/mcv-logo.png", alt="Logo officiel MCV2026", className="mcv-cover-logo"),
    ]


def _question():
    from .metric_discussion import discussion
    return discussion()


def _systems():
    return html.Div([callout([html.Strong("Service commun : "), "1 t nette de CO₂ stockée après les pertes de transport"]),
        html.Figure(html.Img(src=prefix() + "system-flows.svg", alt="Flux de biomasse, énergie, captage, transport et stockage de BECCS et DACCS"), className="systems-flow-map"),
        text("Europe du Nord · flux d’exploitation sélectionnés de 2025. Les émissions de cycle de vie sont incluses dans les scores.\nRéférence BECCS : forêt mature sur pied, à stock constant + électricité et chaleur équivalentes du marché. Absorption attribuée à la repousse après récolte.", "source")], className="stack systems-stack")


def _static():
    return html.Div([html.Div([graph(static_figure())], className="chart-stack"),
        callout(f"BECCS : {number(static_score('BECCS'))} ; DACCS : {number(static_score('DACCS'))} kg CO₂-eq / t nette stockée."),
        text("2025 · SSP2-NPi · Europe du Nord · GWP100 GIEC 2021, CO₂ biogénique inclus.\nBECCS : nouvelle cogénération + CCS face à la forêt sur pied et à l’énergie équivalente du marché.", "source")], className="stack static-stack")


def _time_bridge():
    from .time_bridge import time_bridge
    return time_bridge()


def _trails(print_mode=False):
    from .routing import routing_lesson
    return routing_lesson(print_mode, prefix())


def _temporal(print_mode):
    control = html.Span("Aires empilées", className="print-setting") if print_mode else dcc.RadioItems(id="temporal-view", options=[{"label": "Aires empilées", "value": "stacked"}, {"label": "Courbes séparées", "value": "unstacked"}], value="stacked", inline=True, className="segmented")
    return html.Div([html.Div([html.Div([html.Strong(year), html.Span(label)]) for year, label in (("2027–2029", "Construction"), ("2030–2049", "Exploitation"), ("2050", "Fin de vie"), (f"→ {regrowth_end()}", "Repousse BECCS"))] + [control], className="timeline"),
        graph(temporal_figure(), None if print_mode else "temporal-chart")], className="stack temporal-stack")


def _forcing(print_mode):
    controls = html.Span("Réponse jusqu’en 2300", className="print-setting") if print_mode else dcc.RadioItems(id="forcing-horizon", options=[{"label": "Jusqu’en 2140", "value": 2140}, {"label": "Jusqu’en 2300", "value": 2300}], value=2300, inline=True, className="segmented")
    return html.Div([scenario_handoff(prefix()),
        html.Div([html.Div([html.Div(controls, className="forcing-chart-controls"),
            graph(forcing_figure(), None if print_mode else "forcing-chart")], className="chart-stack"),
            html.Div([html.H2("Avec et sans projet"), text("FaIR ajoute les flux datés du projet aux émissions de fond du même scénario."),
                text([html.Strong("DACCS : "), "réduction du forçage plus précoce."], "daccs-text"),
                text([html.Strong("BECCS : "), "bénéfice progressif avec la repousse."], "beccs-text"),
                callout("Δ forçage négatif : influence refroidissante par rapport au scénario sans projet."),
                text("SSP2-PkBudg1000 · médiane de la réponse totale · 841 configurations FaIR", "source")], className="narrative forcing-narrative")], className="split chart-first")], className="stack")


def _pulse(print_mode):
    controls = html.Div(pulse_window_labels(WINDOW_START, REFERENCE_YEAR, DEFAULT_END), className="window-labels print-setting") if print_mode else html.Div([
        html.Div(pulse_window_labels(WINDOW_START, REFERENCE_YEAR, DEFAULT_END), id="pulse-window-labels", className="window-labels"),
        dcc.RangeSlider(id="pulse-window", min=WINDOW_MIN, max=2300, step=5, value=[WINDOW_START, REFERENCE_YEAR, DEFAULT_END], allowCross=False, pushable=5, updatemode="drag", marks={year: str(year) for year in (2000, 2050, 2100, 2200, 2300)}, tooltip={"placement": "top", "always_visible": False})], className="slider-control")
    def dynamic(children, identifier, className=""):
        return html.Div(children, className=className, **({} if print_mode else {"id": identifier}))
    return html.Div([html.Div([html.H2("Masse de CO₂ donnant le même forçage intégré"),
        html.Div([html.Span("Forçage du système intégré sur la fenêtre"), html.Hr(), html.Span("Forçage par kg d’une impulsion de CO₂ sur cette fenêtre"), html.Span("Même aire ≠ même trajectoire de température.", className="pulse-metric-note")], className="equation"),
        dynamic(pulse_configuration(WINDOW_START, REFERENCE_YEAR, DEFAULT_END), "pulse-configuration"), dynamic(pulse_cards(DEFAULT_END), "pulse-values", "pulse-values"), dynamic(pulse_takeaway(), "pulse-takeaway", "pulse-takeaway")], className="pulse-concept"),
        html.Div([graph(pulse_figure(), None if print_mode else "pulse-chart"), controls, dynamic(pulse_comparison(), "pulse-comparison", "endpoint-comparison")], className="pulse-results")], className="pulse-layout")


def _funding():
    return html.Div([html.Img(src=prefix() + "assets/eu-emblem.jpg", alt="Emblème de l’Union européenne", className="funding-eu-emblem"),
        html.Div([html.Strong("Horizon Europe · UPTAKE"), text(["Financé par l’Union européenne · ", html.A("convention 101081521", href="https://cordis.europa.eu/project/id/101081521", target="_blank")])])], className="funding-acknowledgement")


def _closing():
    return closing(_funding())


def _accounting():
    return html.Div([html.Div([html.H2("Unité fonctionnelle et référence"), text("1 t de CO₂ atmosphérique atteignant le stockage géologique après les pertes au transport. Les émissions de cycle de vie restent dans les scores."), text("BECCS : nouvelle cogénération + CCS face à une forêt mature à stock constant et à une production équivalente d’énergie du marché."), text("L’histoire commune avant décision s’annule. L’absorption supplémentaire est attribuée à la repousse après récolte."), text("La référence ne représente pas toutes les options de gestion forestière ou tous les devenirs alternatifs de la biomasse.")], className="backup-card"),
        html.Div([html.H2("Calendrier et métrique"), text(f"Construction 2027–2029 ; exploitation 2030–2049 ; fin de vie 2050. Repousse de chaque récolte sur 83 ans, jusqu’en {regrowth_end()}."), text(f"Des flux amont précèdent la mise en service : l’inventaire complet débute en {inventory_start()}. Réponse FaIR stockée sur 1940–2300."), text("Défaut : fenêtre 2020–2100 et impulsion de référence 2030. Intégration et rapport dans chaque configuration FaIR, puis médiane des 841 rapports."), text("Même aire de forçage ne signifie pas même trajectoire climatique ou même quantité stockée.")], className="backup-card")], className="two-columns")


def _mixes(print_mode):
    from .scenario import scenario_slide
    return scenario_slide(print_mode)


REFERENCES = [
    ("premise · Sacchi et al. (2022)", "https://doi.org/10.1016/j.rser.2022.112311"),
    ("Indicateurs climatiques · GIEC AR6, groupe I, §7.6", "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/"),
    ("FaIR · Leach et al. (2021)", "https://doi.org/10.5194/gmd-14-3007-2021"),
    ("TRAILS · Sacchi et al. (2026), prépublication", "https://www.researchsquare.com/article/rs-10139523/v1"),
    ("Inventaire DAC · Deutz et Bardow (2021)", "https://doi.org/10.1038/s41560-020-00771-9"),
    ("Énergie du DAC · Qiu et al. (2022)", "https://doi.org/10.1038/s41467-022-31146-1"),
    ("Transport CO₂ · Terlouw et al. (2021)", "https://doi.org/10.1021/acs.est.1c03263"),
]


def _sources():
    return html.Div([html.Ul([html.Li(html.A(label, href=url, target="_blank")) for label, url in REFERENCES], className="references"),
        html.Div([html.H2("Données et modèles"), text("ecoinvent 3.12 cutoff · REMIND-EU · Europe du Nord"), text("ACV statique : SSP2-NPi et SSP2-PkBudg1000. Cohortes temporelles et FaIR : SSP2-PkBudg1000, mise en service en 2030."), text("premise 2.6.0 · TRAILS 1.1.1 · 841 configurations FaIR."), text("Fonds 2005–2100 avec millésimes IAM. Routage explicite sur quatre niveaux. Les branches sont suivies avant la compensation des demandes signées."), _funding()], className="backup-card")], className="two-columns")


def _sensitivity():
    values = results.forest_pool_sensitivity("routed")
    return html.Div([text("Pertes additionnelles de carbone des résidus, racines et sols : correction illustrative.", "emphasis"),
        html.Div([score_card("BECCS", values["baseline_beccs"], "référence · kg CO₂-eq / t nette"), score_card("BECCS", values["stress_test_beccs"], "correction de 10 % · kg CO₂-eq / t nette"), score_card("DACCS", values["comparator_daccs"], "comparaison · kg CO₂-eq / t nette")], className="three-columns"),
        callout(f"Le classement GWP100 change avec une correction de {number(values['break_even_fraction'] * 100, 1)} % de l’absorption brute modélisée."),
        text("Correction non calibrée et non propagée à FaIR ou au CO₂-pulse-eq : amplitude et profil temporel spécifiques au site non disponibles.")], className="stack")


def render_slide(index, *, print_mode=False):
    index = int(index)
    if not 0 <= index < len(ALL_SLIDES):
        raise IndexError(index)
    meta = ALL_SLIDES[index]
    renderers = [_cover, _systems, _static, _time_bridge, lambda: _trails(print_mode),
        lambda: _temporal(print_mode), _question, lambda: _forcing(print_mode), lambda: _pulse(print_mode),
        _closing, _accounting, lambda: _mixes(print_mode), _sources, _sensitivity,
        lambda: stock_vintages(graph, (
            ("photovoltaic", "Photovoltaïque", "GW"), ("hydropower", "Hydraulique", "GW"),
        )),
        lambda: stock_vintages(graph, (
            ("electric_cars", "Véhicules électriques à batterie", "millions de véhicules"),
            ("heat_pumps", "Pompes à chaleur", "GW"),
        )),
        lambda: biomass_profiles(graph)]
    label = f"{index + 1:02d} / {CORE_COUNT:02d}" if index < CORE_COUNT else f"Annexe {index - CORE_COUNT + 1} / {len(BACKUPS)}"
    children = _cover() if index == 0 else [html.Div([html.Div(meta["phase"], className="slide-eyebrow"), html.H1(meta["title"])], className="slide-heading"), html.Div(renderers[index](), className="slide-body")]
    children.append(html.Div(label, className="slide-number"))
    if print_mode and index != 0:
        children.append(html.Img(src=prefix() + "assets/mcv-logo.png", alt="Logo officiel MCV2026", className="mcv-print-logo"))
    return html.Section(children, className=f"slide mcv-slide mcv-slide-{index + 1}" + (" cover-slide" if index == 0 else ""), **{"data-slide": index, "aria-label": f"{label} : {meta['title']}"})
