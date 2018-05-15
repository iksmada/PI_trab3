import argparse
import cv2
import imutils
import numpy as np


def centered_crop(img, new_height, new_width):
    width = np.size(img, 1)
    height = np.size(img, 0)

    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = (width + new_width) // 2
    bottom = (height + new_height) // 2
    c_img = img[top:bottom, left:right, :]
    return c_img


def func_objetivo_projection(hist):
    return max(hist)


def projection(img):
    hists = []
    for theta in np.arange(-90, 90, 1):
        rotated = imutils.rotate_bound(img, -theta)
        hists.append(np.sum(rotated, 1))

    max = -1
    theta = -91
    i = -90
    for hist in hists:
        value = func_objetivo_projection(hist)
        if value > max:
            max = value
            theta = i
        i = i + 1

    return theta


def hough_transform(x, y):
    points = []
    for theta in np.arange(-90, 90, 1):
        points.append((int(x*np.cos(np.radians(theta)) + y*np.sin(np.radians(theta)) + 0.5), theta))
    return points


def func_objetivo_hough(accumulator):
    rows, cols = np.where(accumulator == accumulator.max())
    return cols[0]


def hough(img):
    accumulator = np.zeros((int(img.shape[0]*1.415 + img.shape[1]*1.415 + 0.5), 180), int)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y, x] > 0:
                for point in hough_transform(x, y):
                    accumulator[point] = accumulator[point] + 1

    angle = func_objetivo_hough(accumulator) - 90

    return angle


modes = ("projection", "hough")
parser = argparse.ArgumentParser(description='Fix tilted images')
parser.add_argument('-i', '--input', type=str, help='input image', required=True)
parser.add_argument('-o', '--output', type=str, help='Output image name')
parser.add_argument('-m', '--mode', type=str, help='Technique for alignment algorithm',
                    default='projection', choices=modes)

args = vars(parser.parse_args())
print(args)
INPUT = args["input"]
OUTPUT = args["output"]
MODE = args["mode"]

if OUTPUT and not OUTPUT.endswith(".png"):
    OUTPUT = OUTPUT + ".png"

img_orig = cv2.imread(INPUT)
cv2.imshow("Original", img_orig)
if img_orig.shape[0] > 500 or img_orig.shape[1] > 500:
    img_cropped = centered_crop(img_orig, 500, 500)
else:
    img_cropped = img_orig
img_greyscale = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
cv2.imshow("Greyscale And Cropped", img_greyscale)
ret, img_bin = cv2.threshold(img_greyscale, 220, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
cv2.imshow("Binary", img_bin)
cv2.waitKey(10000)
cv2.destroyAllWindows()


angle = 361
if MODE == modes[0]:  # projection
    angle = projection(img_bin)
elif MODE == modes[1]:  # hough
    angle = hough(img_bin)

if angle >= 0:
    print("Inclinação de %d° no sentido horário" % angle)
else:
    print("Inclinação de %d° no sentido anti-horário" % (-angle))
rotated = imutils.rotate(img_orig, angle)
cv2.imshow("Rotated", rotated)
if OUTPUT:
    cv2.imwrite(OUTPUT, rotated)
cv2.waitKey(0)


