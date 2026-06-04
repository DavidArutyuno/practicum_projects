import asyncio

from flask import flash, redirect, render_template

from . import app, db
from .forms import GenerateLinkForm, LoadFilesForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_YaDISK
from .utils import (
    create_short_links_for_files,
    get_unique_short_id,
    merge_links_dicts
)


BASE_URL = app.config.get('BASE_URL', 'http://localhost')


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

        short_link = f'{BASE_URL}/{short_id}'

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
        # Загружаем файлы на Яндекс.Диск
        yandex_links_list = asyncio.run(
            async_upload_files_to_YaDISK(form.files.data)
        )

        if yandex_links_list:
            flash('Файлы загружены!', 'success')

            # Объединяем словари и создаем короткие ссылки
            merged_links = merge_links_dicts(yandex_links_list)
            file_links = create_short_links_for_files(merged_links)

            return render_template(
                'loader.html', form=form, file_links=file_links
            )
        else:
            flash('Не удалось загрузить файлы.', 'error')

    return render_template('loader.html', form=form)


@app.route('/<string:short_link>', methods=['GET'])
def redirect_on_short_link_view(short_link):
    url_map = URLMap.query.filter_by(short=short_link).first_or_404()
    return redirect(url_map.original)
