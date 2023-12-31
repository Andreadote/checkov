from __future__ import annotations

import logging
import os
import re
from typing import List, Callable

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.terraform.module_loading.registry import module_loader_registry

MODULE_SOURCE_PATTERN = re.compile(r'[^#]*\bsource\s*=\s*"(?P<link>.*)"')
MODULE_VERSION_PATTERN = re.compile(r'[^#]*\bversion\s*=\s*"(?P<operator>=|!=|>=|>|<=|<|~>)?\s*(?P<version>[\d.]+-?\w*)"')


class ModuleDownload:
    def __init__(self, source_dir: str) -> None:
        self.source_dir = source_dir
        self.module_link: str | None = None
        self.version: str | None = None

    def __str__(self) -> str:
        return f"{self.source_dir} -> {self.module_link} ({self.version})"

    @property
    def address(self) -> str:
        return f'{self.module_link}:{self.version}'


def find_modules(path: str) -> List[ModuleDownload]:
    modules_found: list[ModuleDownload] = []

    for root, _, full_file_names in os.walk(path):
        for file_name in full_file_names:
            if not file_name.endswith('.tf'):
                continue

            try:
                content = read_file_with_any_encoding(file_path=os.path.join(path, root, file_name))
                if "module " not in content:
                    # if there is no "module " ref in the whole file, then no need to search line by line
                    continue

                curr_md = None
                for line in content.splitlines():
                    if not curr_md:
                        if line.startswith('module'):
                            curr_md = ModuleDownload(os.path.dirname(os.path.join(root, file_name)))
                            continue
                    else:
                        if line.startswith('}'):
                            if curr_md.module_link is None:
                                logging.warning(f'A module at {curr_md.source_dir} had no source, skipping')
                            else:
                                modules_found.append(curr_md)
                            curr_md = None
                            continue

                        if "source" in line:
                            match = re.match(MODULE_SOURCE_PATTERN, line)
                            if match:
                                curr_md.module_link = match.group('link')
                                continue

                        if "version" in line:
                            match = re.match(MODULE_VERSION_PATTERN, line)
                            if match:
                                curr_md.version = f"{match.group('operator')}{match.group('version')}" if match.group('operator') else match.group('version')
            except (UnicodeDecodeError, FileNotFoundError) as e:
                logging.warning(f"Skipping {os.path.join(path, root, file_name)} because of {e}")
                continue

    return modules_found


def should_download(path: str | None) -> bool:

    return path is not None and not (path.startswith('./') or path.startswith('../') or path.startswith('/'))


def load_tf_modules(
    path: str,
    should_download_module: Callable[[str | None], bool] = should_download,
    run_parallel: bool = False,
    modules_to_load: List[ModuleDownload] | None = None,
    stop_on_failure: bool = False
) -> None:
    module_loader_registry.root_dir = path
    if not modules_to_load:
        modules_to_load = find_modules(path)

    def _download_module(m: ModuleDownload) -> bool:
        if should_download_module(m.module_link):
            logging.info(f'Downloading module {m.address}')
            try:
                content = module_loader_registry.load(m.source_dir, m.module_link,
                                                      "latest" if not m.version else m.version)
                if content is None or not content.loaded():
                    log_message = f'Failed to download module {m.address}'
                    if not module_loader_registry.download_external_modules:
                        log_message += ' (for external modules, the --download-external-modules flag is required)'
                    logging.warning(log_message)
                    return False
            except Exception as e:
                logging.warning(f"Unable to load module ({m.address}): {e}")
                return False
        return True

    # To avoid duplicate work, we need to get the distinct module sources
    distinct_modules = list({m.address: m for m in modules_to_load}.values())

    if run_parallel:
        list(parallel_runner.run_function(_download_module, distinct_modules))
    else:
        logging.info(f"Starting download of modules of length {len(distinct_modules)}")
        for m in distinct_modules:
            success = _download_module(m)
            if not success and stop_on_failure:
                logging.info(f"Stopping downloading of modules due to failed attempt on {m.address}")
                break
