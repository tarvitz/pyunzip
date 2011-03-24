# coding: utf-8
import urllib2
import re
from django.http import HttpResponse,HttpResponseRedirect
from apps.farseer.models import Discount
from celery.task import task

def get_discount_percent(seq1,seq2):
    if seq1.__len__() != seq2.__len__(): return None
    discount = list()
    for i in range(0,seq1.__len__()):
        discount.append(int(
            round(100-(float(seq2[i])/(float(seq1[i])/100)))
            ))
    return discount

def get_discounts():
    url = "http://store.steampowered.com/search/?specials=1"
    try:
        stream = urllib2.urlopen(url)
    except urllib2.HTTPError:
        return None
    block = stream.read()
    #print "stream: ", block
    #parsing html
    r = re.compile(r'<!-- List Items -->(.*?)<!-- End List Items -->',re.S|re.U|re.I)
    if len(block)>1:
        block = r.findall(block)[0]
    else:
        return None
    #print "block: ", block
    #discount prices
    r = re.compile(r'<div class="col search_price.*?<br>.*?(\d+\.\d{1,2}).*?</div>',re.S|re.U|re.I)
    prices = r.findall(block)
    #real prices
    r = re.compile(r'<div class="col search_price.*?<strike>.*?(\d+\.\d{1,2})</strike>.*?</div>',re.S|re.U|re.I)
    real_prices = r.findall(block)
    #discount
    #names
    r = re.compile(r'<h4>(.*?)</h4>',re.I|re.U)
    names = r.findall(block)
    #url
    r = re.compile(r'href="(http://store.steampowered.com/app/.*?)"',re.S|re.I|re.U)
    urls = r.findall(block)
    #return dict(zip(names,prices))
    return zip(names,real_prices,prices,urls)

def update_discount_items(): 
    Discount.objects.all().delete()
    #ehm, lazy fixing? !true lazy
    while True:
        try:
            discounts = get_discounts()
            break
        except:
            pass
    #response = HttpResponse
    #response['Content-Type'] = 'plain/text'
    if discounts is None:
        #response.write('falied')
        return None
    for i in discounts:
        d = Discount(name=i[0],price=i[1],current_price=i[2],url=i[3])
        d.save()
    return True

update_discount = task()(update_discount_items)
