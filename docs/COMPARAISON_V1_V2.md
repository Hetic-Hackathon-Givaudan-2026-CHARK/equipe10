# Comparaison V1 / V2 avec métriques

- **V1** : prototype démontré le mardi 10 novembre, commit
  [`61b9bf7`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/tree/61b9bf7).
  29 fiches (clients, produits, matières premières, commandes, échantillons),
  `qwen3-embedding:4b` + `qwen2.5:1.5b`.
- **V2.2** : version publiée (branche `main`). 103 fiches + 20 fiches de la base de
  connaissances du chatbot, reclassement, réponses directes depuis les données,
  `qwen3-embedding:4b` + `qwen2.5:3b`.

Rapports : [`results/comparaison_v1_v2.md`](../results/comparaison_v1_v2.md) (sans IA) et
[`results/comparaison_v1_v2_modeles.md`](../results/comparaison_v1_v2_modeles.md) (modèles réels).
Script : [`compare_v1_v2.py`](../compare_v1_v2.py).

## Méthode

On pose **les mêmes questions** aux deux versions : les 30 cas de référence et les 10 cas
inédits de `data/eval/`. Chaque version répond avec **ses propres données et sa propre
ingestion**, comme l'utilisateur les a vécues :

- V1 : corpus figé de la démo du mardi ([`data/v1/givaudan_data_v1.txt`](../data/v1/givaudan_data_v1.txt),
  copie exacte du commit `61b9bf7`), découpé par la fonction d'ingestion de la V1 reproduite à
  l'identique dans le script ; prompt et LLM d'origine (`qwen2.5:1.5b`) pour les réponses.
- V2 : dataset et ingestion actuels.

Les identifiants de documents n'ont rien en commun entre les deux versions. Un document est
donc jugé « bon » sur son **contenu** : il doit contenir une fiche du bon type (produit,
projet ou échantillon, commande, FAQ selon la catégorie de la question), citant la
référence ou le nom propre de la question, et contenant toutes les informations attendues.
Sans ces conditions, un passage V1 qui mélange plusieurs fiches serait compté bon dès
qu'il contient le chiffre « 3 » quelque part.

Trois niveaux de mesure :

1. **Données et ingestion** : nombre de documents, part typée, part mélangeant plusieurs fiches.
2. **Recherche** (top 4, sans reclassement) : couverture (la réponse existe-t-elle dans un
   document ?), bon document dans le top 4, MRR. Mesurée sans IA (TF-IDF, reproductible
   partout) et avec le modèle d'embeddings `qwen3-embedding:4b`, le même pour les deux versions.
3. **Réponses** : exactitude et refus corrects de la V1 (son prompt, son LLM), comparés aux
   résultats officiels de la V2.2 (`results/eval_v22_qwen3_llm3b*.json`).

## Résultats

### Données et ingestion

| Critère | V1 | V2 |
|---|---|---|
| Documents indexés | 25 | 123 |
| Documents avec un type métier reconnu | 0 % | 100 % |
| Documents mélangeant plusieurs fiches | 100 % | 0 % |
| Titres de section distincts | 1 (« Introduction ») | 123 |

La V1 ne reconnaissait pas les titres de fiche (le titre et le texte étaient dans le même
paragraphe) : tout le corpus tombait dans une seule section « Introduction », découpée en
passages de 800 caractères qui mélangent chacun 2 à 4 fiches. C'est ce que montraient les
captures de la démo (`docs/captures-demo-v1/`).

### Recherche sans IA (TF-IDF)

| Jeu de cas | Critère | V1 | V2 |
|---|---|---|---|
| 30 cas de référence | Cas dont la réponse existe dans les données | 3,6 % (1/28) | 100 % |
| 30 cas de référence | Bon document dans le top 4 | 0 % | 96,4 % |
| 30 cas de référence | MRR | 0,000 | 0,726 |
| 10 cas inédits | Cas dont la réponse existe dans les données | 11,1 % (1/9) | 100 % |
| 10 cas inédits | Bon document dans le top 4 | 0 % | 100 % |
| 10 cas inédits | MRR | 0,000 | 0,759 |

<!-- RESULTATS_MODELES -->

## Lecture

- **L'essentiel du gain vient des données et de l'ingestion.** La V1 ne contenait la réponse
  qu'à une seule des 28 questions répondables (Q01, arôme mangue `FLV-201`) : pas de projets,
  pas de versions d'échantillons, pas de FAQ, pas de prix ni de délais dans les fiches. Et
  même cette réponse n'était pas retrouvée, noyée dans des passages qui mélangeaient plusieurs
  fiches.
- **La V2 corrige l'ingestion** (une fiche = un document, avec type, domaine et métadonnées)
  et **élargit les données** à tout le parcours de la plateforme (catalogue, projets,
  échantillons V1/V2/V3, commandes, règles).
- **Le choix des modèles et la V2.1/V2.2 apportent le reste** : voir le tableau « Comment on
  y est arrivé » du README (54 % → 96 % de réponses exactes entre la V2 et la V2.2).

## Limites de cette comparaison

- Les 30 cas ont été écrits pour la V2 : la V1 est jugée sur des besoins qu'elle ne visait
  pas tous. L'écart mesure la **couverture fonctionnelle gagnée** autant que la qualité
  technique.
- Le jugement par contenu reste un jugement par mots-clés. Il est légèrement **favorable à
  la V1** : le cas inédit U09 (projet de soda abandonné, inexistant en V1) y est compté
  « couvert » parce qu'une fiche d'échantillon contient le mot « gamme ».
- La V1 n'est pas rejouée avec le reclassement ni les réponses directes : on compare les
  versions telles qu'elles étaient, pas les briques une à une.
