import re

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.http import HttpResponse

import requests
from bs4 import BeautifulSoup

from .models import Product


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}


def amazon(q, page=1):
    products = []
    for p in range(page):
        url = f'https://www.amazon.co.uk/s?k={q}&ref=nb_sb_noss_2'
        #url = f'https://www.amazon.co.uk/s?k={q}&page={p}&qid=1575603947&ref=sr_pg_2'
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        amazon_div = soup.find_all('div', class_='rush-component')
        for ad in amazon_div:
            try:
                name = ad.find('span', class_='a-size-medium a-color-base a-text-normal').text
                price = ad.find('span', class_='a-offscreen').text
                url = 'https://www.amazon.co.uk' + ad.find('a', class_='a-link-normal a-text-normal')['href']
                products.append({'name': name, 'price': price, 'url': url})
            except Exception as e:
                print(e)
                continue
            if len(products) ==5:
                break
    return products


def ebay(q):
    products = []
    url = f'https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={q}&_sacat=0'
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    ebay_div = soup.find_all('li', class_='sresult lvresult clearfix li shic')
    for ed in ebay_div:
        try:
            name = ed.find('a', class_='vip').text
            price = ed.find('li', class_='lvprice prc').span.text
            url = ed.find('a', class_='vip')['href']
            products.append({'name': name, 'price': price, 'url': url})
        except Exception as e:
            print(e)
            continue
        if len(products) ==10:
            break
    return products


def buyitdirect(q):
    products = []
    url = f'https://www.buyitdirect.ie/search-results/{q}'
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    buyitdirect_div = soup.find_all('div', class_='OfferBox')
    for bd in buyitdirect_div:
        try:
            name = bd.find('a', class_='offerboxtitle').text
            price = bd.find('span', class_='offerprice').text
            url = 'https://www.buyitdirect.ie' + bd.find('a', class_='offerboxtitle')['href']
            products.append({'name': name, 'price': price, 'url': url})
        except Exception as e:
            print(e)
            continue
        if len(products) == 10:
            break
    return products


def index(request):
    q = request.GET.get('q', '')
    data = Product.objects.all()
    if q:
        Product.objects.all().delete()
        amazon_product = amazon(q)
        ebay_product = ebay(q)
        buyitdirect_product = buyitdirect(q)
        for platform, products in enumerate([amazon_product, ebay_product, buyitdirect_product]):
            for product in products:
                is_exists = Product.objects.filter(keyword=q, name=['name']).first()
                if is_exists:
                    continue

                p = Product()
                p.keyword = q
                p.name = product['name']
                p.price = re.findall('\d+\.\d+', product['price'])[0]
                p.url = product['url']
                p.store = platform
                p.save()
        data = Product.objects.filter(keyword=q).all()

    paginator = Paginator(data, 6)
    product_list = paginator.page(1)
    if request.method == "GET":
        # get url page , original page= 1
        page = request.GET.get('page')
        try:
            product_list = paginator.page(page)
        except PageNotAnInteger:

            product_list = paginator.page(1)
        except InvalidPage:

            return HttpResponse('Cant find this page!')
        except EmptyPage:

            product_list = paginator.page(paginator.num_pages)


    return render(request, 'index.html', {'q': q, 'data':product_list})

