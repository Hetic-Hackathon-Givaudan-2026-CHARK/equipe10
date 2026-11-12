# Évaluation RAG — v22_qwen3_llm3b

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:3b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 21:47

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.964 | ≥ 0.75 | ✅ |
| answer_accuracy | 96.4 % | ≥ 80.0 % | ✅ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 21.57 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 28/28 questions ; réponses exactes : 27/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 45.65 s |
| Q02 | recommandation | 1 | ✅ | 31.94 s |
| Q03 | recommandation | 2 | ✅ | 33.68 s |
| Q04 | recommandation | 2 | ✅ | 33.73 s |
| Q05 | recommandation | 1 | ✅ | 25.66 s |
| Q06 | recommandation | 1 | ✅ | 46.63 s |
| Q07 | recommandation | 1 | ✅ | 29.80 s |
| Q08 | recommandation | 1 | ✅ | 27.76 s |
| Q09 | fiche_produit | 1 | ✅ | 923.0 ms |
| Q10 | fiche_produit | 1 | ✅ | 18.77 s |
| Q11 | fiche_produit | 1 | ✅ | 914.0 ms |
| Q12 | fiche_produit | 1 | ✅ | 23.34 s |
| Q13 | fiche_produit | 1 | ✅ | 20.47 s |
| Q14 | suivi_projet | 1 | ✅ | 23.02 s |
| Q15 | suivi_projet | 1 | ✅ | 27.77 s |
| Q16 | suivi_projet | 1 | ✅ | 25.25 s |
| Q17 | suivi_projet | 1 | ✅ | 29.93 s |
| Q18 | suivi_projet | 1 | ✅ | 19.44 s |
| Q19 | suivi_projet | 1 | ✅ | 27.48 s |
| Q20 | suivi_projet | 1 | ✅ | 23.59 s |
| Q21 | commande | 1 | ✅ | 783.0 ms |
| Q22 | commande | 1 | ✅ | 25.74 s |
| Q23 | commande | 1 | ✅ | 886.0 ms |
| Q24 | commande | 1 | ✅ | 862.0 ms |
| Q25 | commande | 1 | ❌ | 27.35 s |
| Q26 | faq | 1 | ✅ | 16.79 s |
| Q27 | faq | 1 | ✅ | 21.47 s |
| Q28 | faq | 1 | ✅ | 18.02 s |
| Q29 | hors_perimetre | n/a | ✅ refus | 1.03 s |
| Q30 | hors_perimetre | n/a | ✅ refus | 18.40 s |
