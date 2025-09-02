import logging
import os
from glob import glob

import pytest

from .test_builds import build_docs_setup, setup_clean_mkdocs_folder

pytestmark = pytest.mark.perf

logging.basicConfig(level=logging.INFO)


@pytest.mark.benchmark(group="build_performance")
def test_build_performance(benchmark, tmp_path):
    """
    Minimal sample
    """
    mkdocs_file = "tests/fixtures/mkdocs-benchmark.yml"
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path=mkdocs_file,
        output_path=tmp_path,
        docs_path="tests/fixtures/benchmark_docs",
    )

    file_amount = 100
    content_repeat = 100
    # repeat file content
    source_files = glob(f"{tmp_path}/testproject/benchmark_docs/*.md")
    logging.info(
        f"Create {len(source_files) * file_amount} files with {content_repeat} times content repeat"
    )
    for source_file in source_files:
        file_name = os.path.basename(source_file).split(".")[0]
        with open(source_file, "r") as f:
            content = f.read()
        # create files
        for i in range(file_amount):
            with open(
                f"{tmp_path}/testproject/benchmark_docs/{file_name}_{i}.md", "w"
            ) as f:
                for j in range(content_repeat):
                    f.write(content)

    def do_build():
        result = build_docs_setup(testproject_path)
        assert result.exit_code == 0, result.stdout
        return result

    benchmark(do_build)
