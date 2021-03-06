import argparse
import cv2
import imutils
import numpy as np

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract


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
    for theta in np.arange(0, 180, 1):
        points.append((int(x*np.cos(np.radians(theta)) + y*np.sin(np.radians(theta)) + 0.5), theta))
    return points


def func_objetivo_hough(accumulator):
    rows, cols = np.where(accumulator == accumulator.max())
    return cols[0]


def hough(img):
    accumulator = np.zeros((int(img.shape[0]*1.415 + img.shape[1]*1.415 + 0.5), 180), int)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y, x] > 10:
                for point in hough_transform(x, y):
                    accumulator[point] = accumulator[point] + 1
    # plt.matshow(accumulator[:400,:])
    # plt.show()
    angle = func_objetivo_hough(accumulator) - 90

    return angle


def extract_contours(img):
    image, contours, hierarchy = cv2.findContours(img, 1, 2)
    total_area = img.shape[0]*img.shape[1]
    img_ret = img
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > total_area/2:
            stencil0 = np.zeros(img.shape).astype(img.dtype)
            cv2.fillConvexPoly(stencil0, cnt, 255)
            img_ret = cv2.bitwise_and(img_ret, stencil0)
        elif area > 2000:
            stencil255 = np.ones(img.shape).astype(img.dtype) * 255
            cv2.fillConvexPoly(stencil255, cnt, 0)
            img_ret = cv2.bitwise_and(img_ret, stencil255)

    return img_ret


modes = ("projection", "hough")
pre = ("crop", "sobel", "otsu", "contours", "gray")
parser = argparse.ArgumentParser(description='Fix tilted images')
parser.add_argument('-i', '--input', type=str, help='Input image path', required=True)
parser.add_argument('-o', '--output', type=str, help='Output image path')
parser.add_argument('-m', '--mode', type=str, help='Technique for alignment algorithm',
                    default='projection', choices=modes)
parser.add_argument('-p', '--pre', type=str, help='Technique for preprocessing',default='gray', choices=pre, nargs="*")
parser.add_argument('-c', '--crop', type=int, help='Crop window size', default=500)

args = vars(parser.parse_args())
INPUT = args["input"]
OUTPUT = args["output"]
MODE = args["mode"]
PRE = args["pre"]
CROP = args["crop"]

if OUTPUT and not OUTPUT.endswith(".png"):
    OUTPUT = OUTPUT + ".png"

img_orig = cv2.imread(INPUT)
cv2.imshow("Original", img_orig)

text = pytesseract.image_to_string(img_orig)
print("Texto antes da rotação:")
print(text)

img_out = img_orig

if pre[0] in PRE and (img_orig.shape[0] > CROP or img_orig.shape[1] > CROP):
        img_out = centered_crop(img_out, CROP, CROP)
        cv2.imshow("Cropped", img_out)

if pre[1] in PRE:  # sobel
    # Output dtype = cv2.CV_64F. Then take its absolute and convert to cv2.CV_8U
    sobelx64f = cv2.Sobel(img_out, cv2.CV_64F, 1, 1, ksize=3)
    abs_sobel64f = np.absolute(sobelx64f)
    img_out = np.uint8(abs_sobel64f)
    cv2.imshow("Sobel Filter", img_out)

img_out = cv2.cvtColor(img_out, cv2.COLOR_BGR2GRAY)

if pre[2] in PRE:  # otsu
    ret, img_out = cv2.threshold(img_out, 220, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cv2.imshow("Binary", img_out)

if pre[3] in PRE:
    img_out = extract_contours(img_out)
    cv2.imshow("Remove Contour", img_out)

cv2.waitKey(20000)
cv2.destroyAllWindows()


angle = 361
if MODE == modes[0]:  # projection
    angle = projection(img_out)
elif MODE == modes[1]:  # hough
    angle = hough(img_out)

rotated = imutils.rotate(img_orig, angle)
cv2.imshow("Rotated", rotated)

text = pytesseract.image_to_string(rotated)
print("Texto apos da rotação:")
print(text)

if angle >= 0:
    print("Inclinação de %d° no sentido horário" % angle)
else:
    print("Inclinação de %d° no sentido anti-horário" % (-angle))


if OUTPUT:
    cv2.imwrite(OUTPUT, rotated)
cv2.waitKey(0)


