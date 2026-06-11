import argparse
import os
import sys
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS


# deux dico avec les value des tags
# lit exif de l image et renvoit un dico
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

# affiche le dico de l image (donc son exif)
def print_exif(exif_dict):
    if not exif_dict:
        return print("EXIF:     (none)")
    print("EXIF:")
    for tag_name, value in exif_dict.items():
        # value en string, tronquée si trop longue
        value_str = str(value)
        if len(value_str) > 100:
            value_str = value_str[:97] + "..."
        print(f"  {tag_name}: {value_str}")


# rend propre l affichage avec infos en plus sur l image
def display(file):
    print(f"\n=== {file} ===")
    if not os.path.isfile(file):
        return print("error : File not found")

    # os.stat : metadonnées de base du fichier
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

    print_exif(exif_dict)


# lazy export pour catch si la piexit pas installé au lieu de crash
def _piexif():
    try:
        import piexif
        return piexif
    except ImportError:
        sys.exit("error :  piexif required: pip install piexif")


def delete_exif(img):
    piexif = _piexif()
    try:
        piexif.remove(img)
        print(f"[-] EXIF removed from {img}")
    except (OSError, piexif.InvalidImageDataError) as e:
        print(f"error :  {img}: {e}")


# chaque image a son dico, on reecrase le dico a chaque fois
def modify_exif(img, changes):
    piexif = _piexif()
    try:
        exif_data = piexif.load(img)
        for change in changes:
            # "Make=Sony" -> tag_name="Make", new_value="Sony"
            tag_name, _, new_value = change.partition("=")
            # ImageIFD donne l'id numerique du tag (ex: Make -> 271)
            tag_id = getattr(piexif.ImageIFD, tag_name, None)
            if tag_id is None:
                print(f"error : Unknown tag: {tag_name}")
                continue
            # piexif range les exif par section : "0th" (image principale),
            # "Exif", "GPS"... Make/Model sont dans "0th". encode() car
            # piexif stocke les valeurs en bytes, pas en str.
            exif_data["0th"][tag_id] = new_value.encode()
        # dump() reserialise tout le dico en bloc exif (bytes),
        # insert() reecrit ce bloc dans le fichier image sur le disque.
        piexif.insert(piexif.dump(exif_data), img)
        print(f"[+] EXIF updated in {img}")
    except (OSError, piexif.InvalidImageDataError, ValueError) as e:
        # OSError : fichier introuvable ou illisible/non inscriptible.
        # InvalidImageDataError : pas un jpeg/tiff valide (piexif ne gere
        #   que ces formats), ou image sans exif exploitable.
        # ValueError : valeur incompatible avec le type attendu du tag
        #   (leve par dump()).
        print(f"error : {img}: {e}")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    # groupe de flags mutuellement exclusifs : soit -d soit -m
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--delete", action="store_true")
    # un -m par tag a modifier : -m Make=Sony -m Model=X
    group.add_argument("-m", "--modify", action="append", default=[])
    return parser.parse_args()


def main():
    args = get_args()
    for file in args.files:
        if args.delete:
            delete_exif(file)
        elif args.modify:
            modify_exif(file, args.modify)
        else:
            display(file)


if __name__ == "__main__":
    main()
