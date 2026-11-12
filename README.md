# Intelligent Ordering Platform — RAG

## Objectif

Ce projet propose un système **RAG** (*Retrieval-Augmented Generation*) pour une plateforme B2B de commande intelligente dans les domaines :

- Fragrance & Beauty ;
- Taste & Wellbeing ;
- informations partagées liées aux commandes et à la personnalisation.

Le système permet de :

- rechercher des documents métier pertinents ;
- répondre aux questions des utilisateurs ;
- retourner les sources utilisées ;
- exposer les fonctionnalités via une API FastAPI ;
- documenter l'API avec Swagger/OpenAPI ;
- évaluer la solution sur 30 cas métier ;
- comparer les résultats entre une version V1 et une version V2.

> Les données utilisées dans ce projet sont synthétiques ou anonymisées.

---

## Architecture

```text
Question utilisateur
        |
        v
API FastAPI
        |
        v
Embedding de la question
        |
        v
Recherche vectorielle ChromaDB
        |
        v
Documents pertinents
        |
        v
Construction du contexte
        |
        v
Modèle de génération
        |
        v
Réponse avec sources
```

---

## Structure du projet

```text
.
├── api.py
├── config.py
├── ingest.py
├── rag.py
├── list.py
├── clean.py
├── generate_dataset.py
├── sample_questions.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── givaudan_data.txt
├── data/
├── evaluation/
│   └── reference_cases.csv
├── results/
└── docs/
    ├── api.md
    ├── evaluation.md
    ├── links.md
    └── reproduction.md
```

---

## Données

Les données sont stockées dans :

```text
data/
```

Le projet utilise également le fichier :

```text
givaudan_data.txt
```

Les données de démonstration peuvent inclure :

- des produits ;
- des fragrances ;
- des arômes ;
- des matières premières ;
- des commandes ;
- des échantillons ;
- des informations de personnalisation ;
- des documents métier.

### Sécurité des données

Ne jamais ajouter dans le dépôt :

- des données clients réelles ;
- des formulations propriétaires ;
- des informations confidentielles ;
- des mots de passe ;
- des tokens GitHub ;
- des tokens ngrok ;
- des clés API ;
- un fichier `.env` contenant des secrets.

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10.git
cd equipe10
```

### 2. Utiliser la branche V2

```bash
git checkout feature/taste-fragrance-rag
```

Ou :

```bash
git switch feature/taste-fragrance-rag
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

Si nécessaire :

```bash
python -m pip install fastapi uvicorn chromadb ollama pandas requests
```

---

## Vérification du code

```bash
python -m py_compile api.py
python -m py_compile config.py
python -m py_compile ingest.py
python -m py_compile rag.py
```

---

## Modèles

Les modèles réellement utilisés doivent être vérifiés dans :

```text
config.py
```

Exemple de modèles pouvant être utilisés :

```text
Embedding model : nomic-embed-text ou qwen3-embedding:4b
Generation model : qwen2.5:1.5b
Vector database : ChromaDB
```

### Démarrer Ollama

```bash
ollama serve
```

Dans un autre terminal, télécharger les modèles nécessaires :

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:1.5b
```

> Adapter les commandes aux modèles déclarés dans `config.py`.

---

## Indexation des documents

Indexer les documents dans la base vectorielle :

```bash
python ingest.py
```

Selon l'implémentation du script :

```bash
python ingest.py givaudan_data.txt
```

Vérifier les chunks indexés :

```bash
python list.py
```

---

## API FastAPI

L'API est disponible dans :

```text
api.py
```

### Démarrer l'API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Ou :

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### URLs locales

| Ressource | URL |
|---|---|
| API | `http://127.0.0.1:8000` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` |
| Health check | `http://127.0.0.1:8000/health` |

---

## Endpoints

### `GET /health`

Vérifie que l'API est disponible.

```bash
curl http://127.0.0.1:8000/health
```

Exemple de réponse :

```json
{
  "status": "ok"
}
```

> La structure exacte dépend de l'implémentation de `api.py`.

---

### `POST /search`

Recherche les documents les plus pertinents dans la base vectorielle.

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Je cherche un parfum floral au jasmin.",
    "top_k": 4
  }'
```

Exemple de requête :

```json
{
  "query": "Je cherche un parfum floral au jasmin.",
  "top_k": 4
}
```

---

### `POST /ask`

Génère une réponse à partir des documents récupérés.

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Je cherche un parfum floral et élégant au jasmin.",
    "top_k": 4
  }'
```

Exemple de requête :

```json
{
  "question": "Je cherche un parfum floral et élégant au jasmin.",
  "top_k": 4
}
```

Exemple de réponse attendue :

```json
{
  "question": "Je cherche un parfum floral et élégant au jasmin.",
  "answer": "Réponse générée à partir du contexte documentaire.",
  "sources": [
    {
      "metadata": {
        "title": "Jasmin éclatant",
        "domain": "fragrance_beauty"
      }
    }
  ]
}
```

> Vérifier la structure réelle de chaque endpoint dans Swagger : `/docs`.

---

## Exposer l'API publiquement

Après avoir démarré FastAPI sur le port `8000`, l'API peut être exposée avec ngrok :

```bash
ngrok http 8000
```

L'URL publique sera semblable à :

```text
https://URL_PUBLIQUE.ngrok-free.app
```

Les liens deviennent alors :

