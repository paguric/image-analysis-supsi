import cv2
import numpy as np

"""
Autore: Lapo

Ho usato questo file per testare brevemente:
  - Image Registration (allineamento)
  - Mappa differenziale

Lo lascio in questo stato "grezzo" perchè ancora dobbiamo definir
se allineamento e mappa differenziale possono tornarci utili

Link al codice usato per Image Registration
> https://www.geeksforgeeks.org/python/image-registration-using-opencv-python/

Link al codice usato per mappa differenziale
> https://nulldog.com/opencv-image-difference-detection-and-visualization

Input:
  - out/dopo_frame_100.jpg
  - out/prima_frame_100.jpg

Output:
- out/diff.jpg
- out/gray1.jpg
"""

# Load the two images
image1 = cv2.imread("out/dopo_frame_100.jpg")
image2 = cv2.imread("out/prima_frame_100.jpg")

# Convert the images to grayscale
gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
height, width = gray2.shape

# Create ORB detector with 5000 features.
orb_detector = cv2.ORB_create(5000)

# Find keypoints and descriptors.
# The first arg is the image, second arg is the mask
#  (which is not required in this case).
kp1, d1 = orb_detector.detectAndCompute(gray1, None)
kp2, d2 = orb_detector.detectAndCompute(gray2, None)

# Match features between the two images.
# We create a Brute Force matcher with 
# Hamming distance as measurement mode.
matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

# Match the two sets of descriptors.
matches = matcher.match(d1, d2)

# Sort matches on the basis of their Hamming distance.
matches = sorted(matches, key = lambda x: x.distance)

# Take the top 90 % matches forward.
matches = matches[:int(len(matches)*0.9)]
no_of_matches = len(matches)

# Define empty matrices of shape no_of_matches * 2.
p1 = np.zeros((no_of_matches, 2))
p2 = np.zeros((no_of_matches, 2))

for i in range(len(matches)):
  p1[i, :] = kp1[matches[i].queryIdx].pt
  p2[i, :] = kp2[matches[i].trainIdx].pt

# Find the homography matrix.
homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)

# Use this matrix to transform the
# colored image wrt the reference image.
gray1 = cv2.warpPerspective(gray1,
                    homography, (width, height))

# ------------------------------------------------------------------------------------
# Compute the absolute difference between the grayscale images
diff = cv2.absdiff(gray1, gray2)

cv2.imwrite(f'out/diff.jpg', diff)
cv2.imwrite(f'out/gray1.jpg', gray1)
cv2.imwrite(f'out/gray2.jpg', gray2)
