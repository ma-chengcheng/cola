import sitting
import requests


class Request(object):

    def __init__(self, url, callback=None, method='GET', headers=sitting.headers,  encoding='utf-8'):

        self._set_url(url)
        self.method = method
        self.headers = headers

        if callback is not None and not callable(callback):
            raise TypeError('callback must be set, got {}'.format(type(callback)))
        self.callback = callback
        self._encoding = encoding

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        self._url = url

    @property
    def response(self):
        if self.method == 'GET':
            response = requests.get(url=self._get_url(), headers=self.headers)
            return response

    @property
    def encoding(self):
        return self._encoding

    def __str__(self):
        return "".format(self.method, self._url)

    __repr__ = __str__

