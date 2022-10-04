import sys
import json
import os
import time
import requests
import traceback
from random import randrange


def getSettings():
    headers_file = 'settings.json'

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    config_path = os.path.join(application_path, headers_file)

    # settings
    settings = []
    try:
        with open(config_path, 'r+') as f:
            settings = json.load(f)
    except:
        print('No settings.json file found!')

    return settings


def getProxyFile():
    proxy_file = 'proxies.txt'

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    config_path = os.path.join(application_path, proxy_file)

    # proxies
    proxies = []
    try:
        with open(config_path, 'r+') as f:
            proxies = f.readlines()
    except:
        print(traceback.print_exc())
        print('No proxies.txt file found!')
    return proxies


def getProxy(proxies):
    prox = proxies[randrange(0, len(proxies))].rstrip('\n')
    prox_info = prox.split(':')
    return {'https': 'https://' + prox_info[2] + ':' + prox_info[3] + '@' + prox_info[0] + ':' + prox_info[1]}


def sendHook(product, webhook, shop, restock):
    webhookas = "https://discordapp.com/api/webhooks/988812556514779178/XHbO-gf0N3c_x9qRmr5ASfrnonaBlCoTQ1ZJUtyJLBW1VnrWpRzukb3uLCr1_gkxaOKq"
    timeStruct = time.localtime()
    timestamp = "[" + str(timeStruct.tm_hour) + ":" + \
        str(timeStruct.tm_min) + ":" + str(timeStruct.tm_sec) + "]"

    desc = ""
    try:
        desc = '**Price**: {0} | **Site**: {1}'.format(
            product['variants'][0]['price'], shop)
    except:
        desc = '**Price**: 0 | **Site**: {0}'.format(shop)

    fields = []

    for size in product["variants"]:
        if size["available"]:
            temp = {'name': '**ATC**',
                    'value': '[{0}]({1})'.format(size['title'], shop + '/cart/' + str(size['id']) + ':1'),
                    'inline': True}
            fields.append(temp)

    productUrl = shop + "/product/" + product['handle']

    thumbnail = ""
    obj = {}
    title = ""
    if restock:
        title = product['title'] + " RESTOCKED"
    else:
        title = product['title'] + " ADDED"
    try:
        thumbnail = product['images'][0]['src']
        obj = {'embeds': [{
            'title': title,
            'description': desc,
            'url': shop + "/products/" + str(product['handle']),
            'thumbnail': {
                'url': product['images'][0]['src']
            },
            'fields': fields,
            'color': '11139072'
        }]}
    except:
        obj = {'embeds': [{
            'title': title,
            'description': desc,
            'url': shop + "/products/" + str(product['handle']),
            'fields': fields,
            'color': '11139072'
        }]}
    resp = requests.post(webhook, json=obj)
    while not resp.status_code == 204:
        print("too many requests... retrying...")
        resp = requests.post(webhookas, json=obj)
    if resp.status_code == 204:
        return 0
