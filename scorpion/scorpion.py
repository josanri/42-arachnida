import exifread
import sys
import os
import datetime
from PIL import Image
from PIL.ExifTags import TAGS

def get_extension(image_url:str):
    if image_url.rfind('.') != -1:
        return image_url[image_url.rfind('.')::]
    return ""

def getTimesOfFile(file_path:str):
    print('Created on:', datetime.datetime.fromtimestamp(os.path.getctime(file_path)))
    print('Modified on:', datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
    print('Last access on:', datetime.datetime.fromtimestamp(os.path.getatime(file_path)))
    print('Bytes size:', os.path.getsize(file_path))

def scorpion(file_path:str) :
    getTimesOfFile(file_path)
    if get_extension(file_path) == ".gif":
        print("EXIF data is not supported on .gif files")
        return
    elif get_extension(file_path) in (".png", ".jpeg"):
        f = open(file_path, 'rb')
        tags = exifread.process_file(f)
        for tag in tags.keys():
            print(f"{tag:25}: {tags[tag]}")
        f.close()
    elif get_extension(file_path) in (".jpg", ".bmp"):
        image_open = Image.open(file_path)
        exif_data = image_open.getexif()
        for tag_id in exif_data:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            print(f"{tag:25}: {data}")
        image_open.close()
        

if __name__ == '__main__':
    # Return Exif tags
    assert len(sys.argv) > 1, "One or more files"
    for filename in sys.argv[1:]:
        try:
            print(f"Decoding {filename}")
            scorpion(filename)
            print()
        except Exception:
            print(f"Error while opening {filename}")