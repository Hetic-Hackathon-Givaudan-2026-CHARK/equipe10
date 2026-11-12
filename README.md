# Plateforme B2B intelligente d'arômes et de fragrances — RAG (équipe 10)

[![Tests](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/actions/workflows/tests.yml/badge.svg)](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/actions/workflows/tests.yml)

Prototype de RAG pour une plateforme où les entreprises conçoivent, personnalisent, testent
et commandent des arômes alimentaires et des fragrances, en suivant leurs projets jusqu'à la
livraison. L'assistant IA répond uniquement à partir de données **100 % fictives**.

## Où trouver les livrables

| Livrable | Où le trouver |
|---|---|
| 1. Données nettoyées et préparées | [`data/raw/`](data/raw) (tables CSV) et [`generate_dataset.py`](generate_dataset.py) (génération + contrôles de cohérence) |
| 2. Pipeline de traitement fonctionnel | [`ingest.py`](ingest.py) → ChromaDB → [`rerank.py`](rerank.py) → [`api.py`](api.py) ; démo complète dans [`notebooks/`](notebooks) |
| 3. Modèle V2 publié | V2 = branche `main` (V1 de mardi : tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1)) ; embeddings **`qwen3-embedding:4b`** + LLM **`qwen2.5:3b`**, choix justifié par la section [Résultats](#résultats), [`results/SYNTHESE.md`](results/SYNTHESE.md) et [`docs/etude_benchmark_embeddings.pdf`](docs/etude_benchmark_embeddings.pdf) |
| 4. Métriques et protocole sur 30 cas | section [Résultats](#résultats) ci-dessous, protocole [`docs/EVALUATION.md`](docs/EVALUATION.md), cas [`data/eval/`](data/eval), rapports [`results/`](results), tests [`tests/`](tests) |
| 5. API renvoyant les résultats réels | [`api.py`](api.py) ; contrat pour les interfaces [`docs/API.md`](docs/API.md) et [`docs/openapi.json`](docs/openapi.json) ; Swagger (`/docs`) exposé via ngrok depuis le notebook |

**Tester en 1 clic :** ouvrir [`notebooks/RAG_Givaudan_Equipe10.ipynb`](notebooks/RAG_Givaudan_Equipe10.ipynb) dans Colab puis « Exécuter tout ».

## Résultats

Mesurés sur les **30 cas de référence** et sur **10 cas inédits** (écrits avant toute mesure,
jamais utilisés pour régler le système). Évaluation lancée par GitHub Actions avec les vrais
modèles Ollama, **sur processeur (sans GPU)** ; tableau complet : [`results/SYNTHESE.md`](results/SYNTHESE.md).

### Modèle retenu pour la V2 : `qwen3-embedding:4b` + `qwen2.5:3b` (version V2.1)

| Critère (30 cas) | Seuil | Résultat | |
|---|---|---|---|
| Bon document dans le top 4 | ≥ 90 % | **28/28 (100 %)** | ✅ |
| MRR (bon document en tête) | ≥ 0,75 | **0,964** | ✅ |
| Réponses exactes | ≥ 80 % | **27/28 (96,4 %)** | ✅ |
| Refus corrects (questions pièges) | 100 % | **2/2 (100 %)** | ✅ |
| Latence moyenne | ≤ 10 s | 32 s sur processeur | ❌ → GPU nécessaire |

Sur les **10 cas inédits** : bon document trouvé 9/9, MRR 0,944, réponses exactes 7/9 (77,8 %),
refus 1/1.

### Comment on y est arrivé

| Configuration | Bon document (top 4) | MRR | Réponses exactes | Refus corrects | Latence (CPU) |
|---|---|---|---|---|---|
| Baseline sans IA (TF-IDF) | 26/28 | 0,690 | — | — | 1 ms |
| Baseline sans IA + reclassement | 27/28 | 0,869 | — | — | 1 ms |
| V2 — `nomic-embed-text` + `qwen2.5:1.5b` | 27/28 | 0,929 | 16/28 (57 %) | 2/2 | 16 s |
| V2 — `qwen3-embedding:4b` + `qwen2.5:1.5b` | **28/28** | **0,964** | 15/28 (54 %) | 0/2 | 17 s |
| V2.1 — `qwen3-embedding:4b` + `qwen2.5:1.5b` | 28/28 | 0,964 | 23/28 (82 %) | 0/2 | 18 s |
| **V2.1 — `qwen3-embedding:4b` + `qwen2.5:3b`** | **28/28** | **0,964** | **27/28 (96 %)** | **2/2** | 32 s |

1. **Recherche** : `qwen3-embedding:4b` trouve le bon document dans 100 % des cas et bat la
   baseline sans IA (MRR 0,964 contre 0,690) ; le reclassement ([`rerank.py`](rerank.py)) aide
   tous les modèles. C'est le modèle d'embeddings retenu.
2. **Analyse des erreurs de la V2** : la recherche était bonne, la rédaction non. Sur 13 échecs,
   5 réponses justes citaient l'identifiant interne `PR-xxx` au lieu de la référence commerciale,
   6 étaient des refus à tort alors que la réponse était dans le contexte, 2 étaient de vraies
   erreurs (dont un prix inventé).
3. **V2.1** : fiches produit sans identifiant interne, prompt exigeant la référence commerciale
   et ne refusant que si rien ne répond, interdiction explicite d'inventer. Les 30 cas n'ont
   pas été modifiés.
4. **Choix du LLM** : `qwen2.5:1.5b` monte à 82 % mais **invente une formule et un prix** sur les
   questions pièges (0/2 refus), ce qui est inacceptable pour des données Givaudan ;
   `qwen2.5:3b` atteint 96 % et refuse correctement. **On retient `qwen2.5:3b`.**
5. **Latence** : 32 s par réponse sur les serveurs GitHub sans GPU. Le modèle doit tourner sur
   GPU (Colab T4 dans le notebook de démo) pour respecter le seuil de 10 s.

**Limites** : l'exactitude est mesurée par mots-clés (une réponse juste formulée autrement peut
être comptée fausse, ex. Q25) ; 30 + 10 cas permettent de comparer des versions, pas de garantir
un taux en production ; les données sont fictives.

**Tests automatiques :** `python -m pytest` — tests relancés par GitHub Actions à chaque
modification (badge en haut de page). Évaluation complète relançable depuis l'onglet Actions
(« Évaluation des modèles » → *Run workflow*).

## Historique des versions

| Version | Date | Contenu | Où la voir |
|---|---|---|---|
| **V1** | mardi 10 novembre | Premier prototype démontré : dataset de 29 documents (clients, produits, matières premières, commandes, échantillons), ingestion ChromaDB, API FastAPI (`/health`, `/search`, `/ask`, `/demo/ping`) exposée via ngrok, `qwen3-embedding:4b` + `qwen2.5:1.5b`, étude comparative des modèles d'embeddings | tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1), captures de la démo dans [`docs/captures-demo-v1/`](docs/captures-demo-v1) |
| **V2** | jeudi 12 novembre | Dataset complet (103 documents : catalogue de 30 produits, projets de création, échantillons V1/V2/V3, commandes, FAQ) + base de connaissances du chatbot (20 fiches) ; ingestion corrigée ; reclassement des résultats ; filtre par domaine ; suivi des commandes `GET /orders/{id}` ; évaluation sur 30 cas de référence + 10 inédits ; 73 tests automatiques ; API ouverte aux interfaces web (CORS) et contrat documenté | branche `main` |
| **V2.1** | jeudi 12 novembre (soir) | Corrections issues de l'analyse des erreurs de la V2 (fiches produit, prompt), choix du LLM `qwen2.5:3b` sur mesures : 96 % de réponses exactes, 100 % de refus corrects | branche `main` |

**Ce que la V2 corrige par rapport à la V1** (visible sur les captures de la démo V1) : chaque
fiche du dataset était mal découpée — toutes les sources avaient la section « Introduction »
et le type « unknown », et chaque passage mélangeait plusieurs fiches. La V2 indexe une fiche
par document, avec son type et son domaine. Détail dans [docs/EVALUATION.md](docs/EVALUATION.md).

## Données indexées

`python ingest.py` indexe deux sources dans ChromaDB :

**1. Dataset synthétique** — généré par `generate_dataset.py` (contrôles de cohérence automatiques),
103 documents dans `givaudan_data.txt` :

| Entité | Nb | Fonctionnalité de la plateforme |
|---|---|---|
| Produits catalogue | 30 | catalogue intelligent : 16 arômes `FLV-xxx`, 14 fragrances `FRG-1xx` (profil, applications, intensité, naturalité, certifications, allergènes, dosage, prix, MOQ, délai) |
| Projets de création | 12 | création personnalisée + suivi (brief, préférences, étape, avancement %, prochaine étape) |
| Échantillons | 17 | échantillons et rectifications V1/V2/V3 avec retours et notes clients |
| Commandes | 10 | gestion des commandes `ORD-2026-xxx` (statut, livraison, montant avec remise volume) |
| FAQ | 10 | règles : commande, échantillons, rectifications, délais, tarifs, naturalité… |
| Clients / matières premières | 10 / 14 | comptes B2B, origines et notes réglementaires |

Tables CSV dans `data/raw/`, documents avec métadonnées dans `data/rag/documents.jsonl`.

**2. Base de connaissances du chatbot** — `data/rag_knowledge_base_prototype.csv` (20 fiches :
parfums `FRG-00x`, arômes laitiers `ARM-00x`, personnalisation, processus de commande, gouvernance).

Chaque document porte un **domaine** (`fragrance`, `dairy_aroma` pour les arômes alimentaires,
ou `shared`) utilisé par le filtre `domain` de l'API.

## Démarrage

```bash
pip install -r requirements.txt
ollama pull qwen3-embedding:4b && ollama pull qwen2.5:3b

python generate_dataset.py
python clean.py && python ingest.py
python list.py
uvicorn api:app --reload        # Swagger : http://127.0.0.1:8000/docs
```

Sur Colab : `notebooks/RAG_Givaudan_Equipe10.ipynb` déroule tout (installation, dataset,
évaluation, API, ngrok). Le token ngrok se met dans les *Secrets* Colab (`NGROK_AUTHTOKEN`).

## API

- `GET /health` — documents indexés et modèles utilisés
- `POST /search` — documents pertinents (`doc_id`, `document_type`, `domain`, score), reclassés par `rerank.py`
- `POST /ask` — réponse rédigée à partir des documents retrouvés ; `domain` = `fragrance`, `dairy_aroma` ou `all`
- `GET /orders/{order_id}` — suivi d'une commande (`CMD-2026-xxx` du prototype ou `ORD-2026-xxx` du dataset), toujours au même format
- `GET /demo/ping` — endpoint factice pour la démo ngrok

Contrat complet pour les interfaces (champs, exemples, erreurs, appel depuis un front React via
ngrok) : [docs/API.md](docs/API.md). L'API accepte les appels depuis un navigateur (CORS ouvert par
défaut, `CORS_ORIGINS` pour restreindre). Via ngrok gratuit, ajouter l'en-tête
`ngrok-skip-browser-warning: true`.

