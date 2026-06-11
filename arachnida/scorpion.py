import os
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS
import piexif
import argparse

# efix = id: value  ==> 271: "Make"
# mais GPS a  {1: 'N', 2: ((48, 1), (51, 1), (2800, 100)), 3: 'E', ...


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
    try:
        with Image.open(image) as img:
            print(f"Format:   {img.format}")
            print(f"Mode:     {img.mode}")
            print(f"Size:     {img.width}x{img.height}")
            exif_dict = parse_exif(img)
    except (UnidentifiedImageError, OSError) as error:
        return print(f"error : Cannot read image: {error}")

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


if __name__ == "__main__":
    args = get_args()
    for image in args.images:
        if args.modify:
            modify_exif(image, args.modify)
        elif args.delete:
            delete_exif(image)
        else:
            display_exif(image)
