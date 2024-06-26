import sys
from png import PNG

def main() -> None:
    png = PNG("input.png")
    png.check()

if __name__ == '__main__':
    main()