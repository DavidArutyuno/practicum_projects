import asyncio
import urllib

from flask import abort, flash, redirect, render_template

from . import app, db
from .forms import GenerateLinkForm, LoadFilesForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_YaDISK
from .utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = GenerateLinkForm()
    if form.validate_on_submit():
        if form.custom_id.data:
            short_id = form.custom_id.data
            if short_id == 'files':
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'warning'
                )
                return render_template('shortener.html', form=form)

            if URLMap.query.filter_by(short=short_id).first() is not None:
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'warning'
                )
                return render_template('shortener.html', form=form)
        else:
            short_id = get_unique_short_id()
        original = form.original_link.data
        url_map = URLMap(
            original=original,
            short=short_id
        )
        db.session.add(url_map)
        db.session.commit()

        short_link = f'http://localhost/{short_id}'

        flash(
            'Ваша новая ссылка готова:',
            'success'
        )
        return render_template(
            'shortener.html', form=form, short_link=short_link
        )

    return render_template('shortener.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def load_file_view():
    form = LoadFilesForm()
    if form.validate_on_submit():
        print(f"Получены файлы: {[f.filename for f in form.files.data]}")
        print(f"Токен: {app.config.get('DISK_TOKEN', 'NOT SET')}")

        list_links = asyncio.run(
            async_upload_files_to_YaDISK(form.files.data)
        )

        if list_links:
            flash('Файлы загружены!', 'success')

            # Создаем короткие ссылки для каждого файла
            file_links = {}
            for dict in list_links:
                for filename, link in dict.items():
                    short_id = get_unique_short_id()
                    original = link
                    url_map = URLMap(
                        original=original,
                        short=short_id
                    )
                    db.session.add(url_map)
                    db.session.commit()
                    short_link = f'http://localhost/{short_id}'
                    file_links[filename] = short_link
            return render_template(
                'loader.html', form=form, file_links=file_links
            )
        else:
            flash('Не удалось загрузить файлы.', 'error')

    return render_template('loader.html', form=form)


@app.route('/<string:short_link>', methods=['GET'])
def redirect_on_short_link_view(short_link):
    url_map = URLMap.query.filter_by(short=short_link).first()
    if not url_map:
        abort(404)

    original_url = url_map.original
    if '%' in original_url:
        try:
            original_url = urllib.parse.unquote(original_url)
        except Exception as e:
            print(f"Ошибка декодирования URL: {e}")
    return redirect(original_url)