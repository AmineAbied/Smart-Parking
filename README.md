# 🅿️ Smart Parking Detection System

This project is a **simple smart parking system** that uses an **ESP32-CAM** to capture images of a parking lot and a **Python script (with OpenCV)** to detect which spots are occupied.

It works by comparing the current image to a reference image (with all spots empty) and detecting pixel differences to determine if a car is present.

⚠️ **Project still under development** – improvements and optimizations are ongoing.

---
**I- Requirements**

    pip install opencv-python numpy

**II- Libraries**

    import cv2
    import numpy as np

**III- Define Parking Spot**

    spot1 = (865, 152, 183, 164)
    spot2 = (887, 371, 154, 198)
    ...
We difine each spot as rectangles with *(x, y, width, height)*.

**IV- Loading Images**

    reference = cv2.imread("reference.jpg")
    current = cv2.imread("current.jpg")
*Reference :*
![reference](https://github.com/user-attachments/assets/b1552b64-85d7-4c0b-82c2-6791e1f62d4f)

*Current :*
![current](https://github.com/user-attachments/assets/95baecac-2084-4115-bade-695fe981bcb9)


**V- Convert to Grayscale**

    ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    cur_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
Grayscale conversion simplifies the image by removing colors, and reduce the anaylse time.

*Output (ref) :*
![image](https://github.com/user-attachments/assets/1e7c145d-284f-48d2-be8f-21b6a110b1e6)

*Output (curr) :*
![image](https://github.com/user-attachments/assets/2c3e0861-193e-41cb-96b0-b95269d161b1)


**VI- Gaussian Blur**

    ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)

    cur_blur = cv2.GaussianBlur(cur_gray, (5, 5), 0)
Blurring helps reduce noise and minor differences caused by lighting or shadows.

*Output (ref) :*
![image](https://github.com/user-attachments/assets/73bcf770-83e9-468b-95a1-3c82b760142b)

*Output (curr) :*
![image](https://github.com/user-attachments/assets/67f6bae5-3027-4a8d-9991-b1288007f681)

**VII- Absolute Difference**

    diff = cv2.absdiff(ref_blur, cur_blur)
We subtract the reference from the current image to highlight the changes

*Output :*
![image](https://github.com/user-attachments/assets/cefd8896-c95b-4c6b-b59f-cfb94e60b998)

**VIII-  Thresholding**

    _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
We apply a binary threshold to highlight significant differences only.

*Output :*
![image](https://github.com/user-attachments/assets/63088969-76f0-4632-89b0-2f576d94f71d)

**IX- Check Parking Spot Status**

    for i, (x, y, w, h) in enumerate(parking_spots):

      spot_diff = diff_thresh[y:y+h, x:x+w]
    
      non_zero_count = cv2.countNonZero(spot_diff)
    
      area = w * h

      occupancy_ratio = non_zero_count / area
    
      status = "Occupied" if occupancy_ratio > 0.1 else "Free"
For each defined spot:

   * We extract the region from the thresholded difference.
    
   * Count the number of white pixels (changed pixels).

   * If the change exceeds 10% of the spot area, we consider it occupied.

**X- Draw Results on the Current Image**

    color = (0, 0, 255) if status == "Occupied" else (0, 255, 0)
    cv2.rectangle(current, (x, y), (x+w, y+h), color, 2)
    cv2.putText(current, f"{status}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
* A red rectangle means the spot is occupied.

* A green rectangle means the spot is free.

**XI- Display**

    cv2.imshow("Parking Detection", current)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
Shows the final result with status over each parking spot.

*Output (final) :*
![image](https://github.com/user-attachments/assets/3374d2e4-9e3a-4b7e-8449-8db71622ea70)

