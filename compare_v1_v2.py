"""Comparaison mesurée V1 (mardi 10 novembre) / V2 (version publiée).

Les deux versions sont interrogées avec les MÊMES questions (30 cas de référence
et 10 cas inédits), chacune avec ses propres données et sa propre ingestion,
comme un utilisateur les aurait vécues :

- V1 : corpus figé de la démo du mardi (`data/v1/givaudan_data_v1.txt`, copie
  exacte du commit 61b9bf7) découpé avec la fonction d'ingestion de la V1
  (reproduite ci-dessous à l'identique) ;
- V2 : dataset actuel + base de connaissances du chatbot, découpés par `ingest.py`.

Les identifiants de documents de la V1 et de la V2 n'ont rien en commun : un
document est donc jugé « bon » s'il contient toutes les informations attendues
par le cas (`must_include`), ce qui s'applique de la même façon aux deux versions.

Deux modes :

    python compare_v1_v2.py            # sans IA ni Ollama : structure des données,
                                       # couverture des cas, recherche lexicale TF-IDF
    python compare_v1_v2.py --models   # avec les vrais modèles (Ollama) : recherche
                                       # par embeddings + réponses de la V1 avec son
                                       # prompt et son LLM d'origine (qwen2.5:1.5b)

Résultats : results/comparaison_v1_v2[_modeles].md et .json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import time
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import config
import evaluate
import ingest
from baseline_tfidf import strip_accents

BASE_DIR = Path(__file__).resolve().parent
V1_CORPUS = BASE_DIR / "data" / "v1" / "givaudan_data_v1.txt"
V1_COMMIT = "61b9bf7"
UNSEEN_CASES = BASE_DIR / "data" / "eval" / "unseen_cases.json"
TOP_K = 4

# LLM et prompt de la V1, repris de api.py au commit 61b9bf7.
V1_LLM_MODEL = "qwen2.5:1.5b"
V1_SYSTEM_PROMPT = """Tu es un assistant B2B pour une plateforme de commande intelligente.

Tu aides à retrouver des informations dans un dataset synthétique concernant :
- les clients ;
- les produits et leurs références ;
- les matières premières ;
- les commandes ;
- les demandes d'échantillons.

Règles :
1. Réponds uniquement à partir des extraits fournis.
2. N'invente jamais de client, produit, référence, commande, statut ou prix.
3. Si l'information n'est pas présente dans les extraits, réponds exactement :
   "Information non disponible dans les données fournies."
4. Cite les références importantes lorsque c'est possible.
5. Réponds dans la langue utilisée dans la question.
6. Sois professionnel, clair et concis.
"""

# Début d'une fiche dans les corpus : « PRODUIT | … », « COMMANDE | … »…
RECORD_RE = re.compile(
    r"(?m)^(?:CLIENT|PRODUIT(?: CATALOGUE)?|MATIÈRE PREMIÈRE|COMMANDE|ÉCHANTILLON"
    r"|PROJET DE CRÉATION|FAQ PLATEFORME) \|"
)

# Mêmes réglages que la V1 (config.py au commit 61b9bf7) : 800 caractères, 1 paragraphe repris.
V1_CHUNK_SIZE = 800
V1_CHUNK_OVERLAP = 1


# ---------------------------------------------------------------------------
# Ingestion de la V1, reproduite à l'identique (ingest.py au commit 61b9bf7)
# ---------------------------------------------------------------------------

V1_SECTION_RE = re.compile(r"^(?:chapter|chapitre)\s+\d+\s*[:.]", re.IGNORECASE)


def v1_split_into_sections(text: str) -> list[tuple[str, list[str]]]:
    """Découpage de la V1 : le titre n'est reconnu que s'il est seul dans son paragraphe."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if paragraphs and not V1_SECTION_RE.match(paragraphs[0]):
        paragraphs.pop(0)

    sections: list[tuple[str, list[str]]] = []
    current_title, current = "Introduction", []
    for paragraph in paragraphs:
        if V1_SECTION_RE.match(paragraph) and len(paragraph) < 150:
            if current:
                sections.append((current_title, current))
            current_title, current = paragraph, []
        else:
            current.append(paragraph)
    if current:
        sections.append((current_title, current))
    return sections


def v1_chunk(paragraphs: list[str]) -> list[str]:
    chunks, current, size = [], [], 0
    for paragraph in paragraphs:
        if current and size + len(paragraph) > V1_CHUNK_SIZE:
            chunks.append("\n\n".join(current))
            current = current[-V1_CHUNK_OVERLAP:] if V1_CHUNK_OVERLAP else []
            size = sum(len(item) for item in current)
        current.append(paragraph)
        size += len(paragraph)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def v1_document_type(section_title: str) -> str:
    title = section_title.lower()
    for key, kind in (("client_", "client"), ("product_", "product"),
                      ("raw_material_", "raw_material"), ("order_", "order"),
                      ("sample_", "sample")):
        if key in title:
            return kind
    return "unknown"


