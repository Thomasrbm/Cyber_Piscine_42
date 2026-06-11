import os
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS
import piexif
import argparse
import sys

# efix = id: value  ==> 271: "Make"
# mais GPS a  {1: 'N', 2: ((48, 1), (51, 1), (2800, 100)), 3: 'E', ...}


<<<<<<< HEAD
=======
# deux dico avec les value des tags
# lit exif de l image et renvoit un dico
>>>>>>> refs/remotes/origin/main
def parse_exif(image):
    exif = image.getexif()  # renvoit classe qui comporte comme dico
    exif_dic = {}
    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id)
        if tag_name == "GPSInfo":
            gps_dict = {}
            for gps_id, val in value.items():
                gps_name = GPSTAGS.get(gps_id)
                gps_dict[gps_name] = val
            value = gps_dict
        exif_dic[tag_name] = value
    return exif_dic

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

<<<<<<< HEAD
def modify_exif(image, changes):
    try:
        exif_data = piexif.load(image)
        for change in changes:
            tag_name, _, new_value = change.partition("=")
            tag_id = getattr(piexif.ImageIFD, tag_name, None)
            # cherche l attribue dans tag_id
            if tag_id is None:
                print(f"error : Unknown tag: {tag_name}")
                continue
            exif_data["0th"][tag_id] = new_value.encode()
            # ranger au block 0 a l id met la new value
        piexif.insert(piexif.dump(exif_data), image)
        # dump met en binaire. insert dans l image l exif
        print(f"[+] EXIF updated in {image}")
    except (OSError, piexif.InvalidImageDataError, ValueError) as e:
        print(f"error : {image}: {e}")


def delete_exif(image):
    try:
        piexif.remove(image)
        print(f"[-] EXIF removed from {image}")
    except (OSError, piexif.InvalidImageDataError) as e:
        print(f"error :  {image}: {e}")


def display_exif(image):
    print(f"\n==={image}===")
    if not os.path.isfile(image):
        return print("error : File not found")

=======

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

>>>>>>> refs/remotes/origin/main
    try:
        with Image.open(image) as img:
            print(f"Format:   {img.format}")
            print(f"Mode:     {img.mode}")
            print(f"Size:     {img.width}x{img.height}")
            exif_dict = parse_exif(img)
    except (UnidentifiedImageError, OSError) as error:
        return print(f"error : Cannot read image: {error}")

<<<<<<< HEAD
    if not exif_dict:
        return print("EXIF:     (none)")

    print("EXIF:")
    for tag_name, value in exif_dict.items():
        print(f"  {tag_name}: {value}")


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("images", nargs="+")

    g = p.add_mutually_exclusive_group()
    g.add_argument("-m", "--modify", nargs="+")
    g.add_argument("-d", "--delete", action="store_true")
    return p.parse_args()
=======
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
>>>>>>> refs/remotes/origin/main


if __name__ == "__main__":
    args = get_args()
    for image in args.images:
        if args.modify:
            modify_exif(image, args.modify)
        elif args.delete:
            delete_exif(image)
        else:
            display_exif(image)
