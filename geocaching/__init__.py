# -*- encoding: utf-8 -*-

import atexit
import cgi
from ConfigParser import SafeConfigParser
import cookielib
from cStringIO import StringIO
import os
import re
from urllib import urlencode
import urllib2
from urlparse import urljoin, urlparse, urlunparse
import sys

from BeautifulSoup import BeautifulSoup
from lxml import etree, html

import tools

__all__ = ['Geo', 'GeoCache']

def extract_username(et):
    span = et.find('//span[@class="Success"]/strong')
    if span is not None:
        return span.text
    return None

attribute_map = {
    "dog": (1, "Dogs"),
    "dogs": (1, "Dogs allowed"),
    "fee": (2, "Access or parking fee"),
    "rappelling": (3, "Climbing gear"),
    "boat": (4, "Boat"),
    "scuba": (5, "Scuba gear"),
    "kids": (6, "Recommended for kids"),
    "onehour": (7, "Takes less than an hour"),
    "scenic": (8, "Scenic view"),
    "hiking": (9, "Significant hike"),
    "climbing": (10, "Difficult climbing"),
    "wading": (11, "May require wading"),
    "swimming": (12, "May require swimming"),
    "available": (13, "Available at all times"),
    "night": (14, "Recommended at night"),
    "winter": (15, "Available during winter"),
    "poisonoak": (17, "Poison plants"),
    "snakes": (18, "Snakes"),
    "ticks": (19, "Ticks"),
    "mines": (20, "Abandoned mines"),
    "cliff": (21, "Cliff / falling rocks"),
    "hunting": (22, "Hunting"),
    "danger": (23, "Dangerous area"),
    "wheelchair": (24, "Wheelchair accessible"),
    "parking": (25, "Parking available"),
    "public": (26, "Public transportation"),
    "water": (27, "Drinking water nearby"),
    "restrooms": (28, "Public restrooms nearby"),
    "phone": (29, "Telephone nearby"),
    "picnic": (30, "Picnic tables nearby"),
    "camping": (31, "Camping available"),
    "bicycles": (32, "Bicycles"),
    "motorcycles": (33, "Motorcycles"),
    "quads": (34, "Quads"),
    "jeeps": (35, "Off-road vehicles"),
    "snowmobiles": (36, "Snowmobiles"),
    "horses": (37, "Horses"),
    "campfires": (38, "Campfires"),
    "thorns": (39, "Thorns"),
    "thorn": (39, "Thorns!"),
    "stealth": (40, "Stealth required"),
    "stroller": (41, "Stroller accessible"),
    "firstaid": (42, "Needs maintenance"),
    "cow": (43, "Watch for livestock"),
    "flashlight": (44, "Flashlight required"),
    "landf": (45, "Lost And Found Tour"),
    }

def find_or_create(cache, tag):
    query = cache.xpath('.//*[local-name()="%s"]' % tag)
    if len(query) != 0:
        return query[0]

    groundspeak = cache.nsmap["groundspeak"]
    element = etree.Element("{%s}%s" % (groundspeak, tag))
    cache.append(element)
    return element

class Geo(object):
    cache_dir = os.path.expanduser("~/.cache/geocaching-py")
    config_dir = os.path.expanduser("~/.config/geocaching-py")
    
    def __init__(self, base_url="http://www.geocaching.com"):
        """
        Initialize GeoCaching.com interface, optionally with a user login and password
        """
        for dirname in (self.cache_dir, self.config_dir):
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        
        self.cookie_jar = cookielib.MozillaCookieJar(
            os.path.join(self.cache_dir, "cookies.txt"))
        self.cookie_jar.load()
        atexit.register(self.cookie_jar.save)
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib2.build_opener(self.cookie_processor)
        self.base_url = base_url

    def page_url(self, rel):
        return urljoin(self.base_url, rel)

    def send(self, url, data=None):
        reqtype = data and "POST" or "GET"
        print >> sys.stderr, "Sending %s request to %s" % (reqtype, url)
        return self.opener.open(url, data).read()
        
    def send_req(self, url, data=None):
        data = self.send(url, data)
        print >> sys.stderr, "Parsing"
        return html.parse(StringIO(data))

    def login_from_config(self):
        login, password = open(os.path.join(self.config_dir, "login")).read().strip().split(':', 1)
        return self.login(login, password)

    def login(self, login, password):
        page = self.page_url("/login/default.aspx")
        et = self.send_req(page)

        username = extract_username(et)
        if username is not None:
            if username == login:
                return username
            self.cookie_jar.clear()
            et = self.send_req(page)

        params = {}
        for input in (et.findall('//input[@type="hidden"]') + 
                      et.findall('//input[@type="submit"]')):
            params[input.name] = input.value
        params[et.find('//input[@type="text"]').name] = login
        params[et.find('//input[@type="password"]').name] = password
        params[et.find('//input[@type="checkbox"]').name] = "1"

        login_url = urljoin(page, et.find('//form').action)
        et = self.send_req(login_url, urlencode(params))
        return extract_username(et)

    def guid_from_gc(self, geocode):
        cache_details_url = self.page_url("/seek/cache_details.aspx?wp=" + geocode)
        et = self.send_req(cache_details_url)

        if not et.find('//title').text.strip().startswith(geocode):
            return None

        print_links = et.xpath('//a[contains(@href, "cdpf.aspx")]')
        if len(print_links) == 0:
            return None
        guid = cgi.parse_qs(urlparse(print_links[0].get("href")).query)["guid"][0]
        return guid
        
    def cache_gpx(self, guid):
        printable_url = self.page_url("/seek/cdpf.aspx?guid=" + guid)
        sendtogps_url = self.page_url("/seek/sendtogps.aspx?guid=" + guid)

        info_plain = self.send(printable_url)
        info = html.parse(StringIO(info_plain))
        print >> sys.stderr, "Parsing printable version with BeautifulSoup"
        info_soup = BeautifulSoup(info_plain)
        
        s2gps = self.send(sendtogps_url)
        s2gps = s2gps[s2gps.index("<?xml"):s2gps.index("</gpx>")+6]
        gpx = etree.parse(StringIO(s2gps))

        cache = tools.cache(gpx)
        if cache is None:
            return None

        short_desc = find_or_create(cache, "short_description")
        long_desc = find_or_create(cache, "long_description")
        hints = find_or_create(cache, "encoded_hints")
        
        short_desc.text = re.sub(r'\s+', ' ', info.find('//div[@id="div_sd"]').text_content()).strip()
        long_desc.text = info_soup.find("div", {"id": "div_ld"}).renderContents().decode('utf-8')
        long_desc.set("html", "True")

        try:
            hints_text = re.sub(r'\s+', ' ', info_soup.find("div", {"id":"div_hint"}).div.renderContents().decode('utf-8')).strip()
            hints_text = re.sub(r'<br ?/?>', "\n", hints_text).decode("rot13")
            hints.text = hints_text
        except AttributeError:
            hints.text = "No hint"

        attrs = find_or_create(cache, "attributes")
        for path in info.xpath('//img[contains(@src, "/attributes/")]/@src'):
            name, yesno = path.split("/")[-1].strip(".gif").split("-")
            if name in attribute_map:
                attr = find_or_create(attrs, "attribute")
                attr.set("id", str(attribute_map[name][0]))
                attr.text = attribute_map[name][1]
                if yesno == "yes":
                    attr.set("inc", "1")
                else:
                    attr.set("inc", "0")
                attrs.append(attr)
                    
        return gpx
