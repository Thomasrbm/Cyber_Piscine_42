import argparse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
visited = set()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-r", action="store_true")
    parser.add_argument("-l", type=int, default=5)
    parser.add_argument("-p", default="./data/")
    return parser.parse_args()


def download_image(img_url, save_file_path):
    try:
        # requete get pour l'image
        r = requests.get(img_url, timeout=5)
        r.raise_for_status()
        # r.content a les bytes de l img
        filename = os.path.basename(urlparse(img_url).path)
        # avec url de l'image url parse stock dans une PArse result
        # chaque partie de l'url, dont une qui est path = /photos/cat.png
        # base name prend le bout apres le dernie / donc ici cat.png
        if not filename:
            return
        filepath = os.path.join(save_file_path, filename)
        # met le fichier dans le bon dossier save
        with open(filepath, "wb") as f:
            f.write(r.content)
        # on écrit les byte de l'image dans le fichier dest
        print(f"[+] {img_url}")
    except Exception as e:
        print(f"[-] {img_url}: {e}")


def scrape_page(url, save_file_path):
    os.makedirs(save_file_path, exist_ok=True)  # reécré pas si existe deja
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()  # leve une exception si rep d error
    except Exception as e:
        print(f"[-] Can't fetch {url}: {e}")
        return
    soup = BeautifulSoup(r.text, "html.parser")
    #  r.text = body; stock l'arbre
    for img in soup.find_all("img"):
        # img = objet tag qui contient nom : div, a, img
        # attribut src, alt, class
        # les sous balises enfants, ref au parent etc
        src = img.get("src")
        # pour toutes les lignes avec img, on get la src (irl de l'img)
        if not src:
            continue
        full_url = urljoin(url, src)
        # reconstruit url de la page + url de l'image
        if full_url.lower().endswith(EXTENSIONS):
            download_image(full_url, save_file_path)


def crawl(url, save_file_path, depth, max_depth, base_domain):
    if depth > max_depth or url in visited:
        return
    visited.add(url)
    print(f"[depth {depth}] {url}")
    scrape_page(url, save_file_path)
    if depth == max_depth:
        return
    # va try toutes les sous page de la page courrante
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        # cherche les "a = ancre" balise lien
        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            if urlparse(next_url).netloc == base_domain:
                crawl(next_url, save_file_path, depth + 1, max_depth,
                      base_domain)
    except Exception as e:
        print(f"[-] Crawl error on {url}: {e}")


if __name__ == "__main__":
    args = parse_args()
    max_depth = args.l if args.r else 0
    base_domain = urlparse(args.url).netloc
    start_depth = 0
    crawl(args.url, args.p, start_depth, max_depth, base_domain)
