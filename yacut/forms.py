from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional


class GenerateLinkForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(1, 16), Optional()]
    )
    submit = SubmitField('Создать')


class LoadFilesForm(FlaskForm):
    files = MultipleFileField(
        'Выбрать файлы',
        validators=[
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
                message=(
                    'Выберите файлы с расширением '
                    '.jpg, .jpeg, .png, .gif или .bmp'
                )
            )
        ],
        render_kw={'multiple': True}
    )
    submit = SubmitField('Загрузить')