def load_v1() -> list[dict]:
    docs = []
    for title, paragraphs in v1_split_into_sections(V1_CORPUS.read_text(encoding="utf-8")):
        for chunk in v1_chunk(paragraphs):
            docs.append({"section": title, "type": v1_document_type(title), "text": chunk})
    return docs


def load_v2() -> list[dict]:
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    ingest.add_existing_dataset(config.DATASET_PATH, ids, documents, metadatas)
    ingest.add_knowledge_base(config.KNOWLEDGE_BASE_PATH, ids, documents, metadatas)
    return [
        {"section": m["title"], "type": m["document_type"], "text": d}
        for d, m in zip(documents, metadatas)
    ]


# ---------------------------------------------------------------------------
# Mesures
# ---------------------------------------------------------------------------


# Types de fiche qui peuvent répondre à chaque catégorie de question : libellé de
# fiche dans les corpus (« PRODUIT | … ») ou type des fiches de la base de connaissances.
CATEGORY_RECORDS = {
    "recommandation": {"PRODUIT", "PRODUIT CATALOGUE", "product"},
    "fiche_produit": {"PRODUIT", "PRODUIT CATALOGUE", "product"},
    "suivi_projet": {"PROJET DE CRÉATION", "ÉCHANTILLON"},
    "commande": {"COMMANDE"},
    "faq": {"FAQ PLATEFORME", "faq", "process", "policy", "capability"},
}
REFERENCE_RE = re.compile(r"\b[A-Z]{2,4}-\d{3}(?:-\d{3})?\b")
NAME_RE = re.compile(r"\b[A-ZÉÈÀ][\wÀ-ÿ'-]{2,}")
NOT_NAMES = {"Quel", "Quelle", "Quels", "Quelles", "Which", "What", "Pourquoi", "Combien",
             "Quand", "Avez", "Donne", "Où"}


def anchors(question: str) -> set[str]:
    """Références et noms propres cités dans la question (FRG-108, NutriPeak, Menthe Glaciale…)."""
    found = set(REFERENCE_RE.findall(question))
    for match in NAME_RE.finditer(question):
        word = match.group().strip("'-")
        before = question[: match.start()].rstrip()
        if not before or before[-1] in ".?!" or word in NOT_NAMES or re.fullmatch(r"V\d", word):
            continue
        found.add(word)
    return found


def records(doc: dict) -> list[tuple[str, str]]:
    """Découpe un document en fiches (libellé, texte) : un passage V1 en contient plusieurs."""
    starts = [m.start() for m in RECORD_RE.finditer(doc["text"])]
    if not starts:
        return [(doc["type"], doc["text"])]
    bounds = starts + [len(doc["text"])]
    pieces = [doc["text"][a:b] for a, b in zip(bounds, bounds[1:])]
    return [(piece.split(" |", 1)[0].strip(), piece) for piece in pieces]


def answers_case(doc: dict, case: dict) -> bool:
    """Une fiche du document répond-elle au cas ?

    La fiche doit être du bon type (produit, projet, commande, FAQ…), citer
    la référence (ou à défaut tous les noms propres) de la question, et contenir toutes les
    informations attendues. Sans ces deux premières conditions, un passage long
    qui mélange plusieurs fiches serait compté « bon » dès qu'il contient un
    chiffre attendu (« 3 », « 10 »…) dans une autre fiche.
    """
    allowed = CATEGORY_RECORDS.get(case["category"], set())
    names = anchors(case["question"])
    for label, text in records(doc):
        if label not in allowed:
            continue
        references = {name for name in names if REFERENCE_RE.fullmatch(name)}
        if references and not any(evaluate.contains(text, [ref]) for ref in references):
            continue
        if not references and not all(evaluate.contains(text, [name]) for name in names):
            continue
        if all(contains_value(text, group) for group in case["must_include"]):
            return True
    return False


def contains_value(text: str, alternatives: list[str]) -> bool:
    """Comme evaluate.contains, mais une valeur courte (« 3 », « 10 ») doit être un mot entier."""
    norm = evaluate.normalize(text)
    for alt in alternatives:
        alt = evaluate.normalize(alt)
        if len(alt) <= 3:
            if re.search(rf"(?<![\w.-]){re.escape(alt)}(?![\w.-])", norm):
                return True
        elif alt in norm:
            return True
    return False


def structure(docs: list[dict]) -> dict:
    records = [len(RECORD_RE.findall(d["text"])) for d in docs]
    return {
        "documents": len(docs),
        "typed_share": sum(d["type"] != "unknown" for d in docs) / len(docs),
        "mixed_share": sum(n > 1 for n in records) / len(docs),
        "distinct_sections": len({d["section"] for d in docs}),
    }


