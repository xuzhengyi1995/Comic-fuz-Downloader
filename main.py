# Download book for https://comic-fuz.com/, XU Zhengyi, 01/03/2020
import copy
import gzip
import json
import math
import os
import re
from io import BytesIO
from urllib.parse import unquote

import PIL.Image as image
from threadpool import ThreadPool, makeRequests

import settings
from getHtml import GetHtml

URL = settings.URL
POOL_SIZE = settings.POOL_SIZE
NFBR_A0X_A3H = settings.NFBR_A0X_A3H
BLOCK_SIZE = settings.BLOCK_SIZE

HEADER = {}
HEADER['Cookie'] = settings.COOKIES


HEADER['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
HEADER['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
HEADER['Accept-Encoding'] = 'gzip'
HEADER['Referer'] = URL
HEADER['DNT'] = '1'
HEADER['Sec-Fetch-Mode'] = 'cors'
HEADER['Sec-Fetch-Site'] = 'same-site'
HEADER['Connection'] = 'keep-alive'
HEADER['Upgrade-Insecure-Requests'] = '1'
HEADER['Accept-Language'] = 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'


def caculate_pattern(no, file):
    no = 0
    final_string = str(file) + '/' + str(no)
    s = 0
    for i in final_string:
        s += ord(i)
    return s % NFBR_A0X_A3H + 1


def get_shuffle_data(width, height, block_width, block_height, pattern):
    '''
    block_width = 64
    block_height = 64
    '''
    y = math.floor(width / block_width)
    g = math.floor(height / block_height)
    f = width % block_width
    b = height % block_height
    S = []

    s = y - 43 * pattern % y
    if s % y == 0:
        s = (y - 4) % y
    if s == 0:
        s = y - 1

    a = g - 47 * pattern % g
    if a % g == 0:
        a = g - 4
    if a == 0:
        a = g - 1

    if f > 0 and b > 0:
        o = s * block_width
        u = a * block_height
        S.append({
            'srcX': o,
            'srcY': u,
            'destX': o,
            'destY': u,
            'width': f,
            'height': b
        })

        if b > 0:
            for l in range(y):
                d = calcXCoordinateXRest_(l, y, pattern)
                h = calcYCoordinateXRest_(d, s, a, g, pattern)
                c = calcPositionWithRest_(d, s, f, block_width)
                p = h * block_height
                o = calcPositionWithRest_(l, s, f, block_width)
                u = a * block_height
                S.append({
                    'srcX': o,
                    'srcY': u,
                    'destX': c,
                    'destY': p,
                    'width': block_width,
                    'height': b
                })

    if f > 0:
        for m in range(g):
            h = calcYCoordinateYRest_(m, g, pattern)
            d = calcXCoordinateYRest_(h, s, a, y, pattern)
            c = d * block_width
            p = calcPositionWithRest_(h, a, b, block_height)
            o = s * block_width
            u = calcPositionWithRest_(m, a, b, block_height)
            S.append({
                'srcX': o,
                'srcY': u,
                'destX': c,
                'destY': p,
                'width': f,
                'height': block_height
            })

    for l in range(y):
        for m in range(g):
            d = (l + 29 * pattern + 31 * m) % y
            h = (m + 37 * pattern + 41 * d) % g
            c = d * block_width
            if d >= calcXCoordinateYRest_(h, s, a, y, pattern):
                c += f
            p = h * block_height
            if h >= calcYCoordinateXRest_(d, s, a, g, pattern):
                p += b
            o = l * block_width
            if l >= s:
                o += f
            u = m * block_height
            if m >= a:
                u += b
            S.append({
                'srcX': o,
                'srcY': u,
                'destX': c,
                'destY': p,
                'width': block_width,
                'height': block_height
            })
    return S


def calcPositionWithRest_(e, t, r, i):
    if e >= t:
        return e * i + r
    return e * i


def calcXCoordinateXRest_(e, t, r):
    return (e + 61 * r) % t


def calcYCoordinateXRest_(e, t, r, i, n):
    if e < t:
        if n % 2 == 1:
            a = r
            s = 0
        else:
            a = i - r
            s = r
    else:
        if n % 2 != 1:
            a = r
            s = 0
        else:
            a = i - r
            s = r
    return (e + 53 * n + 59 * r) % a + s


def calcXCoordinateYRest_(e, t, r, i, n):
    if e < r:
        if n % 2 == 1:
            a = i - t
            s = t
        else:
            a = t
            s = 0
    else:
        if n % 2 != 1:
            a = i - t
            s = t
        else:
            a = t
            s = 0
    return (e + 67 * n + t + 71) % a + s


def calcYCoordinateYRest_(e, t, r):
    return (e + 73 * r) % t


def decode_and_save_image(org_img, width, height, pattern, file_full_path):
    draw_data = get_shuffle_data(
        width, height, BLOCK_SIZE, BLOCK_SIZE, pattern)
    des_img = image.new('RGB', (width, height))
    for i in draw_data:
        block = org_img.crop(
            (i['destX'], i['destY'], i['destX'] + i['width'], i['destY'] + i['height']))
        des_img.paste(block, (i['srcX'], i['srcY']))
    with open(file_full_path, 'wb') as image_f:
        des_img.save(image_f)


def get_auth_info(cid):
    url = 'https://comic-fuz.com/api4js/contents/license?cid=%s' % str(cid)
    getter = GetHtml()
    getter.set(url, header=HEADER, retryTimes=5)
    org_data = getter.get()
    try:
        data = gzip.decompress(org_data)
    except:
        data = org_data
    try:
        data = org_data.decode('utf-8')
    except:
        try:
            data = org_data.decode('EUC-JP')
        except:
            raise Exception('Unknow encoding.')
    auth_data = json.loads(data)
    return auth_data


def add_auth_info_to_url(url, auth_info):
    url += '?'
    l = len(auth_info)
    count = 0
    for i in auth_info:
        count += 1
        url = url + i + '=' + auth_info[i]
        if count < l:
            url += '&'
    return url


def get_configuration_pack(base_url, auth_info):
    url = base_url + 'configuration_pack.json'
    url = add_auth_info_to_url(url, auth_info)
    this_header = copy.deepcopy(HEADER)
    this_header['origin'] = 'https://comic-fuz.com'
    this_header['referer'] = 'https://comic-fuz.com/'

    getter = GetHtml()
    getter.set(url, header=this_header, retryTimes=5)
    org_data = getter.get()
    try:
        data = gzip.decompress(org_data)
    except:
        data = org_data
    try:
        data = org_data.decode('utf-8')
    except:
        try:
            data = org_data.decode('EUC-JP')
        except:
            raise Exception('Unknow encoding.')
    configuration_pack = json.loads(data)
    return configuration_pack


def get_image(url, page, pattern, save_dir):
    this_header = copy.deepcopy(HEADER)
    this_header['referer'] = 'https://comic-fuz.com/'

    getter = GetHtml()
    getter.set(url, header=this_header, retryTimes=5)
    org_data = getter.get()
    try:
        data = gzip.decompress(org_data)
    except:
        data = org_data

    org_image = image.open(BytesIO(data))
    width, height = org_image.size
    decode_and_save_image(org_image, width, height, pattern,
                          save_dir + '/%d.jpg' % page)
    print('Saved page %d' % page)


def download_book():
    re_cid = re.compile(r'cid=(.+?)&')
    re_cti = re.compile(r'cti=(.+?)&')

    cid = re_cid.findall(URL)[0]
    ctr = re_cti.findall(URL)[0]
    ctr = str(unquote(ctr))

    if not os.path.isdir(ctr):
        os.mkdir(ctr)

    auth_info = get_auth_info(cid)
    if auth_info['status'] == '200':
        base_url = auth_info['url']
        auth_info = auth_info['auth_info']
        confg_pack = get_configuration_pack(base_url, auth_info)
    else:
        raise Exception('Can not get auth info')

    contents = confg_pack['configuration']['contents']

    pool = ThreadPool(POOL_SIZE)
    args_list = []
    for i in range(len(contents)):
        this_file = contents[i]
        this_url = base_url + this_file['file'] + '/0.jpeg'
        url = add_auth_info_to_url(this_url, auth_info)

        pattern = caculate_pattern(i + 1, this_file['file'])
        args_list.append(((url, i + 1, pattern, ctr), None))

    requests = makeRequests(get_image, args_list)
    [pool.putRequest(i) for i in requests]
    pool.wait()


if __name__ == '__main__':
    download_book()
