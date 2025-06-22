import cv2
import numpy as np

img1 = cv2.imread("reference.jpg")
img2 = cv2.imread("current.jpg")

img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

img1_blur = cv2.GaussianBlur(img1_gray, (5, 5), 0)
img2_blur = cv2.GaussianBlur(img2_gray, (5, 5), 0)

diff = cv2.absdiff(img1_blur, img2_blur)

cv2.imshow("Phase de test :", diff)
cv2.waitKey(0)
cv2.destroyAllWindows()