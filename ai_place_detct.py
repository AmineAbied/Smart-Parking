import cv2
import numpy as np

# Images
reference = cv2.imread("reference.jpg")
current = cv2.imread("current.jpg")

# Grayscale
ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
cur_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)

# Blur
ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)
cur_blur = cv2.GaussianBlur(cur_gray, (5, 5), 0)

# Absolute difference
diff = cv2.absdiff(ref_blur, cur_blur)

# Threshold the difference
_, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# Define parking spots as list of rectangles: [(x, y, w, h), ...]
parking_spots = [
    (865, 152, 183, 164),
    (887, 371, 154, 198),
    (880, 576, 154, 176),
    (881, 764, 150, 150),
    (509, 134, 174, 179),
    (705, 145, 133, 166),
    (4, 578, 156, 170),
    (14, 410, 150, 156),
]

# Check each spot
for i, (x, y, w, h) in enumerate(parking_spots):
    spot_diff = diff_thresh[y:y+h, x:x+w]
    non_zero_count = cv2.countNonZero(spot_diff)
    area = w * h

    # If difference is significant (e.g. >10% changed pixels), it's occupied
    occupancy_ratio = non_zero_count / area
    status = "Occupied" if occupancy_ratio > 0.1 else "Free"

    # Draw rectangle and label
    color = (0, 0, 255) if status == "Occupied" else (0, 255, 0)
    cv2.rectangle(current, (x, y), (x+w, y+h), color, 2)
    cv2.putText(current, f"{status}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Show result
cv2.imshow("Parking Detection", current)
cv2.waitKey(0)
cv2.destroyAllWindows()
