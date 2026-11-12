# Évaluation RAG — v21_qwen3_llm3b

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:3b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 21:34

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.964 | ≥ 0.75 | ✅ |
| answer_accuracy | 96.4 % | ≥ 80.0 % | ✅ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 32.14 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 28/28 questions ; réponses exactes : 27/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 57.91 s |
| Q02 | recommandation | 1 | ✅ | 36.88 s |
| Q03 | recommandation | 2 | ✅ | 39.88 s |
| Q04 | recommandation | 2 | ✅ | 40.51 s |
| Q05 | recommandation | 1 | ✅ | 30.84 s |
| Q06 | recommandation | 1 | ✅ | 43.51 s |
| Q07 | recommandation | 1 | ✅ | 37.11 s |
| Q08 | recommandation | 1 | ✅ | 35.42 s |
| Q09 | fiche_produit | 1 | ✅ | 34.94 s |
| Q10 | fiche_produit | 1 | ✅ | 25.16 s |
| Q11 | fiche_produit | 1 | ✅ | 35.14 s |
| Q12 | fiche_produit | 1 | ✅ | 29.57 s |
| Q13 | fiche_produit | 1 | ✅ | 27.95 s |
| Q14 | suivi_projet | 1 | ✅ | 23.82 s |
| Q15 | suivi_projet | 1 | ✅ | 32.83 s |
| Q16 | suivi_projet | 1 | ✅ | 32.83 s |
| Q17 | suivi_projet | 1 | ✅ | 34.84 s |
| Q18 | suivi_projet | 1 | ✅ | 23.98 s |
| Q19 | suivi_projet | 1 | ✅ | 30.62 s |
| Q20 | suivi_projet | 1 | ✅ | 29.58 s |
| Q21 | commande | 1 | ✅ | 37.42 s |
| Q22 | commande | 1 | ✅ | 31.91 s |
| Q23 | commande | 1 | ✅ | 33.94 s |
| Q24 | commande | 1 | ✅ | 34.61 s |
| Q25 | commande | 1 | ❌ | 31.56 s |
| Q26 | faq | 1 | ✅ | 19.57 s |
| Q27 | faq | 1 | ✅ | 22.94 s |
| Q28 | faq | 1 | ✅ | 23.40 s |
| Q29 | hors_perimetre | n/a | ✅ refus | 33.06 s |
| Q30 | hors_perimetre | n/a | ✅ refus | 12.33 s |
