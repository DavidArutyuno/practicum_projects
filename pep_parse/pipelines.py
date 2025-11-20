import csv
import os
from datetime import datetime

from pep_parse.settings import (
    DATETIME_FORMAT, FEED_EXPORT_ENCODING, RESULTS_DIR
)


class PepParsePipeline:
    def open_spider(self, spider):
        """Вызывается при запуске паука."""
        self.total_count = 0
        self.status_count = {
            'Active': 0,
            'Accepted': 0,
            'Deferred': 0,
            'Final': 0,
            'Provisional': 0,
            'Rejected': 0,
            'Superseded': 0,
            'Withdrawn': 0,
            'Draft': 0,
            'Active': 0,
            'April Fool!': 0,
            'Total': 0,
        }

    def process_item(self, item, spider):
        """Обрабатывает каждый Item."""
        status = item.get('status', 'Unknown')
        self.status_count[status] += 1
        self.total_count += 1
        return item

    def close_spider(self, spider):
        """Вызывается при завершении работы паука."""
        os.makedirs('results', exist_ok=True)

        timestamp = datetime.now().strftime(DATETIME_FORMAT)
        filename = RESULTS_DIR / f'status_summary_{timestamp}.csv'

        with open(
            filename, 'w', newline='', encoding=FEED_EXPORT_ENCODING
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Статус', 'Количество'])
            rows_to_write = [
                [status, count]
                for status, count in sorted(self.status_count.items())
            ]
            rows_to_write.append(['Total', self.total_count])
            writer.writerows(rows_to_write)
