import cv2
import numpy as np

# Load the two images
image1 = cv2.imread("out/dopo_frame_100.jpg")
image2 = cv2.imread("out/prima_frame_100.jpg")

# Convert the images to grayscale
gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

# Compute the absolute difference between the grayscale images
diff = cv2.absdiff(gray1, gray2)

cv2.imwrite(f'out/diff.jpg', diff)

"""
# Apply thresholding to the difference image
thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Find contours in the thresholded image
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# Loop over the contours and draw bounding boxes around the differences
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.rectangle(image2, (x, y), (x + w, y + h), (0, 0, 255), 2)

# Save the images with highlighted differences
#cv2.imshow("Image 1", image1)
#cv2.imshow("Image 2", image2)
#cv2.waitKey(0)
"""