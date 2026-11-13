# Reproduire les résultats


Tous les chiffres du README, de [`results/SYNTHESE.md`](../results/SYNTHESE.md) et de la
présentation se recalculent avec les commandes ci-dessous. Trois façons de faire, de la plus
rapide à la plus complète.

| Ce qu'on reproduit | Modèles nécessaires | Durée | Où |
|---|---|---|---|
| Dataset, tests, baseline sans IA, comparaison V1 / V2 sans IA | aucun | ~1 min | n'importe quel PC (A) |
| Évaluation du modèle publié (30 + 10 cas), comparaison V1 / V2 avec modèles | Ollama + `qwen3-embedding:4b`, `qwen2.5:3b` (et `qwen2.5:1.5b` pour la V1) | ~15 min sur GPU, ~1 h sur CPU | Colab (B) ou GitHub Actions (C) |
| API et démo complète | Ollama + `qwen3-embedding:4b`, `qwen2.5:3b` | ~10 min | Colab (B) |

## Versions de référence

- Code : branche `main`. La V1 du mardi 10 novembre correspond au commit
  [`61b9bf7`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/tree/61b9bf7) ;
  son corpus est aussi copié dans [`data/v1/givaudan_data_v1.txt`](../data/v1/givaudan_data_v1.txt).
- Python 3.12 (GitHub Actions) ou 3.13 (Colab) ; dépendances dans `requirements.txt`.
- Modèles Ollama : `qwen3-embedding:4b` (embeddings), `qwen2.5:3b` (LLM publié),
  `qwen2.5:1.5b` (LLM de la V1 et configuration comparée). Température 0,2, 300 tokens
  maximum par réponse (`config.py`).
- Dataset entièrement déterministe : `python generate_dataset.py` régénère exactement les
  fichiers versionnés (vérifié à chaque push par le workflow « Tests »).

## A. Sans modèle d'IA (tout PC, ~1 min)

```bash
git clone https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10.git
cd equipe10
pip install -r requirements.txt

python generate_dataset.py        # dataset + contrôles de cohérence
git diff --exit-code -- data givaudan_data.txt   # doit être vide : dataset identique

python -m pytest -q               # tests automatiques (sans Ollama)

python baseline_tfidf.py                                    # baseline sans IA, 30 cas
python baseline_tfidf.py --rerank --label baseline_tfidf_rerank
python baseline_tfidf.py --rerank --cases data/eval/unseen_cases.json --label baseline_tfidf_rerank_inedits

python compare_v1_v2.py           # comparaison V1 / V2 sans IA
python report.py                  # synthèse -> results/SYNTHESE.md
```

Résultats attendus (identiques à chaque exécution, seule la latence varie) :

| Rapport | Valeurs |
|---|---|
| `results/eval_baseline_tfidf.md` | bon document 26/28, MRR 0,690 |
| `results/eval_baseline_tfidf_rerank.md` | bon document 27/28, MRR 0,869 |
| `results/comparaison_v1_v2.md` | V1 : 25 documents, 0 % typés ; V2 : 123 documents, 100 % typés ; cas couverts 3,6 % → 100 % |

## B. Sur Colab, avec GPU (modèles réels et API)

1. Ouvrir [`notebooks/RAG_Givaudan_Equipe10.ipynb`](../notebooks/RAG_Givaudan_Equipe10.ipynb) avec le badge « Open in Colab ».
2. *Exécution → Modifier le type d'exécution → GPU T4*. Vérifier avec `!nvidia-smi`.
3. Secrets Colab (icône 🔑) : `NGROK_AUTHTOKEN` (et `NGROK_DOMAIN` pour un lien fixe),
   « Accès au notebook » activé.
4. *Exécution → Tout exécuter*. La section 3 reproduit l'évaluation sur GPU
   (`results/eval_v22_qwen3_llm3b_gpu*.md`) ; la dernière cellule de la section 3 télécharge
   les rapports.

Hors Colab, sur une machine avec Ollama :

```bash
ollama pull qwen3-embedding:4b && ollama pull qwen2.5:3b
export EMBED_MODEL=qwen3-embedding:4b LLM_MODEL=qwen2.5:3b
python clean.py && python ingest.py
python evaluate.py --label v22_qwen3_llm3b
python evaluate.py --label v22_qwen3_llm3b_inedits --cases data/eval/unseen_cases.json

ollama pull qwen2.5:1.5b
python compare_v1_v2.py --models  # V1 avec son prompt et son LLM d'origine
python report.py
```

## C. Sur GitHub Actions (sans rien installer)

Onglet **Actions** du dépôt :

- **« Évaluation des modèles » → Run workflow** : évalue `qwen2.5:1.5b` et `qwen2.5:3b`
  avec `qwen3-embedding:4b` sur les 30 + 10 cas, sur processeur, et ajoute les rapports
  dans `results/` par un commit du bot.
- **« Comparaison V1 / V2 (modèles réels) » → Run workflow** : produit
  `results/comparaison_v1_v2_modeles.md`.
- **« Tests »** : se lance seul à chaque push et vérifie que le dataset régénéré est
  identique au dataset versionné.

## Écarts attendus d'une exécution à l'autre

- **Recherche** (bon document, MRR) : identique, les embeddings sont déterministes.
- **Réponses du LLM** : la température est de 0,2, une formulation peut varier d'une
  exécution à l'autre. Un cas peut basculer (1 cas sur 28 ≈ 3,6 points). Les réponses
  directes depuis les données (commandes, références, formules) ne varient pas.
- **Latence** : dépend du matériel. Mesures publiées sur CPU GitHub Actions (≈ 22 s) ; sur
  GPU T4 elle doit passer sous le seuil de 10 s.

## Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `pip's dependency resolver… python-dateutil 4.0.0 is incompatible` | paquets préinstallés de Colab | sans effet, continuer |
| `Unable to detect NVIDIA/AMD GPU` à l'installation d'Ollama | `lspci` absent sur Colab | sans effet si `!nvidia-smi` affiche une Tesla T4 |
| `503 La base vectorielle est vide` | indexation non faite | `python clean.py && python ingest.py` |
| `502 Erreur lors de l'appel à Ollama` | Ollama arrêté ou modèle absent | `ollama serve`, `ollama pull …` |
| `ERR_NGROK_3200` | session Colab ou tunnel arrêté | relancer les sections 1, 2, 4 et 5 du notebook |
| `ERR_NGROK_8012` | API arrêtée derrière le tunnel | relancer la cellule de lancement de l'API |
| `Authtoken already set` | ancienne cellule ngrok | utiliser la cellule actuelle du notebook (token passé à la configuration) |
| `SecretNotFoundError: NGROK_AUTHTOKEN` | secret Colab absent | l'ajouter (🔑) et activer « Accès au notebook » |
