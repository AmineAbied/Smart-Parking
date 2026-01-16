import cv2
import os
import time
from flask import Flask

# Folder where images are synced
folder_path = "/Documents/smart_parking/Smart-Parking2026/Smart-Parking"  # <-- replace with your synced folder
check_interval = 1  # seconds to wait before checking for a new image

# Parking spots coordinates
parking_spots = [
    (865, 152, 183, 164),
    (887, 371, 154, 198),
    (880, 576, 154, 176),
    (881, 764, 150, 150),
    (705, 145, 133, 166),
    (509, 134, 174, 179),
    (4, 578, 156, 170),
    (14, 410, 150, 156)
]

# Reference image
reference = cv2.imread("reference.jpg")
ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)

# Flask app
app = Flask(__name__)
desired_spot = "None"  # default if no free spot

def get_latest_image(folder):
    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not images:
        return None
    return max(images, key=os.path.getmtime)

def detect_parking(image_path):
    global desired_spot

    current = cv2.imread(image_path)
    cur_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    cur_blur = cv2.GaussianBlur(cur_gray, (5, 5), 0)

    diff = cv2.absdiff(ref_blur, cur_blur)
    _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    free_spots = []

    for i, (x, y, w, h) in enumerate(parking_spots):
        spot_diff = diff_thresh[y:y+h, x:x+w]
        non_zero_count = cv2.countNonZero(spot_diff)
        area = w * h

        occupancy_ratio = non_zero_count / area
        status = "Occupied" if occupancy_ratio > 0.1 else "Free"

        if status == "Free":
            free_spots.append(i + 1)

        color = (0, 0, 255) if status == "Occupied" else (0, 255, 0)
        cv2.rectangle(current, (x, y), (x+w, y+h), color, 2)
        cv2.putText(current, f"{status}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    print("Free parking spots: ", free_spots)
    if free_spots:
        desired_spot = str(min(free_spots))
    else:
        desired_spot = "None"

    print("Desired spot:", desired_spot)

    cv2.imshow("Parking Detection", current)
    cv2.waitKey(1)  # non-blocking display

@app.route("/parking", methods=["GET"])
def parking():
    return desired_spot

if __name__ == "__main__":
    import threading

    # Run Flask in a separate thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)).start()

    print("Monitoring folder for new images...")
    last_processed = None

    while True:
        latest_image = get_latest_image(folder_path)
        if latest_image is not None and latest_image != last_processed:
            detect_parking(latest_image)
            last_processed = latest_image
        time.sleep(check_interval)
