import os
import shutil
from contextlib import suppress
from pathlib import Path

import pytest

try:
    import pep_parse
except ModuleNotFoundError:
    raise AssertionError('Назовите проект `pep_parse`')
try:
    from pep_parse import settings
except Exception:
    raise AssertionError(
        'Возникло исключение при импорте файла `pep_parse.settings`.'
    )


def find_results_path(module):
    results_path_var_name = None
    for name, value in vars(module).items():
        if not any((isinstance(value, Path), isinstance(value, str))):
            continue
        if isinstance(value, str):
            with suppress(Exception):
                cleaned_value = value.rstrip('/')
                basename = os.path.basename(cleaned_value)
                if basename == 'results' and len(cleaned_value.split('/')) > 1:
                    results_path_var_name = name
                    break
        elif isinstance(value, Path):
            if value.name == 'results' and len(value.parts) > 1:
                results_path_var_name = name
                break
    return results_path_var_name


@pytest.fixture
def mock_dirs(monkeypatch):
    file_path = Path(__file__).parent
    tmp_path = Path(os.path.relpath(file_path / '_tmp'))
    tmp_path.mkdir(exist_ok=True)
    mock_results_path = tmp_path / 'results'
    if hasattr(settings, 'BASE_DIR'):
        monkeypatch.setattr(settings, 'BASE_DIR', tmp_path)
    results_var_name = find_results_path(settings)
    if results_var_name:
        monkeypatch.setattr(settings, results_var_name, mock_results_path)

    try:
        from pep_parse import pipelines
    except Exception:
        raise AssertionError(
            'Возникло исключение при импорте файла `pep_parse.pipelines`.'
        )
    if hasattr(pipelines, 'BASE_DIR'):
        monkeypatch.setattr(pipelines, 'BASE_DIR', tmp_path)
    results_var_name = find_results_path(pipelines)
    if results_var_name:
        monkeypatch.setattr(pipelines, results_var_name, mock_results_path)

    yield tmp_path
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
@pytest.mark.usefixtures('mock_dirs')
def pep_parser_pipline_class():
    try:
        return pep_parse.pipelines.PepParsePipeline
    except Exception:
        raise AssertionError(
            'Возникло исключение при импорте файла `pep_parse.pipelines`.'
        )


@pytest.fixture
@pytest.mark.usefixtures('mock_dirs')
def parser_settings():
    return settings
