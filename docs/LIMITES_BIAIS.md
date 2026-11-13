# Limites et biais

Ce que nos résultats démontrent, ce qu'ils ne démontrent pas, et ce qu'il faudrait faire
avant une mise en production. Chiffres de référence : [`results/SYNTHESE.md`](../results/SYNTHESE.md).

## En résumé

| Point | Effet sur les résultats | Gravité | Ce qu'on a fait | Ce qu'il reste à faire |
|---|---|---|---|---|
| Données 100 % synthétiques, écrites par l'équipe | résultats probablement **optimistes** | élevée | dataset cohérent et contrôlé, aucune donnée réelle | tester sur le vrai catalogue et de vrais briefs clients |
| Cas de test écrits par ceux qui ont construit le système | **sur-apprentissage** possible | élevée | 10 cas inédits écrits avant toute mesure du reclassement, jamais utilisés pour régler | faire écrire 50 à 100 questions par des utilisateurs Givaudan |
| Petit échantillon (28 + 9 questions répondables, 3 pièges) | **marge d'erreur large** | moyenne | comparaison de configurations sur le même jeu | élargir le jeu de test |
| Exactitude mesurée par mots-clés | sous-estime ou sur-estime certaines réponses | moyenne | alternatives acceptées (« 3 » / « trois » / « V3 »), relecture des échecs | double notation humaine sur un échantillon |
| Latence sur processeur (22 s) | critère ≤ 10 s non atteint | moyenne | réponses directes sans LLM pour les références (-33 %) | GPU en production, mesure sur GPU |
| LLM non déterministe (température 0,2) | un cas peut basculer d'une exécution à l'autre | faible | réponses directes déterministes pour commandes, références et formules | plusieurs exécutions et moyenne |
| Démo sur Colab + ngrok | coupures possibles, pas de sécurité | faible pour la démo, bloquante en production | procédure de relance documentée | hébergement dédié, authentification |

## 1. Biais liés aux données

- **Données synthétiques.** Le catalogue (30 produits), les projets, échantillons et
  commandes ont été générés par `generate_dataset.py`. Les fiches sont propres, complètes et
  rédigées dans un style homogène. Un vrai catalogue aura des fiches incomplètes, des
  synonymes, des abréviations internes et des doublons : la recherche y sera moins
  performante qu'ici.
