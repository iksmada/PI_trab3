import argparse
import cv2

modes = ("projection", "hough")
parser = argparse.ArgumentParser(description='Fix tilted images')
parser.add_argument('-i', '--input', type=int, help='input image', required=True)
parser.add_argument('-o', '--output', type=int, help='Output image name', required=True)
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
img_greyscale = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)


def projection(img):
    return 0


def hough(img):
    return 0


angle = 361
if MODE == modes[0]:
    angle = projection(img_greyscale)
elif MODE == modes[1]:
    angle = hough(img_greyscale)

print("Angulo de inclinação no sentido anti-horário: %d" % angle)


