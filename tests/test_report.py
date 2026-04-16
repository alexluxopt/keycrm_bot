from decimal import Decimal
from unittest import TestCase

from app.report import AggregatedProduct, aggregate_products, format_report, split_message


class ReportTests(TestCase):
    def test_aggregate_products_groups_by_sku(self) -> None:
        orders = [
            {
                "products": [
                    {"sku": "AAA_1", "name": "Item A", "quantity": 2},
                    {"sku": "AAA_1", "name": "Item A", "quantity": "3"},
                    {"sku": "BBB_1", "name": "Item B", "quantity": 1},
                    {"sku": "", "name": "Skip me", "quantity": 10},
                ]
            },
            {
                "products": [
                    {"sku": "BBB_1", "name": "Item B", "quantity": "2.5"},
                    {"sku": "CCC", "name": "Item C", "quantity": None},
                ]
            },
        ]

        result = aggregate_products(orders)

        self.assertEqual(
            [(item.sku, item.total_quantity) for item in result],
            [
                ("AAA_1", Decimal("5")),
                ("BBB_1", Decimal("3.5")),
                ("CCC", Decimal("0")),
            ],
        )

    def test_format_report_inserts_blank_line_on_group_change(self) -> None:
        items = [
            AggregatedProduct(sku="AAA_1", name="Item A", total_quantity=Decimal("5")),
            AggregatedProduct(sku="AAA_2", name="Item A2", total_quantity=Decimal("7")),
            AggregatedProduct(sku="BBB_1", name="Item B", total_quantity=Decimal("3")),
        ]

        self.assertEqual(
            format_report(items),
            "AAA_1 -- 5\nAAA_2 -- 7\n\nBBB_1 -- 3",
        )

    def test_split_message_keeps_lines_intact_when_possible(self) -> None:
        message = "row-1\nrow-2\nrow-3"

        self.assertEqual(split_message(message, max_length=8), ["row-1", "row-2", "row-3"])
