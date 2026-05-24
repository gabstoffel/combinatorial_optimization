import sys

from oma.instance import load
from oma.logger import Logger


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "dataset/oma01.dat"
    instance = load(path)
    logger = Logger(stderr=True)
    logger.info("instance_loaded", {"file": path, "n": instance.n, "m": instance.m})


if __name__ == "__main__":
    main()
