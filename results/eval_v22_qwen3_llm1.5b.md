# Évaluation RAG — v22_qwen3_llm1.5b

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 21:33

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.964 | ≥ 0.75 | ✅ |
| answer_accuracy | 89.3 % | ≥ 80.0 % | ✅ |
| refusal_accuracy | 50.0 % | ≥ 100.0 % | ❌ |
| latency_mean_s | 5.24 s | ≤ 10 s | ✅ |

Bon document dans le top 4 : 28/28 questions ; réponses exactes : 25/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 11.94 s |
| Q02 | recommandation | 1 | ✅ | 10.60 s |
| Q03 | recommandation | 2 | ✅ | 7.94 s |
| Q04 | recommandation | 2 | ✅ | 7.83 s |
| Q05 | recommandation | 1 | ✅ | 7.04 s |
| Q06 | recommandation | 1 | ✅ | 8.28 s |
| Q07 | recommandation | 1 | ✅ | 6.33 s |
| Q08 | recommandation | 1 | ❌ | 6.53 s |
| Q09 | fiche_produit | 1 | ✅ | 471.0 ms |
| Q10 | fiche_produit | 1 | ✅ | 4.54 s |
| Q11 | fiche_produit | 1 | ✅ | 486.0 ms |
| Q12 | fiche_produit | 1 | ✅ | 5.25 s |
| Q13 | fiche_produit | 1 | ✅ | 4.73 s |
| Q14 | suivi_projet | 1 | ✅ | 6.42 s |
| Q15 | suivi_projet | 1 | ✅ | 5.79 s |
| Q16 | suivi_projet | 1 | ✅ | 6.04 s |
| Q17 | suivi_projet | 1 | ✅ | 6.35 s |
| Q18 | suivi_projet | 1 | ✅ | 4.83 s |
| Q19 | suivi_projet | 1 | ✅ | 5.77 s |
| Q20 | suivi_projet | 1 | ❌ | 4.95 s |
| Q21 | commande | 1 | ✅ | 408.0 ms |
| Q22 | commande | 1 | ✅ | 6.02 s |
| Q23 | commande | 1 | ✅ | 421.0 ms |
| Q24 | commande | 1 | ✅ | 418.0 ms |
| Q25 | commande | 1 | ❌ | 5.92 s |
| Q26 | faq | 1 | ✅ | 3.47 s |
| Q27 | faq | 1 | ✅ | 8.54 s |
| Q28 | faq | 1 | ✅ | 5.12 s |
| Q29 | hors_perimetre | n/a | ✅ refus | 586.0 ms |
| Q30 | hors_perimetre | n/a | ❌ pas de refus | 4.08 s |
