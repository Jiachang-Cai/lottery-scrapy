import datetime
import hashlib
import os
import uuid
import re
import requests
import time
from scrapy.http import Request, Headers
from scrapy.utils.reqser import request_to_dict, request_from_dict
from requests.adapters import HTTPAdapter
from scrapy.responsetypes import responsetypes


# 2a47d8b6-6f5b-11e6-ac9d-64006a0b51ab
def get_uuid():
    return str(uuid.uuid1())


# 2016-08-31T09:13:22.434Z
def get_utc_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[
           :-3] + "Z"


def get_md5(content):
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest()


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def http_request(url, ip, timeout=30):
    session = requests.Session()
    session.proxies = {'http': 'http://%s' % ip,
                       'https': 'http://%s' % ip}
    session.mount('https://', HTTPAdapter(max_retries=5))
    session.mount('http://', HTTPAdapter(max_retries=5))
    response = session.get(url, timeout=timeout)
    return response


def log(content):
    print(
        "============================= {content} ==========================".format(
            content=(get_utc_time() + " " + content)))


def normalize_whitespace(str):
    if str == None:
        return ""
    str = str.strip()
    str = re.sub(r'\s+', ' ', str)
    return special_str(str)


def normalize_list_whitespace(list):
    if list == None:
        return []
    for index, item in enumerate(list):
        str = item.strip()
        list[index] = re.sub(r'\s+', ' ', special_str(str))
    return list


def special_str(str):
    return str.replace('"', '\\"').replace('/', '\\/').replace('\\', '\\\\')


def response_to_dict(response, spider, include_request=True, **kwargs):
    """Returns a dict based on a response from a spider"""
    d = {
        'time': time.time(),
        'status': response.status,
        'url': response.url,
        'headers': dict(response.headers),
        # 'body': response.body,
    }
    if include_request:
        d['request'] = request_to_dict(response.request, spider)
    return d


def response_from_dict(response, spider=None, **kwargs):
    """Returns a dict based on a response from a spider"""
    url = response.get("url")
    status = response.get("status")
    headers = Headers([(x, list(map(str, y))) for x, y in
                       response.get("headers").items()])
    body = response.get("body")

    respcls = responsetypes.from_args(headers=headers, url=url)
    response = respcls(url=url, headers=headers, status=status, body=body)
    return response
