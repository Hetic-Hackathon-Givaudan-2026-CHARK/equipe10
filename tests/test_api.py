"""Ingestion et API de bout en bout (embedding et LLM de test)."""

import ingest


def test_decoupage_une_section_par_fiche():
    text = ingest.config.DATASET_PATH.read_text(encoding="utf-8")
    _, sections = ingest.split_into_sections(text)
    assert len(sections) == 103
    assert all(ingest.get_document_type(title) != "unknown" for title, _ in sections)
    assert ingest.get_doc_id("Chapter 12: product_PR-001") == "product_PR-001"


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["indexed_documents"] == 123   # 103 du dataset + 20 de la base de connaissances
    assert body["rerank"] is True


def test_demo_ping(client):
    assert client.get("/demo/ping").json()["status"] == "ok"


def test_search_renvoie_les_champs_du_contrat(client):
    sources = client.post("/search", json={"question": "arôme mangue boisson protéinée"}).json()
    assert len(sources) == 4
    assert set(sources[0]) == {"section", "doc_id", "document_type", "domain", "text", "score", "metadata", "rank_score"}
    # L'ordre des sources suit rank_score (similarité + bonus du reclassement).
    assert [s["rank_score"] for s in sources] == sorted((s["rank_score"] for s in sources), reverse=True)


def test_search_reference_exacte_en_premier(client):
    sources = client.post("/search", json={"question": "Quel est le statut de la commande ORD-2026-007 ?"}).json()
    assert sources[0]["doc_id"] == "order_ORD-2026-007"


def test_filtre_de_domaine(client):
    for domain in ("fragrance", "dairy_aroma"):
        sources = client.post("/search", json={"question": "produit floral fruité", "domain": domain, "top_k": 10}).json()
        assert {s["domain"] for s in sources} <= {domain, "shared"}


def test_ask(client):
    response = client.post("/ask", json={"question": "Où en est le projet PJ-003 ?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] and body["sources"] and body["answer_source"] == "llm"


def test_validation_de_la_requete(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "x", "domain": "autre"}).status_code == 422


def test_orders_un_seul_format(client):
    dataset_order = client.get("/orders/ORD-2026-007").json()
    prototype_order = client.get("/orders/CMD-2026-003").json()
    assert set(dataset_order) == set(prototype_order)
    assert dataset_order["order_status"] == "Expédiée"
    assert client.get("/orders/ord-2026-010").json()["order_status"] == "Annulée"


def test_orders_introuvable(client):
    assert client.get("/orders/INCONNUE").status_code == 404


def test_cors_pour_les_interfaces_web(client):
    response = client.options("/ask", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] in {"*", "http://localhost:5173"}


def test_contrat_openapi_a_jour(indexed):
    import json
    from pathlib import Path

    exported = json.loads((Path(__file__).resolve().parents[1] / "docs" / "openapi.json").read_text(encoding="utf-8"))
    assert exported == json.loads(json.dumps(indexed.app.openapi())), \
        "docs/openapi.json n'est plus à jour : lancer python export_openapi.py"


def test_ask_reponse_directe(client):
    body = client.post("/ask", json={"question": "Quel est le statut de la commande ORD-2026-007 ?"}).json()
    assert body["answer_source"] == "donnees"
    assert "Expédiée" in body["answer"] and body["sources"][0]["doc_id"] == "order_ORD-2026-007"


def test_metadonnees_metier_dans_les_sources(client):
    sources = client.post("/search", json={"question": "Quel est le statut de la commande ORD-2026-007 ?"}).json()
    order = sources[0]["metadata"]
    assert order["order_id"] == "ORD-2026-007" and order["client_id"] == "CL-004"
    assert order["reference"] == "FLV-212" and order["status"] == "Expédiée"
    assert order["amount_eur"] == 95040.0 and order["delivery_date"] == "2026-11-16"
    assert "chunk_index" not in order

    product = client.post("/search", json={"question": "Prix de FRG-108 ?"}).json()[0]["metadata"]
    assert product["reference"] == "FRG-108" and product["price_eur_kg"] == 145 and product["moq_kg"] == 2

    project = client.post("/search", json={"question": "Où en est le projet PJ-003 ?"}).json()[0]["metadata"]
    assert project["project_id"] == "PJ-003" and project["stage"] == "Rectification" and project["progress_pct"] == 60


def test_evaluation_pour_la_demo(client):
    body = client.get("/evaluation").json()
    assert body["modele"] == {"embeddings": "qwen3-embedding:4b", "llm": "qwen2.5:3b", "reclassement": True}
    reference = body["cas_de_reference"]
    assert reference["cas"] == 30 and reference["reponses_exactes"] == 0.964 and reference["refus_corrects"] == 1.0
    assert body["cas_inedits"]["cas"] == 10
    comparaison = body["comparaison_v1_v2"]
    assert comparaison["documents_indexes"]["v1"] == 25
    assert comparaison["documents_types"] == {"v1": 0.0, "v2": 1.0}
    assert comparaison["reponses_exactes"]["v2"] == 0.964
