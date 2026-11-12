# Évaluation RAG — v21_qwen3_llm1.5b_inedits

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 21:18

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.944 | ≥ 0.75 | ✅ |
| answer_accuracy | 77.8 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 17.02 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 9/9 questions ; réponses exactes : 7/9

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | ❌ | 20.36 s |
| U02 | recommandation | 2 | ❌ | 17.35 s |
| U03 | fiche_produit | 1 | ✅ | 14.99 s |
| U04 | suivi_projet | 1 | ✅ | 22.66 s |
| U05 | suivi_projet | 1 | ✅ | 14.54 s |
| U06 | commande | 1 | ✅ | 18.25 s |
| U07 | faq | 1 | ✅ | 10.65 s |
| U08 | fiche_produit | 1 | ✅ | 13.67 s |
| U09 | suivi_projet | 1 | ✅ | 23.24 s |
| U10 | hors_perimetre | n/a | ✅ refus | 14.46 s |
