# Évaluation RAG — v21_qwen3_llm3b_inedits

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:3b`
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 21:40

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.944 | ≥ 0.75 | ✅ |
| answer_accuracy | 77.8 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 31.96 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 9/9 questions ; réponses exactes : 7/9

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | ✅ | 37.46 s |
| U02 | recommandation | 2 | ❌ | 29.56 s |
| U03 | fiche_produit | 1 | ✅ | 30.28 s |
| U04 | suivi_projet | 1 | ✅ | 43.14 s |
| U05 | suivi_projet | 1 | ✅ | 28.29 s |
| U06 | commande | 1 | ✅ | 34.87 s |
| U07 | faq | 1 | ❌ | 23.41 s |
| U08 | fiche_produit | 1 | ✅ | 25.84 s |
| U09 | suivi_projet | 1 | ✅ | 39.90 s |
| U10 | hors_perimetre | n/a | ✅ refus | 26.88 s |
