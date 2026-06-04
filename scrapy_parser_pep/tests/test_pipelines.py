import inspect


def test_pep_parse_pipeline(pep_parser_pipline_class):
    assert inspect.isclass(pep_parser_pipline_class), (
        '`PepParsePipeline` должен быть классом.'
    )


def test_pipeline_open_spider(pep_parser_pipline_class):
    assert hasattr(pep_parser_pipline_class, 'open_spider'), (
        f'В классе `{pep_parser_pipline_class.__class__.__name__}` должен '
        'быть метод `open_spider`.'
    )
    assert callable(pep_parser_pipline_class.open_spider), (
        f'`open_spider` класса {pep_parser_pipline_class.__class__.__name__} '
        'должен быть вызываемым методом.'
    )
    pep_pipeline_signature = list(
        inspect.signature(pep_parser_pipline_class.open_spider).parameters,
    )
    assert set(pep_pipeline_signature) == {'self', 'spider'}, (
        'Метод `open_spider` класса '
        f'{pep_parser_pipline_class.__class__.__name__} должен принимать '
        'параметр `spider`'
    )


def test_pipeline_process_item(pep_parser_pipline_class):
    assert hasattr(pep_parser_pipline_class, 'process_item'), (
        f'В классе `{pep_parser_pipline_class.__class__.__name__}` '
        'должен быть метод `process_item`.'
    )
    assert callable(pep_parser_pipline_class.process_item), (
        f'`process_item` класса {pep_parser_pipline_class.__class__.__name__} '
        'должен быть вызываемым методом.'
    )
    pep_parse_pipeline_signature = list(
        inspect.signature(pep_parser_pipline_class.process_item).parameters,
    )
    assert set(pep_parse_pipeline_signature) == {'self', 'item', 'spider'}, (
        'Метод `process_item` класса '
        f'{pep_parser_pipline_class.__class__.__name__} должен принимать '
        'параметры `item, spider`'
    )


def test_pipeline_close_spider(pep_parser_pipline_class):
    assert hasattr(pep_parser_pipline_class, 'close_spider'), (
        f'В классе `{pep_parser_pipline_class.__class__.__name__}` '
        'должен быть метод `close_spider`.'
    )
    assert callable(pep_parser_pipline_class.close_spider), (
        f'`close_spider` класса {pep_parser_pipline_class.__class__.__name__} '
        'должен быть вызываемым методом.'
    )
    pep_parse_pipeline_signature = list(
        inspect.signature(pep_parser_pipline_class.close_spider).parameters,
    )
    assert set(pep_parse_pipeline_signature) == {'self', 'spider'}, (
        'Метод `close_spider` класса '
        f'{pep_parser_pipline_class.__class__.__name__} должен принимать '
        'параметр `spider`'
    )
