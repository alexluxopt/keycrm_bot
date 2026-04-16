from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass
class AggregatedProduct:
    sku: str
    name: str
    total_quantity: Decimal


def aggregate_products(orders: Iterable[Mapping[str, Any]]) -> list[AggregatedProduct]:
    grouped: dict[str, AggregatedProduct] = {}

    for order in orders:
        products = order.get("products", [])
        if not isinstance(products, list):
            continue

        for product in products:
            if not isinstance(product, Mapping):
                continue

            sku = str(product.get("sku", "")).strip()
            if not sku:
                continue

            name = str(product.get("name", "")).strip()
            quantity = _to_decimal(product.get("quantity"))

            if sku not in grouped:
                grouped[sku] = AggregatedProduct(sku=sku, name=name, total_quantity=Decimal("0"))

            grouped[sku].total_quantity += quantity

    return sorted(grouped.values(), key=lambda item: item.sku)


def format_report(items: Iterable[AggregatedProduct]) -> str:
    sorted_items = sorted(items, key=lambda item: item.sku)
    lines: list[str] = []
    previous_group: str | None = None

    for item in sorted_items:
        group = item.sku.split("_", 1)[0]
        if previous_group is not None and group != previous_group:
            lines.append("")

        lines.append(f"{item.sku} -- {_format_decimal(item.total_quantity)}")
        previous_group = group

    return "\n".join(lines) if lines else "No matching orders found."


def split_message(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current_lines: list[str] = []
    current_length = 0

    for line in text.splitlines():
        candidate_length = current_length + len(line) + (1 if current_lines else 0)
        if current_lines and candidate_length > max_length:
            chunks.append("\n".join(current_lines))
            current_lines = [line]
            current_length = len(line)
            continue

        if len(line) > max_length:
            if current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_length = 0

            chunks.extend(_split_long_line(line, max_length))
            continue

        current_lines.append(line)
        current_length = candidate_length

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks


def _split_long_line(line: str, max_length: int) -> list[str]:
    return [line[index : index + max_length] for index in range(0, len(line), max_length)]


def _to_decimal(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0")

    try:
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal("0")


def _format_decimal(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." not in text:
        return text
    return text.rstrip("0").rstrip(".")
