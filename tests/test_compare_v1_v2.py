"""Comparaison V1 / V2 (compare_v1_v2.py), mode sans IA."""


import compare_v1_v2 as compare


def test_ingestion_v1_reproduit_les_defauts_constates():
    docs = compare.load_v1()
    structure = compare.structure(docs)
    # Démo du mardi : 25 passages, tous « Introduction » / « unknown », chacun mélangeant plusieurs fiches.
    assert structure["documents"] == 25
    assert structure["typed_share"] == 0
    assert structure["mixed_share"] == 1
    assert structure["distinct_sections"] == 1


def test_ingestion_v2_une_fiche_par_document(indexed):
    structure = compare.structure(compare.load_v2())
    assert structure["typed_share"] == 1
    assert structure["mixed_share"] == 0


def test_entites_de_la_question():
    assert compare.anchors("Quel est le statut de la commande ORD-2026-007 ?") == {"ORD-2026-007"}
    assert compare.anchors("Où en est le projet de lessive de Lumina Laundry ?") == {"Lumina", "Laundry"}
    assert compare.anchors("Plutôt vegan. Que proposez-vous ?") == set()


def test_un_chiffre_isole_ne_suffit_pas():
    case = {"category": "faq", "question": "Combien de rectifications sont incluses ?", "must_include": [["3"]]}
    melange = {"type": "unknown", "text": "ÉCHANTILLON | SMP-001. Quantité : 3 kg.\nCOMMANDE | ORD-1. Montant : 300 EUR."}
    faq = {"type": "unknown", "text": "FAQ PLATEFORME | Rectifications : 3 incluses, puis payantes."}
    assert not compare.answers_case(melange, case)
    assert compare.answers_case(faq, case)


def test_la_reference_citee_est_exigee():
    case = {"category": "fiche_produit", "question": "L'arôme FLV-207 est-il disponible en Allemagne ?",
            "must_include": [["Belgique"]]}
    autre_produit = {"type": "unknown", "text": "PRODUIT | Référence : FRG-104. Marchés : Belgique, Allemagne."}
    assert not compare.answers_case(autre_produit, case)


def test_rapport_sans_ia(indexed, tmp_path, monkeypatch):
    monkeypatch.setattr(compare.evaluate, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr("sys.argv", ["compare_v1_v2.py"])
    compare.main()
    report = (tmp_path / "comparaison_v1_v2.md").read_text(encoding="utf-8")
    assert "| Documents indexés | 25 |" in report
    assert (tmp_path / "comparaison_v1_v2.json").exists()
