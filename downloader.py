import hashlib
import os
import requests

from tqdm import tqdm


def download(url):
    print("Downloader: Downloading firmware")
    print("Downloader: Start downloading")
    r = requests.get(url, stream=True)
    with open(os.path.basename(url), 'wb') as f:
        file_size = int(r.headers["content-length"])
        chunk_size = 1000
        with tqdm(ncols=100, desc="Downloader: Fetching Firmware", total=file_size, unit_scale=True) as pbar:
            # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(chunk_size)
    print("Downloader: Download complete")


def checkHash(filename, md5sum):
    print("Hashing firmware.")
    m = hashlib.md5()
    with open(filename, "rb") as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)
    if m.hexdigest() != md5sum:
        print("Firmware hash invalid! Should be " + md5sum + ", got " + m.hexdigest())
        print("Exiting")
        exit(1)
