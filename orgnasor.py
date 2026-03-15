import os
import glob
import time

def clean_folder(folder_path):
    images = glob.glob(os.path.join(folder_path, "*.jpg"))
    if len(images) <= 1:
        return
    # keep only the latest, delete the rest
    images.sort(key=os.path.getmtime, reverse=True)
    for old_image in images[1:]:
        os.remove(old_image)
        print(f"Deleted: {old_image}")

folder = "./parking_images"

while True:
    clean_folder(folder)
    time.sleep(1)