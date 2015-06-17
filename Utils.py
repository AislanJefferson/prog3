__author__ = 'Aislan'
import urllib
import urlparse


def get_URL_Atual(o):
    return 'http://' + o.request.environ[
        'HTTP_HOST'] + o.request.path


def insert_URL_Params(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)
