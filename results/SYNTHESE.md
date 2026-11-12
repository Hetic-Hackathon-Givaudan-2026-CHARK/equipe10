# Synthèse des évaluations

Générée par `python report.py` le 2026-11-12 20:57 à partir de 4 rapport(s). Protocole et seuils : [docs/EVALUATION.md](../docs/EVALUATION.md).

| Configuration | Cas | Embeddings | LLM | Reclassement | Bon document dans le top 4 | MRR | Réponses exactes | Refus corrects | Latence moy. | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline_tfidf` | 30 | TF-IDF lexical (sans IA, scikit-learn) | aucun | non | 26/28 (92,9 %) ✅ | 0,690 ❌ | — | — | 1.0 ms | recherche non validée |
| `baseline_tfidf_inedits` | 10 | TF-IDF lexical (sans IA, scikit-learn) | aucun | non | 9/9 (100,0 %) ✅ | 0,759 ✅ | — | — | 1.0 ms | recherche validée |
| `baseline_tfidf_rerank` | 30 | TF-IDF lexical (sans IA, scikit-learn) + reclassement | aucun | oui | 27/28 (96,4 %) ✅ | 0,869 ✅ | — | — | 1.0 ms | recherche validée |
| `baseline_tfidf_rerank_inedits` | 10 | TF-IDF lexical (sans IA, scikit-learn) + reclassement | aucun | oui | 9/9 (100,0 %) ✅ | 1,000 ✅ | — | — | 1.0 ms | recherche validée |

Seuils : top 4 ≥ 90 %, MRR ≥ 0,75, réponses exactes ≥ 80 %, refus corrects 100 %, latence ≤ 10 s. « — » : non mesuré (configuration sans LLM). Le détail par cas, avec les réponses du modèle, est dans chaque `eval_<configuration>.md` / `.json`.
