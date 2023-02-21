import sys

from . import cli


def main():
    return sys.exit(cli.main(prog_name="python -m audible_cli"))


if __name__ == "__main__":
    main()
