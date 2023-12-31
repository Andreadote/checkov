from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.enums import CheckResult


class KeyVaultEnablesSoftDelete(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that key vault enables soft delete"
        id = "CKV_AZURE_111"
        supported_resources = ['Microsoft.KeyVault/vaults']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "properties/enableSoftDelete"


check = KeyVaultEnablesSoftDelete()
