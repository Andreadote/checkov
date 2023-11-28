from __future__ import annotations

from collections.abc import Iterable

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories

from checkov.yaml_doc.registry import registry


class BaseYamlCheck(BaseCheck):
    def __init__(
        self, name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_entities: Iterable[str],
        block_type: str,
        path: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
        registry.register(self)
