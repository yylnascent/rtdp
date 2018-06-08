class CommonETL(object):
    def __init__(self):
        pass
        
    def fetch_data(self, *args, **kwargs):
        raise NotImplementedError('please implemente fetch_data')

    def save_data(self, result):
        raise NotImplementedError('please implemente save_data')
