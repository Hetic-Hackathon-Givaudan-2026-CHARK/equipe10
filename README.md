# Plateforme B2B intelligente d'arômes et de fragrances — RAG (équipe 10)

Prototype de RAG pour une plateforme où les entreprises conçoivent, personnalisent, testent
et commandent des arômes alimentaires et des fragrances, en suivant leurs projets jusqu'à la
livraison. L'assistant IA répond uniquement à partir de données **100 % fictives**.

## Où trouver les livrables

| Livrable | Où le trouver |
|---|---|
| 1. Données nettoyées et préparées | [`data/raw/`](data/raw) (tables CSV) et [`generate_dataset.py`](generate_dataset.py) (génération + contrôles de cohérence) |
| 2. Pipeline de traitement fonctionnel | [`ingest.py`](ingest.py) → ChromaDB → [`api.py`](api.py) ; démo complète dans [`notebooks/`](notebooks) |
| 3. Modèle V2 publié | V2 = branche `main` (V1 de mardi : tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1)) ; embeddings `qwen3-embedding:4b` + LLM `qwen2.5:1.5b`, choix justifié par [`results/`](results) et [`docs/etude_benchmark_embeddings.pdf`](docs/etude_benchmark_embeddings.pdf) |
| 4. Métriques et protocole sur 30 cas | [`docs/EVALUATION.md`](docs/EVALUATION.md), [`data/eval/reference_cases.json`](data/eval/reference_cases.json), rapports dans [`results/`](results) |
| 5. API renvoyant les résultats réels | [`api.py`](api.py), documentée par Swagger (`/docs`) et exposée via ngrok depuis le notebook |

**Tester en 1 clic :** ouvrir [`notebooks/RAG_Givaudan_Equipe10.ipynb`](notebooks/RAG_Givaudan_Equipe10.ipynb) dans Colab puis « Exécuter tout ».

## Résultats sur les 30 cas de référence

| Configuration | Hit@4 | MRR | Exactitude des réponses | Refus corrects | Latence moyenne | Rapport |
|---|---|---|---|---|---|---|
| Seuil de validation | ≥ 90 % | ≥ 0,75 | ≥ 80 % | 100 % | ≤ 10 s | |
| Baseline TF-IDF (sans IA, recherche seule) | **92,9 %** (26/28) | **0,690** | non mesuré | non mesuré | 1 ms | [rapport](results/eval_baseline_tfidf.md) |
| V2 — `nomic-embed-text` + `qwen2.5:1.5b` | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | `results/eval_v2_nomic.md` |
| V2 — `qwen3-embedding:4b` + `qwen2.5:1.5b` | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | `results/eval_v2_qwen3.md` |

**Ce que montre la baseline sans IA :** une recherche par mots-clés retrouve le bon document
dans le top 4 pour 26 questions sur 28, mais souvent pas en premier (MRR 0,690 < 0,75) : elle
confond un projet avec le produit qu'il utilise, ou une commande avec une autre du même client.
Elle échoue complètement sur la question en anglais (Q08 : « sunscreen » ≠ « crème solaire »)
et sur une question formulée sans les mots du document (Q15). Ce sont exactement les cas que
les modèles d'embeddings doivent améliorer : un modèle qui ne bat pas cette baseline n'apporte rien.

Les lignes V2 se remplissent en lançant le notebook (Ollama nécessaire), qui produit
`results.zip` à déposer dans [`results/`](results).

## Historique des versions

| Version | Date | Contenu | Où la voir |
|---|---|---|---|
| **V1** | mardi 10 novembre | Premier prototype démontré : dataset de 29 documents (clients, produits, matières premières, commandes, échantillons), ingestion ChromaDB, API FastAPI (`/health`, `/search`, `/ask`, `/demo/ping`) exposée via ngrok, `qwen3-embedding:4b` + `qwen2.5:1.5b`, étude comparative des modèles d'embeddings | tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1), captures de la démo dans [`docs/captures-demo-v1/`](docs/captures-demo-v1) |
| **V2** | jeudi 12 novembre | Dataset complet (103 documents : catalogue de 30 produits, projets de création, échantillons V1/V2/V3, commandes, FAQ) + base de connaissances du chatbot (20 fiches) ; ingestion corrigée ; filtre par domaine ; suivi des commandes `GET /orders/{id}` ; évaluation sur 30 cas de référence | branche `main` |

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
ollama pull nomic-embed-text && ollama pull qwen2.5:1.5b

