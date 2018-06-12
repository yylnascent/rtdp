import logging

from datetime import datetime, timedelta

log = logging.getLogger('abstracts')

class CommonETL(object):
    def __init__(self):
        pass

    def format_sql(self, sql, **kwargs):
        params = {
            'TODAY': datetime.now().strftime('%Y-%m-%d'),
            'today': datetime.now().strftime('%Y%m%d'),
            'YESTERDAY': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'yesterday': (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'),
            'TOMORROW': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'tomorrow': (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
        }

        params.update(kwargs)

        if sql:
            for argkey, argvalue in params.items():
                log.debug('argkey %s, argvalue %s.', argkey, argvalue)
                sql = sql.replace('${' + argkey + '}', argvalue)

        log.debug('formated sql: %s.', sql)

        return sql
        
    def fetch_data(self, *args, **kwargs):
        raise NotImplementedError('please implemente fetch_data')

    def save_data(self, result):
        raise NotImplementedError('please implemente save_data')

if __name__ == "__main__":
    CommonETL().format_sql()