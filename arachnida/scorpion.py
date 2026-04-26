import argparse
import os
import sys
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS


# deux dico avec les value des tags
def parse_exif(image):
    raw_exif = image.getexif()
    exif_dict = {}
    for tag_id, value in raw_exif.items():
        tag_name = TAGS.get(tag_id)
        # si gps info cas spécial on cherche dans gps dico
        if tag_name == "GPSInfo":
            value = {GPSTAGS.get(gps_id): v for gps_id, v in value.items()}
        exif_dict[tag_name] = value
    return exif_dict


def display(file):
    print(f"\n=== {file} ===")
    if not os.path.isfile(file):
        return print("error : File not found")

    # os stat meta donné de base
    file_stat = os.stat(file)
    date_format = "%Y-%m-%d %H:%M:%S"
    created = datetime.fromtimestamp(file_stat.st_ctime).strftime(date_format)
    modified = datetime.fromtimestamp(file_stat.st_mtime).strftime(date_format)
    print(f"Size:     {file_stat.st_size} bytes")
    print(f"Created:  {created}")
    print(f"Modified: {modified}")

    try:
        with Image.open(file) as image:
            print(f"Format:   {image.format}")
            print(f"Mode:     {image.mode}")
            print(f"Size:     {image.width}x{image.height}")
            exif_dict = parse_exif(image)
    except (UnidentifiedImageError, OSError) as error:
        return print(f"error : Cannot read image: {error}")

    if not exif_dict:
        return print("EXIF:     (none)")

    print("EXIF:")
    for tag_name, value in exif_dict.items():
        # value en string + ... si longue
        value_str = str(value)
        if len(value_str) > 100:
            value_str = value_str[:97] + "..."
        print(f"  {tag_name}: {value_str}")


# lazy export pour catch si la piexit pas installé au lieu de crash
def _piexif():
    try:
        import piexif
        return piexif
    except ImportError:
        sys.exit("error :  piexif required: pip install piexif")


def delete_exif(img):
    px = _piexif()
    try:
        px.remove(img)
        print(f"[-] EXIF removed from {img}")
    except (OSError, px.InvalidImageDataError) as e:
        print(f"error :  {img}: {e}")


def modify_exif(img, changes):
    piexif = _piexif()
    try:
        exif_data = piexif.load(img)
        for change in changes:
            tag_name, _, new_value = change.partition("=")
            # renvoit un tuple avec les 3 partie
            #  le tag le = et la value stock dans 3 var
            tag_id = getattr(piexif.ImageIFD, tag_name, None)
            # classe qui contient les id de tous les exifs
            # piexif.ImageIFD.Make            # 271
            # piexif.ImageIFD.Model           # 272
            if tag_id is None:
                print(f"error : Unknown tag: {tag_name}")
                continue
            # 0th block exif principal
            exif_data["0th"][tag_id] = new_value.encode()
            # encode convertit en byte comme le veut piexif
        piexif.insert(piexif.dump(exif_data), img)
        # dump met en byte (format pour images)
        # inset met dans l'image
        print(f"[+] EXIF updated in {img}")
    except (OSError, piexif.InvalidImageDataError, ValueError) as e:
        print(f"error : {img}: {e}")


def main():
    argv = sys.argv[1:]
    # flags == m puis modify
    for flag in ("-m", "--modify"):
        if flag not in argv:
            continue
        # si flag present check si y'a mot avant le -m qui serait sans -
        # donc qui serait un fichier
        before = argv[:argv.index(flag)]
        has_file = any(not a.startswith("-") for a in before)
        if not has_file:
            sys.exit("error :  FILE(s) must come BEFORE -m\n"
                     "    Correct: scorpion.py file.jpg -m Make=Sony")

    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    # cree groupe dans le parser de flag qui sont mutuellement exclusif
    g = p.add_mutually_exclusive_group()
    g.add_argument("-d", "--delete", action="store_true")
    g.add_argument("-m", "--modify", nargs="+")
    args = p.parse_args()

    for file in args.files:
        if args.delete:
            delete_exif(file)
        elif args.modify:
            modify_exif(file, args.modify)
        else:
            display(file)


if __name__ == "__main__":
    main()
