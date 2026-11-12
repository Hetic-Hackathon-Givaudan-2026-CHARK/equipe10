# Évaluation RAG — v22_qwen3_llm1.5b_inedits

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 21:34

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.944 | ≥ 0.75 | ✅ |
| answer_accuracy | 88.9 % | ≥ 80.0 % | ✅ |
| refusal_accuracy | 0.0 % | ≥ 100.0 % | ❌ |
| latency_mean_s | 5.34 s | ≤ 10 s | ✅ |

Bon document dans le top 4 : 9/9 questions ; réponses exactes : 8/9

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | ✅ | 8.75 s |
| U02 | recommandation | 2 | ❌ | 6.65 s |
| U03 | fiche_produit | 1 | ✅ | 5.53 s |
| U04 | suivi_projet | 1 | ✅ | 8.03 s |
| U05 | suivi_projet | 1 | ✅ | 5.35 s |
| U06 | commande | 1 | ✅ | 467.0 ms |
| U07 | faq | 1 | ✅ | 4.47 s |
| U08 | fiche_produit | 1 | ✅ | 394.0 ms |
| U09 | suivi_projet | 1 | ✅ | 8.59 s |
| U10 | hors_perimetre | n/a | ❌ pas de refus | 5.21 s |
