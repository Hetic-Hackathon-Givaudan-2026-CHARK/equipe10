# Comparaison V1 / V2 — sans IA (TF-IDF)

Générée par `python compare_v1_v2.py` le 2026-11-13 13:40. V1 = commit `61b9bf7` (démo du mardi 10 novembre), V2 = branche `main`. Méthode : [docs/COMPARAISON_V1_V2.md](../docs/COMPARAISON_V1_V2.md).

## Données et ingestion

| Critère | V1 | V2 |
|---|---|---|
| Documents indexés | 25 | 123 |
| Documents avec un type métier reconnu | 0,0 % | 100,0 % |
| Documents mélangeant plusieurs fiches | 100,0 % | 0,0 % |
| Titres de section distincts | 1 | 123 |

## Recherche (TF-IDF lexical, sans IA, top 4, sans reclassement)

Un document est « bon » s'il contient toutes les informations attendues par le cas.

| Jeu de cas | Critère | V1 | V2 |
|---|---|---|---|
| 30 cas de référence | Cas dont la réponse existe dans les données | 3,6 % | 100,0 % |
| 30 cas de référence | Bon document dans le top 4 | 0,0 % | 96,4 % |
| 30 cas de référence | MRR | 0,000 | 0,726 |
| 10 cas inédits | Cas dont la réponse existe dans les données | 11,1 % | 100,0 % |
| 10 cas inédits | Bon document dans le top 4 | 0,0 % | 100,0 % |
| 10 cas inédits | MRR | 0,000 | 0,759 |

## Détail par cas (30 cas de référence)

| Cas | Catégorie | V1 : réponse dans les données | V1 : rang | V2 : rang |
|---|---|---|---|---|
| Q01 | recommandation | oui | — | 2 |
| Q02 | recommandation | non | — | 1 |
| Q03 | recommandation | non | — | 2 |
| Q04 | recommandation | non | — | 2 |
| Q05 | recommandation | non | — | 1 |
| Q06 | recommandation | non | — | 2 |
| Q07 | recommandation | non | — | 1 |
| Q08 | recommandation | non | — | — |
| Q09 | fiche_produit | non | — | 2 |
| Q10 | fiche_produit | non | — | 1 |
| Q11 | fiche_produit | non | — | 2 |
| Q12 | fiche_produit | non | — | 1 |
| Q13 | fiche_produit | non | — | 1 |
| Q14 | suivi_projet | non | — | 2 |
| Q15 | suivi_projet | non | — | 1 |
| Q16 | suivi_projet | non | — | 3 |
| Q17 | suivi_projet | non | — | 2 |
| Q18 | suivi_projet | non | — | 2 |
| Q19 | suivi_projet | non | — | 1 |
| Q20 | suivi_projet | non | — | 1 |
| Q21 | commande | non | — | 2 |
| Q22 | commande | non | — | 1 |
| Q23 | commande | non | — | 1 |
| Q24 | commande | non | — | 1 |
| Q25 | commande | non | — | 2 |
| Q26 | faq | non | — | 1 |
| Q27 | faq | non | — | 1 |
| Q28 | faq | non | — | 2 |
| Q29 | hors_perimetre | question piège | — | — |
| Q30 | hors_perimetre | question piège | — | — |
