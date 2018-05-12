import argparse
import cv2
import imutils
import numpy as np

modes = ("projection", "hough")
parser = argparse.ArgumentParser(description='Fix tilted images')
parser.add_argument('-i', '--input', type=str, help='input image', required=True)
parser.add_argument('-o', '--output', type=str, help='Output image name', required=True)
parser.add_argument('-m', '--mode', type=str, help='Technique for alignment algorithm',
                    default='projection', choices=modes)

args = vars(parser.parse_args())
print(args)
INPUT = args["input"]
OUTPUT = args["output"]
MODE = args["mode"]

if not OUTPUT.endswith(".png"):
    OUTPUT = OUTPUT + ".png"

img_orig = cv2.imread(INPUT)
cv2.imshow("Original", img_orig)
img_greyscale = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
cv2.imshow("Greyscale", img_greyscale)
ret, img_bin = cv2.threshold(img_greyscale, thresh=220, maxval=1, type=cv2.THRESH_BINARY_INV)
cv2.imshow("Binary", img_bin*255)
cv2.waitKey(10000)


def func_objetivo(hist):
    pass


def projection(img):
    hists = []
    for angle in np.arange(-90, 90, 1):
        rotated = imutils.rotate_bound(img, angle)
        hists.append(np.sum(rotated, 1))

    max = 0
    idx = -91
    i = 0
    for hist in hists:
        value = func_objetivo(hist)
        if value > max:
            max = value
            idx = i
        i = i +1
        
    return idx


def hough(img):
    return 0


angle = 361
if MODE == modes[0]:  # projection
    angle = projection(img_bin)
elif MODE == modes[1]:  # hough
    angle = hough(img_greyscale)

print("Angulo de inclinação no sentido anti-horário: %d" % angle)


