"""Réponses directes à partir des données structurées (V2.2).

Le LLM n'est pas indispensable quand la question cite une référence précise :
la réponse est déjà dans les tables (catalogue, suivi des commandes). On la
construit alors directement : exacte, instantanée, sans risque d'invention.
Le LLM reste utilisé pour les questions ouvertes (« je cherche un arôme… »).

Deux garde-fous complètent les réponses du LLM :
- une question sur une formule ou une composition est refusée (confidentialité) ;
- une recommandation de produit qui ne cite pas la référence commerciale est
  complétée par la référence du produit trouvé en premier.
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache

import config
import rerank

NOT_AVAILABLE = "Information non disponible dans les données fournies."

CONFIDENTIAL_RE = re.compile(
    r"\b(formule|formulation exacte|composition|recette|pourcentage de chaque|"
    r"liste des ingredients|formula|ingredients list)\b"
)
PRODUCT_REF_RE = re.compile(r"\b(?:FLV|FRG)-\d{3}\b", re.IGNORECASE)
ORDER_REF_RE = re.compile(r"\b(?:ORD|CMD)-\d{4}-\d{3}\b", re.IGNORECASE)


def _read(path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


@lru_cache(maxsize=1)
def _products() -> dict[str, dict]:
    rows = _read(config.BASE_DIR / "data" / "raw" / "products.csv")
    return {row["reference"].upper(): row for row in rows}


@lru_cache(maxsize=1)
def _orders() -> dict[str, dict]:
    orders = {}
    for path in (config.ORDERS_TRACKING_PATH, config.DATASET_ORDERS_PATH):
        for row in _read(path):
            orders[row["order_id"].upper()] = row
    # Montants des commandes du dataset (absents du fichier de suivi).
    for row in _read(config.BASE_DIR / "data" / "raw" / "orders.csv"):
        if row["order_id"].upper() in orders:
            orders[row["order_id"].upper()]["amount_eur"] = row.get("amount_eur", "")
            orders[row["order_id"].upper()]["discount_pct"] = row.get("discount_pct", "")
    return orders


def _amount(value: str) -> str:
    number = float(value)
    text = f"{number:,.2f}".replace(",", " ").replace(".", ",")
    return text[:-3] if text.endswith(",00") else text


def product_sheet(product: dict) -> str:
    kind = "arôme alimentaire" if product["domain"] == "Arôme" else "fragrance"
    return (
        f"{product['reference']} — {product['name']} ({kind}, famille {product['family'].lower()}) : "
        f"profil {product['profile']} ; applications : {product['applications']} ; "
        f"intensité {product['intensity']} ; naturalité : {product['naturalness']} ; "
        f"allergènes : {product['allergens']} ; dosage recommandé : {product['dosage']} ; "
        f"prix indicatif {product['price_eur_kg']} €/kg ; quantité minimale de commande "
        f"{product['moq_kg']} kg ; délai de fabrication {product['lead_time_days']} jours ouvrés ; "
        f"marchés : {product['markets']} ; statut : {product['status']}."
    )


def order_status(order: dict) -> str:
    parts = [
        f"La commande {order['order_id']} ({order['product_or_brief']}, {order['quantity']} {order['unit']}) "
        f"est au statut « {order['order_status']} »"
    ]
    if order.get("status_updated_at"):
        parts[0] += f" depuis le {order['status_updated_at'][:10]}"
    parts[0] += "."
    if order.get("estimated_delivery_date"):
        parts.append(f"Livraison prévue ou réalisée le {order['estimated_delivery_date']}.")
    if order.get("amount_eur"):
        discount = f", remise volume de {order['discount_pct']} % incluse" if order.get("discount_pct") not in ("", "0") else ""
        parts.append(f"Montant total : {_amount(order['amount_eur'])} € HT{discount}.")
    if order.get("tracking_message"):
        parts.append(order["tracking_message"])
    if order.get("next_action") and order["next_action"] != "Aucune":
        parts.append(f"Prochaine étape : {order['next_action']}.")
    return " ".join(parts)


def direct_answer(question: str) -> str | None:
    """Réponse construite depuis les données, ou None s'il faut passer par le LLM."""
    normalized = rerank.normalize(question)
    if CONFIDENTIAL_RE.search(normalized):
        return (f"{NOT_AVAILABLE} La composition détaillée des formules est confidentielle "
                "et n'est jamais communiquée.")

    orders = {ref.upper() for ref in ORDER_REF_RE.findall(question)}
    products = {ref.upper() for ref in PRODUCT_REF_RE.findall(question)}

    if len(orders) == 1 and not products:
        order = _orders().get(orders.pop())
        return order_status(order) if order else None
    if len(products) == 1 and not orders:
        product = _products().get(products.pop())
        return product_sheet(product) if product else None
    return None


def ensure_reference(question: str, answer: str, sources: list[dict]) -> str:
    """Ajoute la référence du produit recommandé si le LLM ne l'a pas citée."""
    if "product" not in rerank.question_intents(question) or not sources:
        return answer
    if PRODUCT_REF_RE.search(answer) or "ARM-" in answer.upper():
        return answer
    if rerank.normalize(NOT_AVAILABLE) in rerank.normalize(answer):
        return answer
    top = sources[0]
    if top.get("document_type") != "product":
        return answer
    match = PRODUCT_REF_RE.search(top.get("text", "")[:80]) or re.search(r"\bARM-\d{3}\b", top.get("doc_id", ""))
    if not match:
        return answer
    reference = match.group(0).upper()
    name = _products().get(reference, {}).get("name", "")
    return f"{answer.rstrip()} (Référence : {reference}{' — ' + name if name else ''}.)"
