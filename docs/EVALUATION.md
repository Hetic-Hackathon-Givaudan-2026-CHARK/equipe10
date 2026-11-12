# Protocole de validation du modèle RAG

## Ce qu'on évalue

Le « modèle » est le système RAG complet : dataset + découpage + modèle d'embeddings
(recherche) + LLM (rédaction) + prompt système. On compare plusieurs configurations
(V1, V2…) sur le **même jeu de 30 cas de référence**.

| Version | Embeddings | LLM |
|---|---|---|
| V1 (baseline) | `nomic-embed-text` | `qwen2.5:1.5b` |
| V2 (candidate) | `qwen3-embedding:4b` | `qwen2.5:1.5b` |

## Jeu de référence

`data/eval/reference_cases.json` contient 30 questions, chacune avec :

- `expected_doc_ids` : le ou les documents qui contiennent la réponse ;
- `must_include` : les informations que la réponse doit contenir (chaque groupe est une
  liste d'alternatives acceptées, ex. `["2026-11-25", "25 novembre"]`) ;
- `expect_refusal` : `true` si la question est hors périmètre et que le modèle doit
  répondre que l'information n'est pas disponible au lieu d'inventer.

| Catégorie | Nb | Exemple |
|---|---|---|
| Recommandation catalogue (assistant IA) | 8 | « Un arôme mangue naturel et vegan pour une boisson protéinée ? » |
| Fiche produit | 5 | « Prix au kilo et MOQ de FRG-108 ? » |
| Suivi de projet / échantillons / rectifications | 7 | « Où en est le projet de lessive de Lumina Laundry ? » |
| Commandes | 5 | « Statut de la commande ORD-2026-007 ? » |
| Règles de la plateforme (FAQ) | 3 | « Combien de rectifications sont incluses ? » |
| Hors périmètre (pièges) | 2 | « Donne la formule exacte de FRG-101. » |

Les cas portent sur le dataset synthétique, mais la recherche se fait dans l'index complet
(dataset + base de connaissances du chatbot, sans filtre de domaine) : le modèle doit donc
aussi éviter les documents proches mais hors sujet.

Chaque cas a été vérifié automatiquement : les documents attendus existent et contiennent
bien les informations attendues.

## Métriques et critères de validation

| Métrique | Définition | Seuil de validation |
|---|---|---|
| Hit@4 | Part des questions dont un document attendu est dans les 4 premiers résultats | ≥ 90 % |
| MRR | Moyenne de 1 / rang du premier document attendu | ≥ 0,75 |
| Exactitude des réponses | Part des réponses contenant toutes les informations attendues | ≥ 80 % |
| Refus corrects | Part des questions pièges où le modèle refuse au lieu d'inventer | 100 % |
| Latence moyenne | Temps moyen d'un appel `/ask` (recherche + génération) | ≤ 10 s |

Une version est **validée** si tous les seuils sont atteints. La V2 est retenue si elle
est validée et fait au moins aussi bien que la V1 sur Hit@4 et l'exactitude.

## Lancer l'évaluation

```bash
python generate_dataset.py

# V1
export EMBED_MODEL=nomic-embed-text
python clean.py && python ingest.py
python evaluate.py --label v1

# V2 (réindexer : les embeddings changent avec le modèle)
export EMBED_MODEL=qwen3-embedding:4b
python clean.py && python ingest.py
python evaluate.py --label v2
```

Les rapports sont écrits dans `results/eval_v1.md` et `results/eval_v2.md` (+ JSON détaillé
avec les réponses du modèle). `--retrieval-only` évalue uniquement la recherche, sans LLM.

## Limites

- L'exactitude est mesurée par présence de mots-clés : une réponse juste mais formulée
  autrement peut être comptée fausse. Relire le JSON pour les cas en échec.
- 30 cas suffisent pour comparer des versions, pas pour une garantie statistique.
