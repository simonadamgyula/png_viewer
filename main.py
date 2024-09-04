import sys
from png import PNG

def main() -> None:
    png_location = input("Input the path to the png file: ")
    png = PNG(png_location)
    png.show()

if __name__ == '__main__':
    main()
