from datetime import datetime, timezone

from flask import url_for

from yacut import db
from . import app


MAX_LENGTH = app.config.get('MAX_LENGTH', 16)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(MAX_LENGTH), nullable=True)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.now(timezone.utc))

    def to_dict(self):
        url_for_link = url_for('redirect_on_short_link_view',
                               short_link=self.short, _external=True)
        return dict(
            url=self.original,
            short_link=url_for_link

        )

    def from_dict(self, data):
        if 'url' in data:
            self.original = data['url']
        if 'custom_id' in data:
            self.short = data['custom_id']