- **Vocabulaire partagé entre données et questions.** La même équipe a écrit les fiches et
  les questions de test. Les questions reprennent donc souvent les mots des fiches
  (« masquer l'amertume des protéines » ↔ fiche « Masquant Protéine »), ce qui avantage
  la recherche. C'est la principale raison de considérer nos taux comme un plafond.
- **Couverture déséquilibrée.** 16 arômes contre 14 fragrances, 10 clients, 10 commandes.
  Les catégories rares (commandes annulées, projets abandonnés) n'ont qu'un ou deux exemples.
- **Langue.** Données et questions en français, une seule question en anglais dans chaque
  jeu (Q08, U08). La performance en anglais ou en allemand (clients étrangers du dataset)
  n'est pas mesurée.
- **Base de connaissances du chatbot.** Les 20 fiches de
  `data/rag_knowledge_base_prototype.csv` (références `FRG-00x`, `ARM-00x`) coexistent avec le
  catalogue (`FRG-1xx`, `FLV-2xx`) : deux nomenclatures pour des produits proches, qui se
  concurrencent dans la recherche (Q08 : deux fiches `FRG-00x` passent devant la bonne fiche
  avec la baseline sans IA). De même, un projet client qui décrit le même besoin qu'un
  produit peut passer devant ce produit (Q03 : le projet de lessive `PJ-003` avant la
  fragrance `FRG-105`). Le reclassement (`rerank.py`) corrige une partie de ces cas.

## 2. Biais liés à l'évaluation

- **Taille de l'échantillon.** 28 questions répondables : une question vaut 3,6 points.
  L'intervalle de confiance à 95 % de « 96,4 % de réponses exactes » va d'environ 82 % à
  99 % (méthode de Wilson). Nos chiffres servent à **comparer des versions** sur le même
  jeu, pas à garantir un taux en production.
- **Seulement 3 questions pièges** (Q29, Q30, U10). « 100 % de refus » signifie 3 sur 3 :
  c'est encourageant, pas une preuve que le modèle n'invente jamais.
- **Exactitude par mots-clés.** Une réponse est comptée juste si elle contient les
  informations attendues (`must_include`). Une réponse juste formulée autrement peut être
  comptée fausse (ex. Q25), et une réponse qui contient le bon mot dans une phrase fausse
  peut être comptée juste. Les échecs ont été relus à la main ; les réussites non.
- **Réglage sur le jeu de référence.** Le prompt, les fiches produit (V2.1) et le
  reclassement ont été ajustés après analyse des erreurs sur les 30 cas. Les 30 cas n'ont
  pas été modifiés, mais le système a été réglé en les regardant. C'est pourquoi on publie
  aussi les **10 cas inédits** : recherche aussi bonne (9/9), réponses moins bonnes
  (78 % contre 96 %). L'écart entre les deux est la meilleure estimation du sur-apprentissage.
- **Comparaison V1 / V2.** Les deux versions n'ont ni les mêmes données ni les mêmes
  identifiants ; la comparaison juge les documents par leur contenu (méthode dans
  [COMPARAISON_V1_V2.md](COMPARAISON_V1_V2.md)). Les 30 cas ont été écrits pour la V2 :
  la V1 est jugée sur des besoins qu'elle ne visait pas tous (projets, FAQ). L'écart
  mesure surtout la couverture fonctionnelle gagnée, pas seulement la qualité technique.
  Une réponse de refus formulée autrement (« je ne trouve pas d'informations ») n'est pas
  reconnue par le protocole : la V1 perd ainsi un refus (Q29).

## 3. Limites du modèle

- **Latence.** 22 s en moyenne par réponse sur processeur (GitHub Actions), contre un
  seuil de 10 s. Le modèle `qwen2.5:3b` doit tourner sur GPU. Le modèle plus petit
  (`qwen2.5:1.5b`, 5 s) a été écarté parce qu'il **invente** une formule et un prix sur les
  questions pièges.
- **Petit LLM local.** Le choix de modèles de 3 et 4 milliards de paramètres hébergés
  localement protège les données (rien ne sort vers un service externe) mais limite la
  qualité de rédaction et le raisonnement sur plusieurs documents.
- **Recommandation par similarité.** L'assistant propose les produits dont la fiche
  ressemble le plus au brief. Il ne raisonne pas sur la formulation, la compatibilité
  réglementaire fine ou le coût : ces décisions restent à l'expert Givaudan.
- **Le pourcentage de « match » affiché dans l'interface** vient d'un score de similarité
  de texte, pas d'une mesure sensorielle. Il ne doit pas être présenté comme une
  probabilité que le client aime le produit.
- **Les curseurs d'affinage** (gourmandise, douceur, rondeur) de l'interface ne sont pas
  calculés par l'IA : ce sont des réglages de profil. Aucune formule n'est manipulée.

## 4. Garde-fous en place

- Refus d'office des demandes de formule ou de composition, **avant** l'appel au LLM
  (`direct_answers.py`), en plus de la consigne du prompt.
- Réponses construites directement depuis les données structurées pour les commandes et
  références citées : pas d'invention possible sur un statut, une date ou un prix.
- Prompt : ne répondre qu'à partir des extraits, phrase de refus imposée si rien ne répond.
- `answer_source` dans chaque réponse de l'API (`donnees` ou `llm`) : l'interface peut
  signaler ce qui vient de l'IA.
- Validation humaine obligatoire avant envoi d'un échantillon ou d'une formule.

## 5. Données personnelles et sécurité (RGPD)

Le prototype ne traite **aucune donnée réelle**. Pour un passage en production :

- **Ce qui est déjà favorable** : modèles hébergés localement (Ollama), donc aucune
  question ni donnée envoyée à un service d'IA externe ; données pseudonymisées par
  identifiants (`CL-004`, `ORD-2026-007`) sans nom de contact.
- **Ce qui manque** : authentification et cloisonnement par client (aujourd'hui, toute
  personne qui a le lien ngrok peut interroger `/orders` et `/ask`) ; durée de conservation
  et journalisation sans donnée personnelle ; procédure d'effacement des documents d'un
  client dans la base vectorielle ; hébergement en Europe ou chez Givaudan ; registre des
  traitements et analyse d'impact avec le DPO de Givaudan.
- **Minimisation** : n'indexer que les données métier nécessaires (produits, projets,
  commandes), jamais les coordonnées des contacts ni les formules.

## 6. Ce qui permettrait de lever ces limites

1. Rejouer l'évaluation sur le **vrai catalogue** et des **briefs réels** anonymisés.
2. Faire écrire le jeu de test par des **utilisateurs** (commerciaux, chefs de projet),
   au moins 100 questions, dont 20 pièges.
3. Noter un échantillon de réponses **à la main** par deux personnes, en plus des mots-clés.
4. Mesurer la latence sur l'**infrastructure cible** (GPU).
5. Ajouter authentification, cloisonnement par client et journalisation conforme au RGPD.
