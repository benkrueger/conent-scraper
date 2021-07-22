import argparse
import os
import configparser
import json
import feedparser
import re
import urllib.request
from bs4 import BeautifulSoup
import html5lib
import httplib2
import shutil
from datetime import datetime
import hashlib
import pdfkit

#these we can just download
IMGREG = "<span>\<a\shref=\"(https:\/\/.+\.jpg)\">"
#these we can download and render a pdf with (hopefully)
HTMLREG = ""
def cli_args_init():
    parser = argparse.ArgumentParser(description='cmd line tool to parse a set of rss links and download content')
    parser.add_argument('--links',type=str,required=True,default='links.ini')
    return parser
def parse_config_file(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config
def parse_links_file(path):
    f = open(path,"r")
    links = json.load(f)

    return links

def create_content_dirs(links,path='./'):
    for site in links:
        path += site
        if os.path.isdir(path):
            print("{} dir exists".format(path))
        else:
            print("creating {} dir".format(path))
            os.mkdir(path)
        os.chdir(path)
        for sub in links[site]:
            
            path = "./{}".format(sub)
            if os.path.isdir(path):
                print("{} dir exists".format(path))
            else:
                print("creating {} dir".format(path))
                os.mkdir(path)
        os.chdir('../')

def link_download_pdf(path,link):
    now = datetime.now()
    m = hashlib.md5()
    m.update(link.encode('utf-8'))
    path += "{}.pdf".format(m.hexdigest())
    pdfkit.from_url(link, path)

#just download the image to a file, no big deal
def link_download_image(path,link):
    now = datetime.now()
    m = hashlib.md5()
    m.update(link.encode('utf-8'))
    path += "{}.jpg".format(m.hexdigest())
    print("Attempting to download image {} to file {}".format(link,path))
    with urllib.request.urlopen(link) as response, open(path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def parse_feed_content(feed,downdir):
    for e in feed.entries:
        try:
            if hasattr(e, 'content'):
                #image download
                for c in e.content:
                    m = re.search(IMGREG, c.value)
                    if m is not None:
                        print("Image found at {} ".format(m.group(1)))
                        link_download_image(downdir, m.group(1))
            if hasattr(e, 'links'):
                for l in e.links:
  
                    link_download_pdf(downdir, l['href'])

        except UnicodeEncodeError:
            print("Unicode encoding error")

def parse_feeds(links):
    for s in links:
        for l in links[s]:
            rss_link = links[s][l]
            currentfeed = l
            print("Fetching feed from {}".format(l))
            downdir = "./{}/{}/".format(s,currentfeed)
            d = feedparser.parse(rss_link)
            parse_feed_content(d, downdir)

  
def main():
    p = cli_args_init()
    args = p.parse_args()
    links = parse_links_file(args.links)
    #create_content_dirs(links)
    parse_feeds(links)
if __name__ == "__main__":
    main()