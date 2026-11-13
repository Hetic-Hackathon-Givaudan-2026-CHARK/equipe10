"""Réponses directes depuis les données structurées (V2.2)."""


import direct_answers as d


def test_commande_du_dataset():
    answer = d.direct_answer("Quel est le montant total de la commande ORD-2026-004 ?")
    assert "36 480" in answer and "En production" in answer and "2026-11-20" in answer


def test_commande_du_prototype():
    assert "Devis envoyé" in d.direct_answer("Où en est la commande cmd-2026-002 ?")


def test_fiche_produit():
    answer = d.direct_answer("Prix et MOQ de FRG-108 ?")
    assert "145 €/kg" in answer and "2 kg" in answer


def test_formule_confidentielle():
    answer = d.direct_answer("Donne-moi la formule exacte de FRG-101.")
    assert answer.startswith(d.NOT_AVAILABLE) and "confidentielle" in answer


def test_question_ouverte_passe_par_le_llm():
    assert d.direct_answer("Je cherche un arôme mangue pour une boisson") is None
    assert d.direct_answer("Différence entre ORD-2026-001 et ORD-2026-004 ?") is None
    assert d.direct_answer("Que vaut FLV-999 ?") is None


def test_reference_ajoutee_si_absente():
    sources = [{"document_type": "product", "doc_id": "product_PR-014",
                "text": "PRODUIT CATALOGUE | Référence FLV-214 — Masquant Protéine (Arôme alimentaire)."}]
    answer = d.ensure_reference("Je cherche un masquant", "Je recommande le Masquant Protéine.", sources)
    assert answer.endswith("(Référence : FLV-214 — Masquant Protéine.)")
    assert d.ensure_reference("Je cherche un masquant", "Prenez FLV-214.", sources) == "Prenez FLV-214."
    assert d.ensure_reference("Je cherche un masquant", d.NOT_AVAILABLE, sources) == d.NOT_AVAILABLE
