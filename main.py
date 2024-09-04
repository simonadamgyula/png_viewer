import sys
from png import PNG

def main() -> None:
    png_location = input("Input the path to the png file (C:/path/to/image.png): ")
    png = PNG(png_location)
    png.show()

if __name__ == '__main__':
    main()
