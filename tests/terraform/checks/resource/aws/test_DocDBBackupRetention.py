import unittest

from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBBackupRetention import check


class TestDocDBBackupRetention(unittest.TestCase):

    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_DocDBBackupRetention"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_docdb_cluster.pass",
        }
        failing_resources = {
            "aws_docdb_cluster.fail_no_value",
            "aws_docdb_cluster.fail_value_not_adequate"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 3)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == '__main__':
    unittest.main()
