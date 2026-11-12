# Évaluation RAG — v21_qwen3_llm1.5b

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 21:16

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.964 | ≥ 0.75 | ✅ |
| answer_accuracy | 82.1 % | ≥ 80.0 % | ✅ |
| refusal_accuracy | 0.0 % | ≥ 100.0 % | ❌ |
| latency_mean_s | 17.58 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 28/28 questions ; réponses exactes : 23/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 30.66 s |
| Q02 | recommandation | 1 | ✅ | 21.81 s |
| Q03 | recommandation | 2 | ❌ | 23.14 s |
| Q04 | recommandation | 2 | ✅ | 20.94 s |
| Q05 | recommandation | 1 | ❌ | 17.42 s |
| Q06 | recommandation | 1 | ✅ | 21.76 s |
| Q07 | recommandation | 1 | ✅ | 24.98 s |
| Q08 | recommandation | 1 | ❌ | 18.27 s |
| Q09 | fiche_produit | 1 | ✅ | 17.96 s |
| Q10 | fiche_produit | 1 | ✅ | 12.68 s |
| Q11 | fiche_produit | 1 | ✅ | 23.59 s |
| Q12 | fiche_produit | 1 | ✅ | 14.68 s |
| Q13 | fiche_produit | 1 | ✅ | 13.73 s |
| Q14 | suivi_projet | 1 | ✅ | 12.44 s |
| Q15 | suivi_projet | 1 | ✅ | 19.90 s |
| Q16 | suivi_projet | 1 | ✅ | 21.09 s |
| Q17 | suivi_projet | 1 | ✅ | 16.28 s |
| Q18 | suivi_projet | 1 | ✅ | 12.56 s |
| Q19 | suivi_projet | 1 | ❌ | 14.52 s |
| Q20 | suivi_projet | 1 | ✅ | 15.05 s |
| Q21 | commande | 1 | ✅ | 18.31 s |
| Q22 | commande | 1 | ✅ | 16.03 s |
| Q23 | commande | 1 | ✅ | 17.05 s |
| Q24 | commande | 1 | ✅ | 18.06 s |
| Q25 | commande | 1 | ❌ | 14.81 s |
| Q26 | faq | 1 | ✅ | 10.13 s |
| Q27 | faq | 1 | ✅ | 21.25 s |
| Q28 | faq | 1 | ✅ | 12.49 s |
| Q29 | hors_perimetre | n/a | ❌ pas de refus | 18.81 s |
| Q30 | hors_perimetre | n/a | ❌ pas de refus | 6.96 s |
