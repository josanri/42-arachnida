from bs4 import BeautifulSoup
import requests
import urllib3
import sys
import os
import time
import argparse

class Spider:
    def __init__(self, recursion=False, max_depth=1, image_dir="./data", debug_data=False) -> None:
        self.files_downloaded = 0
        self.recursion = recursion
        self.max_depth = max_depth
        self.original_url = ""
        self.visited_urls = set()
        self.visited_images = set()
        self.image_dir = image_dir
        self.debug_data = debug_data
        os.mkdir(self.image_dir)

    def download_image(self, image_url:str):
        req = requests.get(image_url)
        if req.status_code != 404 and req.status_code != 302:
            open_file = open(self.image_dir + "/" + str(self.files_downloaded) + Spider.get_extension(image_url), "wb")
            open_file.write(req.content)
            open_file.close()
            self.files_downloaded += 1

    def start_scrapping(self, original_url):
        self.original_url = original_url
        if self.debug_data:
            self.debug_file = open(self.image_dir + "/urls.txt", "wt")
        try:
            print("Start scrapping")
            self.scrap(original_url, 1)
        except Exception as err:
            print(err)
        if self.debug_data:
            self.debug_file.close()

    def scrap(self, url: str, level: int):
        if level > self.max_depth or url in self.visited_urls:
            return
        self.visited_urls.add(url)
        if url.startswith("file://"):
            http_pool = urllib3.PoolManager()
            #open_file = open(url[len("file://")::], "rt")
            #data_html = open.read()
            #open_file.close()
            data_html = http_pool.request('GET', url).data
        else:
            req = requests.get(url)
            data_html = req.content.decode("utf-8")
        soup = BeautifulSoup(data_html, "html.parser")
        image_tags = soup.find_all('img')
        for link in image_tags:
            image_url = link.get('src')
            if image_url != None and image_url != "" and not image_url in self.visited_images and Spider.get_extension(Spider.get_extension(image_url)) in (".png", ".gif", ".jpg", ".jpeg", ".bmp"):
                if self.debug_data:
                    self.debug_file.write(f"{self.files_downloaded} {image_url}\n")
                self.download_image(image_url)
                self.visited_images.add(image_url)
        if self.recursion:
            for link in soup.find_all():
                new_reference = link.get('href')
                if new_reference != None and isinstance(new_reference, str) and new_reference.startswith(self.original_url):
                    try:
                        self.scrap(new_reference, level=(level + 1))
                    except Exception:
                        pass
    def get_extension(image_url:str):
        if image_url.rfind('.') != -1:
            return image_url[image_url.rfind('.')::]
        return ""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web scrapper, ./spider [-rlp] URL')
    parser.add_argument('-r', action='store_true', help="Searches recursively")
    parser.add_argument('-l', type=int, default=None, action='store', help="Define the depth")
    parser.add_argument('URL', default="", action='store', help="URL to start searching")
    parser.add_argument('-p', default="./data", action='store', help="Path to store files")
    args = parser.parse_args()
    print (f"Recursion: {args.r}")
    print (f"Max Level: {args.l}")
    print (f"Path: {args.p}")
    print (f"URL: {args.URL}")

    if args.r == False and args.l != None:
        raise AssertionError("Cannot specify depth if recursion not activated")
    spidy = Spider(recursion=args.r, max_depth=args.l, image_dir=args.p, debug_data=True)
    spidy.start_scrapping(args.URL)