```text
https://URL_PUBLIQUE.ngrok-free.app/docs
https://URL_PUBLIQUE.ngrok-free.app/openapi.json
https://URL_PUBLIQUE.ngrok-free.app/health
```

> L'URL publique est temporaire. Ajouter la vraie URL dans `docs/links.md` seulement après avoir lancé l'API.

---

## Évaluation

Le jeu de référence est disponible dans :

```text
evaluation/reference_cases.csv
```

Il contient **30 cas métier** répartis dans les domaines suivants :

- `fragrance_beauty`
- `taste_wellbeing`
- `shared`

### Structure du fichier

```text
case_id
domain
question
expected_keywords
```

### Méthode

Pour chaque cas :

1. envoyer la question à l'endpoint `/ask` ;
2. récupérer la réponse générée ;
3. récupérer les sources utilisées ;
4. vérifier les mots-clés attendus ;
5. mesurer la latence ;
6. relever les éventuelles erreurs ;
7. enregistrer les résultats.

Les résultats doivent être sauvegardés dans :

```text
results/evaluation_v1.csv
results/evaluation_v2.csv
results/evaluation_summary.md
```

---

## Critères d'évaluation

Les critères évalués sont :

- **Exactitude** : la réponse est-elle correcte ?
- **Pertinence** : répond-elle réellement à la question ?
- **Factualité** : est-elle soutenue par les sources récupérées ?
- **Exhaustivité** : contient-elle les informations importantes ?
- **Robustesse** : résiste-t-elle à différentes formulations ?
- **Performance** : quelle est la latence de réponse ?
- **Sécurité** : évite-t-elle les informations inventées ou sensibles ?

---

## Résultats

> **Important :** remplacer les valeurs ci-dessous uniquement par des résultats réellement mesurés.

### Résultats V1

| Métrique | Valeur |
|---|---:|
| Nombre de cas évalués | 30 |
| Nombre de documents indexés | À mesurer |
| Taux de correspondance des mots-clés | À mesurer |
| Score moyen de factualité | À mesurer |
| Score moyen de pertinence | À mesurer |
| Latence moyenne | À mesurer |
| Taux d'erreur | À mesurer |

### Résultats V2

| Métrique | Valeur |
|---|---:|
| Nombre de cas évalués | 30 |
| Nombre de documents indexés | À mesurer |
| Taux de correspondance des mots-clés | À mesurer |
| Score moyen de factualité | À mesurer |
| Score moyen de pertinence | À mesurer |
| Latence moyenne | À mesurer |
| Taux d'erreur | À mesurer |

---

## Comparaison V1 / V2

| Critère | V1 | V2 | Analyse |
|---|---|---|---|
| Modèle d'embeddings | À compléter | À compléter | À analyser |
| Modèle de génération | À compléter | À compléter | À analyser |
| Nombre de documents indexés | À mesurer | À mesurer | À analyser |
| Couverture des domaines | À compléter | À compléter | À analyser |
| Taux de mots-clés attendus | À mesurer | À mesurer | À analyser |
| Factualité moyenne | À mesurer | À mesurer | À analyser |
| Pertinence moyenne | À mesurer | À mesurer | À analyser |
| Latence moyenne | À mesurer | À mesurer | À analyser |
| Qualité des sources | À analyser | À analyser | À analyser |
| Limites principales | À analyser | À analyser | À analyser |

### Analyse qualitative attendue

La comparaison V1/V2 doit préciser :

- les modifications du dataset ;
- les changements de modèles ;
- les changements de configuration ;
- les différences de qualité de recherche ;
- les différences de qualité de réponse ;
- les différences de latence ;
- les améliorations ;
- les régressions éventuelles ;
- les limites restantes.

---

## Exemple de test métier

### Question

```text
Je cherche un parfum floral et élégant au jasmin.
```

### Sources attendues

```text
- Commander un parfum floral
- Jasmin éclatant
- Rose poudrée
- Introduction
```

### Analyse attendue

La réponse est considérée comme correcte si :

- elle répond à la demande ;
- elle s'appuie sur les documents récupérés ;
- elle mentionne les informations pertinentes ;
- elle n'invente pas d'informations absentes des sources.

---

## Limites

Les principales limites du projet sont :

- la qualité des réponses dépend directement des documents indexés ;
- une question absente de la base peut produire une réponse insuffisante ;
- les questions ambiguës peuvent nécessiter une clarification ;
- les performances dépendent des ressources disponibles ;
- la génération locale peut introduire de la latence ;
- une URL publique de type ngrok est temporaire ;
- le contrôle par mots-clés ne remplace pas une validation humaine ;
- la base vectorielle doit être réindexée après une modification des données.

---

## Documentation

- docs/api.md
- docs/evaluation.md
- docs/links.md
- docs/reproduction.md
- [Historique des versions](CHANGELOG.md)

## Repository

- [Dépôt GitHub](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10)
- [Branche V2](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/tree/feature/taste-fragrance-rag)

---

## Sources documentaires

- `2.livrables.pdf` — Page 1
- `Comment évalue-t-on un LLM _.pdf` — Page 4
- `Comment évalue-t-on un LLM _.pdf` — Page 8

L'évaluation par cas métier est adaptée à la mesure de la valeur réelle du système. Les dimensions de qualité étudiées incluent notamment l'exactitude, la pertinence, la factualité, la robustesse, la sécurité et la performance.
