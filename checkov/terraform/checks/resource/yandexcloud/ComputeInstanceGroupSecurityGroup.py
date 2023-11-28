from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class ComputeInstanceGroupSecurityGroup(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure compute instance group has security group assigned."
        id = "CKV_YC_22"
        supported_resources = ("yandex_compute_instance_group",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "instance_template/[0]/network_interface/[0]/security_group_ids"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ComputeInstanceGroupSecurityGroup()
