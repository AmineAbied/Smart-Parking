import cv2
import os
import glob
import time
import threading
from flask import Flask, jsonify

# ==== Parking Spots ====
parking_spots = [
    (865, 152, 183, 164),  # spot 1
    (887, 371, 154, 198),  # spot 2
    (880, 576, 154, 176),  # spot 3
    (881, 764, 150, 150),  # spot 4
    (705, 145, 133, 166),  # spot 5
    (509, 134, 174, 179),  # spot 6
    (4,   578, 156, 170),  # spot 7
    (14,  410, 150, 156),  # spot 8
]

IMG_DIR      = "./parking_images"
REFERENCE    = "reference.jpg"

# ==== Shared state (updated by detection loop, read by Flask) ====
state = {
    "free_spots"   : [],
    "desired_spot" : "No SPOTS",
    "timestamp"    : 0,
}
state_lock    = threading.Lock()
previous_image = None

# ==== Image folder helper ====
def get_latest_image(folder_path):
    images = glob.glob(os.path.join(folder_path, "*.jpg"))
    if not images:
        return None
    return max(images, key=os.path.getmtime)

# ==== Core detection ====
def analyze(current_path):
    reference = cv2.imread(REFERENCE)
    current   = cv2.imread(current_path)

    if reference is None or current is None:
        print("Error: could not load image(s)")
        return

    ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    cur_gray = cv2.cvtColor(current,   cv2.COLOR_BGR2GRAY)

    ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)
    cur_blur = cv2.GaussianBlur(cur_gray, (5, 5), 0)

    cur_blur = cv2.resize(cur_blur, (ref_blur.shape[1], ref_blur.shape[0]))
    diff     = cv2.absdiff(ref_blur, cur_blur)
    _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    free_spots = []

    for i, (x, y, w, h) in enumerate(parking_spots):
        spot_diff       = diff_thresh[y:y+h, x:x+w]
        occupancy_ratio = cv2.countNonZero(spot_diff) / (w * h)
        status          = "Occupied" if occupancy_ratio > 0.1 else "Free"

        if status == "Free":
            free_spots.append(i + 1)

        color = (0, 0, 255) if status == "Occupied" else (0, 255, 0)
        cv2.rectangle(current, (x, y), (x+w, y+h), color, 2)
        cv2.putText(current, status, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    desired_spot = "No SPOTS" if not free_spots else str(min(free_spots))

    # Update shared state safely
    with state_lock:
        state["free_spots"]    = free_spots
        state["desired_spot"]  = desired_spot
        state["timestamp"]     = int(time.time())

    print(f"Free spots: {free_spots} | Desired: {desired_spot}")

# ==== Detection loop (runs in background thread) ====
def detection_loop():
    global previous_image
    while True:
        latest = get_latest_image(IMG_DIR)
        if latest and latest != previous_image:
            print(f"New image detected: {latest}")
            analyze(latest)
            previous_image = latest
        time.sleep(0.5)

# ==== Flask server ====
app = Flask(__name__)

@app.route("/parking", methods=["GET"])
def parking():
    with state_lock:
        return jsonify(state)

# ==== Entry point ====
if __name__ == "__main__":
    # Start detection loop in background
    thread = threading.Thread(target=detection_loop, daemon=True)
    thread.start()

    # Start Flask server
    print("Server running on http://0.0.0.0:5000/parking")
    app.run(host="0.0.0.0", port=5000)