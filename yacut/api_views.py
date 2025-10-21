import string

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    allowed_chars = set(string.ascii_letters + string.digits)

    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!', 400)
    if 'custom_id' in data and data['custom_id']:
        custom_id = data['custom_id']

        if len(custom_id) > 16:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки', 400
            )

        if not set(data['custom_id']).issubset(allowed_chars):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки', 400
            )

        short_id = data['custom_id']
        if URLMap.query.filter_by(short=short_id).first() is not None:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки '
                'уже существует.', 400
            )
    else:
        short_id = get_unique_short_id()
        data['custom_id'] = short_id
    url_map = URLMap()
    url_map.from_dict(data)
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.to_dict()), 201


@app.route('/api/id/<string:id>/', methods=['GET'])
def get_url(id):
    url_map = URLMap.query.filter_by(short=id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    data = url_map.to_dict()
    return jsonify({'url': data.get('url')})