## Évaluation du modèle

30 cas de référence et 10 cas inédits (`data/eval/`), `evaluate.py` : Hit@k, MRR,
exactitude des réponses, refus corrects, latence. `baseline_tfidf.py` mesure la même chose
sans IA, comme plancher. Deux modèles d'embeddings comparés pour la V2 :
`nomic-embed-text` et `qwen3-embedding:4b`. Protocole et seuils : [docs/EVALUATION.md](docs/EVALUATION.md).

## Critères d'acceptation minimum

- `python ingest.py` se termine sans erreur ; `python list.py` affiche les documents indexés.
- `GET /health` renvoie le nombre de documents et les modèles.
- `POST /search` renvoie des passages pertinents pour une question produit ou commande.
- `POST /ask` produit une réponse fondée sur le contexte retrouvé.
- `GET /demo/ping` est joignable en local et via ngrok.
- `python evaluate.py` produit les rapports d'évaluation dans `results/`.
- `python -m pytest` passe (73 tests).

## Organisation du dépôt

```
├── generate_dataset.py      # génère et contrôle le dataset synthétique
├── ingest.py                # indexe le dataset + la base de connaissances dans ChromaDB
├── api.py                   # API FastAPI
├── evaluate.py              # évaluation sur les 30 cas de référence
├── baseline_tfidf.py        # baseline sans IA (TF-IDF) sur les mêmes cas
├── rerank.py                # reclassement des résultats (références exactes, type de question)
├── report.py                # synthèse de toutes les évaluations -> results/SYNTHESE.md
├── export_openapi.py        # exporte le contrat d'API -> docs/openapi.json
├── rag.py, config.py        # briques communes et paramètres (surchargeables par variables d'env.)
├── list.py, clean.py        # inspecter / vider la base vectorielle
├── sample_questions.py      # questions de démo
├── givaudan_data.txt        # corpus généré, prêt à ingérer
├── data/
│   ├── raw/                 # tables CSV du dataset (clients, produits, projets, échantillons, commandes…)
│   ├── rag/documents.jsonl  # documents du dataset avec métadonnées
│   ├── eval/                # 30 cas de référence + 10 cas inédits
│   ├── rag_knowledge_base_prototype.csv   # base de connaissances du chatbot
│   ├── orders_tracking_prototype.csv      # suivi de commandes du prototype (CMD-2026-xxx)
│   └── orders_tracking_dataset.csv        # suivi des commandes du dataset, même format (ORD-2026-xxx)
├── results/                 # rapports d'évaluation (générés par evaluate.py)
├── tests/                   # tests automatiques (pytest, sans Ollama)
├── notebooks/               # notebook Colab de démonstration
└── docs/                    # contrat d'API, protocole d'évaluation, étude des modèles, captures de la démo V1
```

## Règle de sécurité

Données synthétiques uniquement. Aucune identité client réelle, formule propriétaire,
composition de matière première, identifiant ou donnée de commande interne dans GitHub,
ChromaDB ou un endpoint exposé via ngrok. Aucun token (ngrok…) en clair dans le code ou le notebook.
