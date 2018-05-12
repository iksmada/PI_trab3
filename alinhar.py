import argparse


parser = argparse.ArgumentParser(description='Fix tilted images')
parser.add_argument('-i', '--input', type=int, help='input image', required=True)
parser.add_argument('-o', '--output', type=int, help='Output image name', required=True)
parser.add_argument('-m', '--mode', type=str, help='Technique for alignment algorithm',
                    default='projection', choices=("projection", "hough"))

args = vars(parser.parse_args())
print(args)
INPUT = args["input"]
OUTPUT = args["output"]
MODE = args["mode"]

if not OUTPUT.endswith(".png"):
    OUTPUT = OUTPUT + ".png"



