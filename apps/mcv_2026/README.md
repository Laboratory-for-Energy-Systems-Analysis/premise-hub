# MCV2026 · Carbone biogénique et temporalité

**Élimination du CO₂ : une ACV prospective et dynamique couplée à un modèle climatique**

Romain Sacchi (présentateur), Tom Terlouw, Karin Treyer, Alvaro Hahn Menacho,
Arthur Jakobs et Christian Bauer. Laboratoire d’analyse des systèmes énergétiques,
Paul Scherrer Institut (PSI), Suisse. **Abstract 146**, confirmé par le présentateur.

25 novembre 2026, session **11 h 30–13 h**, Amphi B, Lille. Intitulé du programme :
*Taking Biogenic Carbon into account in LCA: what is the consensus?*
Présidence : Philippe Osset (Solinnen – SCORE LCA) et Vincent Grosshenny (COLAS SA).
Deuxième présentation orale dans le programme fourni ; pas d’horaire individuel
supposé. Quatre exposés oraux : **12 minutes + 3 minutes de questions** selon
les consignes transmises.

## Présenter

L’application est intégrée au portail à **`/mcv-2026/`**. Le serveur utilise la
variable d’environnement `MCV_2026_PASSWORD` pour ouvrir l’accès. Pour démarrer
en mode autonome après avoir défini cette variable :

```sh
MCV_2026_REQUESTS_PREFIX=/ .venv/bin/python -m apps.mcv_2026.app
```

Ouvrir `http://127.0.0.1:8050/`. La vue orateur est `/presenter` (ou
`/mcv-2026/presenter` dans le portail). Les notes suivent les changements de
diapositive dans un autre onglet du même navigateur. Minuteur manuel de 12 minutes.
Navigation au clavier, plein écran, liens `#slide-0` à `#slide-13`. Les touches
fléchées restent disponibles pour les contrôles quand ceux-ci ont le focus.
La synchronisation utilise une clé MCV distincte de SETAC.

Le parcours principal comporte **10 diapositives**, prévu pour **11 min 40 s**
(20 s de marge ; cible de répétition, pas durée mesurée). Le bouton Annexes ouvre
quatre pages supplémentaires ; la navigation principale s’arrête à la conclusion.

| Diapositive | Contenu | Temps |
| --- | --- | --- |
| 1 | Titre, auteurs et affiliation, logo MCV2026 | 0:25 |
| 2 | BECCS–DACCS et référence forestière | 1:05 |
| 3 | Résultats statiques en GWP100 | 0:50 |
| 4 | Du bilan agrégé aux cinq dimensions temporelles | 0:45 |
| 5 | Scénarios → premise → TRAILS et graphes réels DACCS/BECCS | 0:55 |
| 6 | Inventaires datés, repousse et cumul GWP100 | 1:45 |
| 7 | Même GWP100 : fenêtres, retrait différé, persistance et atmosphère | 1:05 |
| 8 | Couplage à FaIR et forçage radiatif | 1:05 |
| 9 | CO₂-pulse-eq et choix de fenêtre | 2:30 |
| 10 | ISO/GHG Protocol, PEF et proposition de déclaration des flux datés | 1:15 |

Annexes : hypothèses de référence ; scénarios et mix ; sources et versions ;
sensibilité illustrative aux pertes forestières.

## Message pour la session

Le GWP100 a un horizon temporel. Appliqué conventionnellement puis agrégé,
il ne conserve pas les dates civiles des émissions et absorptions. Le cas
biogénique illustre les conséquences de ce décalage entre flux.
La référence forestière reste déterminante : forêt mature à stock constant,
histoire commune avant décision annulée, absorption attribuée à la repousse
après récolte. Ces hypothèses ne représentent pas tous les devenirs forestiers.

Le bilan physique stocké, la somme GWP100 et le CO₂-pulse-eq sont distingués.
La démonstration compare **le même inventaire daté de cohorte 2030**, sous
SSP2-PkBudg1000 : environ −976 / −911 kg CO₂-eq (BECCS / DACCS), et
−219 / −792 kg CO₂-pulse-eq sur 2020–2100, impulsion de référence 2030,
par tonne nette stockée. À 2300, les équivalents sont −823 / −889 :
aucune inversion de classement entre ces deux bornes.

La diapositive 9 donne aussi la lecture inverse, calculée à partir du score non
arrondi : tonnes nettes à retirer et stocker = −1000 / score par tonne nette.
Pour égaler le forçage intégré d’un retrait ponctuel de 1 t CO₂ en 2030 sur
2020–2100, il faut environ **4,57 t nettes BECCS** ou **1,26 t nettes DACCS**.
Les quantités suivent les réglages de fenêtre et de référence ; à 2300, elles
sont de 1,22 et 1,13 t. La mise à l’échelle conserve le profil du projet et suppose
une réponse proportionnelle. Les valeurs sont des tonnes nettes stockées, pas
du captage brut. Un score nul ou réchauffant n’est pas inversé en une cible de retrait.

