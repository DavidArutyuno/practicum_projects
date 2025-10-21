from datetime import datetime, timezone

from flask import url_for

from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(16), nullable=True)
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
        for field in ['url', 'custom_id']:
            if field in data and field == 'url':
                setattr(self, 'original', data[field])
            if field in data and field == 'custom_id':
                setattr(self, 'short', data[field])