def lexical_ranker(docs: list[dict]):
    texts = [f"{d['section']}\n{d['text']}" for d in docs]
    vectorizer = TfidfVectorizer(preprocessor=strip_accents, ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform(texts)

    def rank(question: str) -> list[int]:
        scores = linear_kernel(vectorizer.transform([question]), matrix)[0]
        return list(scores.argsort()[::-1][:TOP_K])

    return rank


def embedding_ranker(docs: list[dict]):
    import rag

    vectors = rag.embed_documents([f"{d['section']}\n{d['text']}" for d in docs])

    def cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1.0)

    def rank(question: str) -> list[int]:
        query = rag.embed_query(question)
        scores = [cosine(query, v) for v in vectors]
        return sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:TOP_K]

    return rank


def v1_answer(question: str, docs: list[dict], retrieved: list[int]) -> str:
    """Réponse de la V1 : son prompt, son format de contexte, son LLM."""
    import ollama

    context = "\n\n---\n\n".join(
        f"[{docs[i]['section']} | type={docs[i]['type']}]\n{docs[i]['text']}" for i in retrieved
    )
    response = ollama.Client(host=config.OLLAMA_HOST).chat(
        model=V1_LLM_MODEL,
        messages=[
            {"role": "system", "content": V1_SYSTEM_PROMPT},
            {"role": "user", "content": f"Contexte récupéré :\n\n{context}\n\nQuestion utilisateur : {question}"},
        ],
        options={"temperature": 0.2, "num_predict": config.MAX_ANSWER_TOKENS},
    )
    return response["message"]["content"].strip()


def run(docs: list[dict], cases: list[dict], ranker, with_answers: bool) -> dict:
    per_case = []
    for case in cases:
        start = time.perf_counter()
        retrieved = ranker(case["question"])
        row = {"id": case["id"], "category": case["category"], "question": case["question"]}
        if case["expect_refusal"]:
            row["refusal_case"] = True
        else:
            good = [i for i, d in enumerate(docs) if answers_case(d, case)]
            rank = next((pos + 1 for pos, i in enumerate(retrieved) if i in good), None)
            row.update({"answerable": bool(good), "rank": rank})
        if with_answers:
            try:
                answer = v1_answer(case["question"], docs, retrieved)
            except Exception as exc:  # un cas en erreur ne bloque pas la comparaison
                answer, row["error"] = "", repr(exc)
            row["answer"] = answer
            if case["expect_refusal"]:
                row["refusal_ok"] = evaluate.contains(answer, evaluate.REFUSAL_MARKERS)
            else:
                row["answer_ok"] = all(evaluate.contains(answer, group) for group in case["must_include"])
        row["latency_s"] = round(time.perf_counter() - start, 3)
        per_case.append(row)

    answerable = [r for r in per_case if not r.get("refusal_case")]
    summary = {
        "cases": len(per_case),
        "answerable_cases": len(answerable),
        "coverage": sum(r["answerable"] for r in answerable) / len(answerable),
        "hit_at_4": sum(r["rank"] is not None for r in answerable) / len(answerable),
        "mrr": sum(1 / r["rank"] for r in answerable if r["rank"]) / len(answerable),
    }
    if with_answers:
        refusals = [r for r in per_case if r.get("refusal_case")]
        summary["answer_accuracy"] = sum(r["answer_ok"] for r in answerable) / len(answerable)
        summary["refusal_accuracy"] = (
            sum(r["refusal_ok"] for r in refusals) / len(refusals) if refusals else None
        )
        summary["latency_mean_s"] = round(statistics.mean(r["latency_s"] for r in per_case), 2)
    return {"summary": summary, "results": per_case}


def official_v2(label: str) -> dict | None:
    """Résultats officiels de la V2 publiée (pipeline complet : reclassement, réponses directes)."""
    path = evaluate.RESULTS_DIR / f"eval_{label}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["summary"]


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------


def pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f} %".replace(".", ",")


def seconds(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f} s".replace(".", ",")


