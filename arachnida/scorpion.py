"""Display, modify or delete image metadata."""
import argparse
import os
import sys
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS


def parse_exif(img):
    exif = img.getexif()
    out = {}
    for tid, val in exif.items():
        name = TAGS.get(tid, tid)
        if name == "GPSInfo":
            val = {GPSTAGS.get(k, k): v for k, v in val.items()}
        out[name] = val
    return out


def display(path):
    print(f"\n=== {path} ===")
    if not os.path.isfile(path):
        return print("[!] File not found")
    st = os.stat(path)
    fmt = "%Y-%m-%d %H:%M:%S"
    print(f"Size:     {st.st_size} bytes")
    print(f"Created:  {datetime.fromtimestamp(st.st_ctime).strftime(fmt)}")
    print(f"Modified: {datetime.fromtimestamp(st.st_mtime).strftime(fmt)}")
    try:
        with Image.open(path) as img:
            print(f"Format:   {img.format}\nMode:     {img.mode}")
            print(f"Size:     {img.width}x{img.height}")
            exif = parse_exif(img)
    except (UnidentifiedImageError, OSError) as e:
        return print(f"[!] Cannot read image: {e}")
    if not exif:
        return print("EXIF:     (none)")
    print("EXIF:")
    for k, v in exif.items():
        s = str(v)
        print(f"  {k}: {s[:97] + '...' if len(s) > 100 else s}")


def _piexif():
    try:
        import piexif
        return piexif
    except ImportError:
        sys.exit("[!] piexif required: pip install piexif")


def delete_exif(path):
    px = _piexif()
    try:
        px.remove(path)
        print(f"[+] EXIF removed from {path}")
    except (OSError, px.InvalidImageDataError) as e:
        print(f"[!] {path}: {e}")


def modify_exif(path, changes):
    px = _piexif()
    try:
        exif = px.load(path)
        for kv in changes:
            tag, _, val = kv.partition("=")
            tid = getattr(px.ImageIFD, tag, None)
            if tid is None:
                print(f"[!] Unknown tag: {tag}")
                continue
            exif["0th"][tid] = val.encode()
        px.insert(px.dump(exif), path)
        print(f"[+] EXIF updated in {path}")
    except (OSError, px.InvalidImageDataError, ValueError) as e:
        print(f"[!] {path}: {e}")


def main():
    argv = sys.argv[1:]
    for flag in ("-m", "--modify"):
        if flag in argv and not any(
                not a.startswith("-") for a in argv[:argv.index(flag)]):
            sys.exit("[!] FILE(s) must come BEFORE -m\n"
                     "    Correct: scorpion.py file.jpg -m Make=Sony")
    p = argparse.ArgumentParser(
        description=__doc__,
        usage="%(prog)s FILE [FILE ...] [-d | -m TAG=VALUE ...]")
    p.add_argument("files", nargs="+")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-d", "--delete", action="store_true")
    g.add_argument("-m", "--modify", nargs="+", metavar="TAG=VALUE")
    a = p.parse_args()
    for f in a.files:
        (delete_exif if a.delete else
         (lambda f: modify_exif(f, a.modify)) if a.modify else display)(f)


if __name__ == "__main__":
    main()
