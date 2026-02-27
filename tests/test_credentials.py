try:
    from app.core.config import settings
except (NameError, ImportError):
    raise AssertionError(
        'Не обнаружен инициализированный объект `settings`.'
        'Проверьте и поправьте: он должен быть доступен в модуле '
        '`app.core.config`',
    )


def test_google_cred():
    need_cred = [
        'type',
        'project_id',
        'private_key_id',
        'private_key',
        'client_email',
        'client_id',
        'auth_uri',
        'token_uri',
        'auth_provider_x509_cert_url',
        'client_x509_cert_url',
        'email',
    ]
    missing_cred = [cred for cred in need_cred if not hasattr(settings, cred)]
    if missing_cred:
        raise AssertionError(
            'В настройках проекта (`app.core.config.Settings`) не обнаружены '
            f'следующие атрибуты: {", ".join(missing_cred)}'
        )