def write_report(path: Path, report: dict) -> None:
    s1, s2 = report["structure"]["v1"], report["structure"]["v2"]
    mode = "modèles réels (Ollama)" if report["models"] else "sans IA (TF-IDF)"
    lines = [
        f"# Comparaison V1 / V2 — {mode}",
        "",
        f"Générée par `python compare_v1_v2.py{' --models' if report['models'] else ''}` le {report['date']}. "
        f"V1 = commit `{V1_COMMIT}` (démo du mardi 10 novembre), V2 = branche `main`. "
        "Méthode : [docs/COMPARAISON_V1_V2.md](../docs/COMPARAISON_V1_V2.md).",
        "",
        "## Données et ingestion",
        "",
        "| Critère | V1 | V2 |",
        "|---|---|---|",
        f"| Documents indexés | {s1['documents']} | {s2['documents']} |",
        f"| Documents avec un type métier reconnu | {pct(s1['typed_share'])} | {pct(s2['typed_share'])} |",
        f"| Documents mélangeant plusieurs fiches | {pct(s1['mixed_share'])} | {pct(s2['mixed_share'])} |",
        f"| Titres de section distincts | {s1['distinct_sections']} | {s2['distinct_sections']} |",
        "",
    ]
    retrieval = report["retrieval"]
    lines += [
        f"## Recherche ({report['retriever']}, top {TOP_K}, sans reclassement)",
        "",
        "Un document est « bon » s'il contient toutes les informations attendues par le cas.",
        "",
        "| Jeu de cas | Critère | V1 | V2 |",
        "|---|---|---|---|",
    ]
    for name, label in (("reference", "30 cas de référence"), ("unseen", "10 cas inédits")):
        a, b = retrieval[name]["v1"]["summary"], retrieval[name]["v2"]["summary"]
        lines += [
            f"| {label} | Cas dont la réponse existe dans les données | {pct(a['coverage'])} | {pct(b['coverage'])} |",
            f"| {label} | Bon document dans le top {TOP_K} | {pct(a['hit_at_4'])} | {pct(b['hit_at_4'])} |",
            f"| {label} | MRR | {a['mrr']:.3f} | {b['mrr']:.3f} |".replace(".", ","),
        ]
    lines.append("")

    if report["models"]:
        lines += [
            "## Réponses (V1 : `qwen2.5:1.5b` + prompt V1 ; V2 : version publiée V2.2, `qwen2.5:3b`)",
            "",
            "| Jeu de cas | Critère | V1 | V2 |",
            "|---|---|---|---|",
        ]
        for name, label, official in (("reference", "30 cas de référence", "v22_qwen3_llm3b"),
                                      ("unseen", "10 cas inédits", "v22_qwen3_llm3b_inedits")):
            a = retrieval[name]["v1"]["summary"]
            b = official_v2(official) or {}
            lines += [
                f"| {label} | Réponses exactes | {pct(a.get('answer_accuracy'))} | {pct(b.get('answer_accuracy'))} |",
                f"| {label} | Refus corrects (questions pièges) | {pct(a.get('refusal_accuracy'))} | {pct(b.get('refusal_accuracy'))} |",
                f"| {label} | Latence moyenne (CPU) | {seconds(a.get('latency_mean_s'))} | {seconds(b.get('latency_mean_s'))} |",
            ]
        lines += ["", "Les colonnes V2 reprennent `results/eval_v22_qwen3_llm3b*.json` (même protocole, CPU GitHub Actions).", ""]

    lines += ["## Détail par cas (30 cas de référence)", "", "| Cas | Catégorie | V1 : réponse dans les données | V1 : rang | V2 : rang |", "|---|---|---|---|---|"]
    for r1, r2 in zip(retrieval["reference"]["v1"]["results"], retrieval["reference"]["v2"]["results"]):
        if r1.get("refusal_case"):
            lines.append(f"| {r1['id']} | {r1['category']} | question piège | — | — |")
        else:
            lines.append(
                f"| {r1['id']} | {r1['category']} | {'oui' if r1['answerable'] else 'non'} "
                f"| {r1['rank'] or '—'} | {r2['rank'] or '—'} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", action="store_true",
                        help="recherche par embeddings (EMBED_MODEL) et réponses de la V1 via Ollama")
    args = parser.parse_args()

    docs = {"v1": load_v1(), "v2": load_v2()}
    case_sets = {
        "reference": json.loads(evaluate.DEFAULT_CASES.read_text(encoding="utf-8")),
        "unseen": json.loads(UNSEEN_CASES.read_text(encoding="utf-8")),
    }
    make_ranker = embedding_ranker if args.models else lexical_ranker
    rankers = {version: make_ranker(version_docs) for version, version_docs in docs.items()}

    retrieval = {
        name: {
            version: run(docs[version], cases, rankers[version], with_answers=args.models and version == "v1")
            for version in ("v1", "v2")
        }
        for name, cases in case_sets.items()
    }
    report = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "models": args.models,
        "retriever": f"embeddings `{config.EMBED_MODEL}`" if args.models else "TF-IDF lexical, sans IA",
        "structure": {version: structure(version_docs) for version, version_docs in docs.items()},
        "retrieval": retrieval,
    }

    label = "comparaison_v1_v2_modeles" if args.models else "comparaison_v1_v2"
    evaluate.RESULTS_DIR.mkdir(exist_ok=True)
    (evaluate.RESULTS_DIR / f"{label}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path = evaluate.RESULTS_DIR / f"{label}.md"
    write_report(md_path, report)
    print(md_path.read_text(encoding="utf-8").split("## Détail")[0])


if __name__ == "__main__":
    main()
