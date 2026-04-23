import cv2
from flask import Flask, send_file
import os
import glob
import time
import threading

# ==== Parking Spots ====
spot1 = (865, 152, 183, 164)
spot2 = (887, 371, 154, 198)
spot3 = (880, 576, 154, 176)
spot4 = (881, 764, 150, 150)
spot6 = (509, 134, 174, 179)
spot5 = (705, 145, 133, 166)
spot7 = (4, 578, 156, 170)
spot8 = (14, 410, 150, 156)

parking_spots = [spot1, spot2, spot3, spot4, spot5, spot6, spot7, spot8]

# ==== Shared state ====
desired_spot   = "No SPOTS"
state_lock     = threading.Lock()
previous_image = None
OUTPUT_FOLDER  = "./free_spots_images"
OUTPUT_PATH    = os.path.join(OUTPUT_FOLDER, "annotated_output.jpg")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==== Image folder helper ====
def get_latest_image(folder_path):
    images = glob.glob(os.path.join(folder_path, "*.jpg"))
    if not images:
        return None
    return max(images, key=os.path.getmtime)

# ==== Detection ====
def analyze():
    global desired_spot

    latest    = get_latest_image("./parking_images")
    current   = cv2.imread(latest)
    reference = cv2.imread("reference.jpg")

    if current is None or reference is None:
        print("Error: could not load image(s)")
        return

    ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    cur_gray = cv2.cvtColor(current,   cv2.COLOR_BGR2GRAY)

    ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)
    cur_blur = cv2.GaussianBlur(cur_gray, (5, 5), 0)

    cur_blur = cv2.resize(cur_blur, (ref_blur.shape[1], ref_blur.shape[0]))
    current  = cv2.resize(current,  (ref_blur.shape[1], ref_blur.shape[0]))

    diff = cv2.absdiff(ref_blur, cur_blur)
    _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    free_spots = []

    for i, (x, y, w, h) in enumerate(parking_spots):
        spot_diff      = diff_thresh[y:y+h, x:x+w]
        non_zero_count = cv2.countNonZero(spot_diff)
        area           = w * h

        occupancy_ratio = non_zero_count / area
        status = "Occupied" if occupancy_ratio > 0.1 else "Free"

        if status == "Free":
            free_spots.append(i + 1)

        color = (0, 0, 255) if status == "Occupied" else (0, 255, 0)
        cv2.rectangle(current, (x, y), (x+w, y+h), color, 2)
        cv2.putText(current, status, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    print("Free parking spots:", free_spots)
    result = "No SPOTS" if not free_spots else str(min(free_spots))

    with state_lock:
        desired_spot = result
        cv2.imwrite(OUTPUT_PATH, current)

    print("Desired spot:", desired_spot)

# ==== Detection loop ====
def detection_loop():
    global previous_image
    while True:
        latest = get_latest_image("./parking_images")
        if latest and latest != previous_image:
            analyze()
            previous_image = latest
        time.sleep(0.5)

# ==== Flask server ====
app = Flask(__name__)

@app.route("/parking", methods=["GET"])
def parking():
    with state_lock:
        return desired_spot

@app.route("/parking/image", methods=["GET"])
def parking_image():
    return '''
    <html>
      <head>
        <title>Parking Detection</title>
        <meta http-equiv="refresh" content="1">
        <style>
          body { margin: 0; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; }
          img  { max-width: 100%; border: 2px solid #444; }
        </style>
      </head>
      <body>
        <img src="/parking/raw" alt="Parking Detection">
      </body>
    </html>
    '''

@app.route("/parking/raw", methods=["GET"])
def parking_raw():
    if os.path.exists(OUTPUT_PATH):
        return send_file(OUTPUT_PATH, mimetype="image/jpeg")
    return "No image yet", 404

# ==== Entry point ====
if __name__ == "__main__":
    thread = threading.Thread(target=detection_loop, daemon=True)
    thread.start()

    print("Server running on http://0.0.0.0:5000/parking")
    app.run(host="0.0.0.0", port=5000)