python generate_dataset.py
python clean.py && python ingest.py
python list.py
uvicorn api:app --reload        # Swagger : http://127.0.0.1:8000/docs
```

Sur Colab : `notebooks/RAG_Givaudan_Equipe10.ipynb` déroule tout (installation, dataset,
évaluation, API, ngrok). Le token ngrok se met dans les *Secrets* Colab (`NGROK_AUTHTOKEN`).

## API

- `GET /health` — documents indexés et modèles utilisés
- `POST /search` — documents pertinents (`doc_id`, `document_type`, `domain`, score)
- `POST /ask` — réponse rédigée à partir des documents retrouvés ; `domain` = `fragrance`, `dairy_aroma` ou `all`
- `GET /orders/{order_id}` — suivi d'une commande (`CMD-2026-xxx` du prototype ou `ORD-2026-xxx` du dataset), toujours au même format
- `GET /demo/ping` — endpoint factice pour la démo ngrok

## Évaluation du modèle

30 cas de référence (`data/eval/reference_cases.json`) et `evaluate.py` : Hit@k, MRR,
exactitude des réponses, refus corrects, latence. Deux modèles d'embeddings comparés pour la V2 :
`nomic-embed-text` et `qwen3-embedding:4b`. Protocole et seuils : [docs/EVALUATION.md](docs/EVALUATION.md).

## Critères d'acceptation minimum

- `python ingest.py` se termine sans erreur ; `python list.py` affiche les documents indexés.
- `GET /health` renvoie le nombre de documents et les modèles.
- `POST /search` renvoie des passages pertinents pour une question produit ou commande.
- `POST /ask` produit une réponse fondée sur le contexte retrouvé.
- `GET /demo/ping` est joignable en local et via ngrok.
- `python evaluate.py` produit les rapports d'évaluation dans `results/`.

## Organisation du dépôt

```
├── generate_dataset.py      # génère et contrôle le dataset synthétique
├── ingest.py                # indexe le dataset + la base de connaissances dans ChromaDB
├── api.py                   # API FastAPI
├── evaluate.py              # évaluation sur les 30 cas de référence
├── baseline_tfidf.py        # baseline sans IA (TF-IDF) sur les mêmes 30 cas
├── rag.py, config.py        # briques communes et paramètres (surchargeables par variables d'env.)
├── list.py, clean.py        # inspecter / vider la base vectorielle
├── sample_questions.py      # questions de démo
├── givaudan_data.txt        # corpus généré, prêt à ingérer
├── data/
│   ├── raw/                 # tables CSV du dataset (clients, produits, projets, échantillons, commandes…)
│   ├── rag/documents.jsonl  # documents du dataset avec métadonnées
│   ├── eval/                # 30 cas de référence
│   ├── rag_knowledge_base_prototype.csv   # base de connaissances du chatbot
│   ├── orders_tracking_prototype.csv      # suivi de commandes du prototype (CMD-2026-xxx)
│   └── orders_tracking_dataset.csv        # suivi des commandes du dataset, même format (ORD-2026-xxx)
├── results/                 # rapports d'évaluation (générés par evaluate.py)
├── notebooks/               # notebook Colab de démonstration
└── docs/                    # protocole d'évaluation, étude des modèles, captures de la démo V1
```

## Règle de sécurité

Données synthétiques uniquement. Aucune identité client réelle, formule propriétaire,
composition de matière première, identifiant ou donnée de commande interne dans GitHub,
ChromaDB ou un endpoint exposé via ngrok. Aucun token (ngrok…) en clair dans le code ou le notebook.