La proposition au débat est d’expliciter référence, flux et dates, devenir du
stock, scénario de fond, indicateur et fenêtre. La conclusion relie les questions
« que comptabiliser, quand et comment interpréter ? » aux travaux conjoints ISO/GHG Protocol
sur l’empreinte produit (compte rendu du 21 septembre 2026, p. 4) et à la convention
de pondération temporelle du texte PEF de 2021 (§4.4.10). Les sources sont liées
directement sur la diapositive 10. Elle propose d’harmoniser la déclaration des
flux datés en distinguant empreinte conventionnelle et analyse climatique
complémentaire ; elle ne présente ni une nouvelle disposition de 2026 ni un
consensus déjà acquis. Le CO₂-pulse-eq déclare une fenêtre et une impulsion :
il ne supprime pas ces choix. Une aire de forçage égale n’implique pas une même
trajectoire de température.

## Résultats et réutilisation

Les données et calculs sont ceux de [`../setac_2026/`](../setac_2026/README.md),
régénérés le 14 octobre 2026 et vérifiés par ses audits. `figures.py` adapte
uniquement les libellés et la mise en page des figures d’origine ; aucune copie
des inventaires ou recalculation scientifique n’est introduite. Les scénarios,
années, métadonnées et paramètres des ensembles restent identiques. Le PDF et
les captures demandent seulement les artefacts publics présents dans le dépôt.

Les empreintes et audits restent dans `apps/setac_2026/data/`. Ils incluent la
correction du signe de l’absorption évitée dans le couplage FaIR. Les équivalents
sont calculés configuration par configuration, puis résumés par leur médiane ;
ils ne sont pas des rapports d’aires sous les courbes médianes affichées.
La sensibilité forestière de 10 % reste une illustration GWP100 distincte,
non propagée à FaIR ou aux équivalents d’impulsion.

La charte et les composants sont adaptés de SETAC et de `lca_time`. La diapositive 4
utilise un schéma SVG natif (`time_bridge.py`) : le bilan agrégé à gauche se
déplie à droite en une chaîne d’activités reliée aux profils d’émission et
d’absorption ; les fournisseurs et les milieux récepteurs évoluent sur le même
calendrier. Les profils et proportions sont illustratifs, sans
échelle quantitative ni calcul de scénario. Le logo MCV
officiel est stocké localement, inchangé ; sa source et son empreinte figurent
dans `assets/provenance.json`. Les schémas SVG existants sont traduits en français. La diapositive 7 adapte
la diapositive 17 de Séoul : quatre frises en grille 2×2, avec leurs avertissements
sur les illustrations schématiques et leurs sources méthodologiques. La diapositive 5
adapte la diapositive 15 de Séoul : transfert des données à gauche et véritable
graphe temporel TRAILS à droite, avec sélecteur DACCS/BECCS. Le lecteur reprend
les graphes publics vérifiés et leur chargement progressif (niveaux 0–3 puis 4),
sans copier les données ni modifier les calculs. Les noms des activités restent
ceux des bases sources. Le PDF utilise la capture DACCS vérifiée de Séoul.
Le financement Horizon Europe UPTAKE, convention 101081521, est conservé.

## PDF et vérification

Le bouton **Exporter le PDF** utilise les réglages par défaut, indépendamment
des sélections interactives : fenêtre 2020–2100, référence 2030 et aires empilées.
Choisir PDF, paysage, sans en-têtes ni pieds de page. Le nom de dépôt est :

`PrésentationMCV2026_146_Sacchi.pdf`

La case **Avec annexes** ajoute quatre pages et le suffixe `_avec_annexes` au
nom du fichier. Chaque diapositive occupe une page 16:9. Les notes orateur restent dans la
vue séparée. L’export ne soumet aucun fichier à Conftool.

```sh
.venv/bin/python -m pytest tests/test_mcv_2026.py tests/test_setac_2026.py tests/test_portal.py -q
.venv/bin/python apps/mcv_2026/scripts/browser_check.py --url http://127.0.0.1:8050/mcv-2026/
```

Le contrôle Chromium vérifie les 14 pages à 1440×900 et 1280×720, les images,
la synchronisation des notes, les contrôles temporels et les scénarios, puis
exporte les PDF de **10 et 14 pages** dans `build/mcv-2026/` avec captures et
rapport de débordement. Le numéro d’abstract a été confirmé par le présentateur ;
1085 dans le brief initial désigne le déposant.
