import sys
import time
import requests
from random import randrange
from threading import Thread
from utils import getProxy, getProxyFile, getSettings, sendHook
from urllib.parse import urlparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.24 Safari/537.36'}

settings = getSettings()


def getTimestamp():
    timeStruct = time.localtime()
    return "[" + str(timeStruct.tm_hour) + ":" + str(timeStruct.tm_min) + ":" + str(timeStruct.tm_sec) + "]"


def getProducts(shop):
    try:
        if not urlparse(shop).path:
            try:
                if settings['useProxy']:
                    resp = requests.get(shop + "/collections/all/products.json?limit=255",
                                        headers=headers, proxies=getProxy(settings['proxies'])).json()
                else:
                    resp = requests.get(
                        shop + "/collections/all/products.json?limit=255", headers=headers).json()
            except:
                if settings['useProxy']:
                    resp = requests.get(
                        shop + "/products.json?limit=255", headers=headers, proxies=getProxy(settings['proxies'])).json()
                else:
                    resp = requests.get(
                        shop + "/products.json?limit=255", headers=headers).json()
        else:
            if settings['useProxy']:
                resp = requests.get(shop + "/products.json?limit=255",
                                    headers=headers, proxies=getProxy(settings['proxies'])).json()
            else:
                resp = requests.get(
                    shop + "/products.json?limit=255", headers=headers).json()
        return resp['products']
    except:
        # print(traceback.print_exc())
        return None


def getProductInfo(productURL):
    try:
        if settings['useProxy']:
            resp = requests.get(
                productURL + ".js", headers=headers, proxies=getProxy(settings['proxies'])).json()
        else:
            resp = requests.get(productURL + ".js", headers=headers).json()
        return resp
    except:
        return None


def monitor(shop):
    current = getProducts(shop)
    while current == None:
        print('failed to get products for the first time')
        current = getProducts(shop)
        time.sleep(settings['ban_delay'])

    while True:
        foundNew = False
        if settings['showTimestamps']:
            print(getTimestamp() + " Checking for new...")
        new = getProducts(shop)

        while new == None:
            print('failed to get products')
            new = getProducts(shop)
            time.sleep(settings['ban_delay'])

        for item in new:
            if not any(d['id'] == item['id'] for d in current):
                if len(settings["keyWords"]) > 0:
                    valid = True
                    for keyword in settings["keyWords"]:
                        if(keyword[0] == "+"):
                            keyword = keyword[1:]
                            if(keyword.lower() not in item["title"].lower()):
                                valid = False
                                break
                        elif(keyword[0] == "-"):
                            keyword = keyword[1:]
                            if(keyword.lower() in item["title"].lower()):
                                valid = False
                                break
                    if valid:
                        print('new product: {}'.format(item['title']))
                        sendHook(item, settings['webhook'], "https://" + urlparse(shop).netloc, False)
                        foundNew = True
                else:
                    print('new product: {}'.format(item['title']))
                    sendHook(item, settings['webhook'], "https://" + urlparse(shop).netloc, False)
                    foundNew = True
        if foundNew:
            current = new
        time.sleep(settings['delay'])


def monitorRestock(url):
    current = getProductInfo(url)
    while current == None:
        print('[' + url + ']' + ' failed to get product for the first time')
        current = getProductInfo(url)
        time.sleep(settings['ban_delay'])

    while True:
        foundNew = False
        if settings['showTimestamps']:
            print(getTimestamp() + " Checking for restock...")
        new = getProductInfo(url)
        while new == None:
            print('[' + url + ']' + ' failed to get product')
            new = getProductInfo(url)
            time.sleep(settings['ban_delay'])

        for i in range(len(new['variants'])):
            if (current['variants'][i]['available'] == False) and (new['variants'][i]['available'] == True):
                # send hook
                print('restock: {}'.format(new['title']))
                sendHook(new, settings['webhook'],
                         "https://" + urlparse(url).netloc, True)
                foundNew = True
        if foundNew:
            current = new
        time.sleep(settings['delay'])


if __name__ == "__main__":
    for shop in settings['shops']:
        Thread(target=monitor, args=(shop,)).start()

    # for item in settings['restock_links']:
    #     Thread(target=monitorRestock, args=(item,)).start()

    # print(urlparse(settings['shops'][1]).path)
