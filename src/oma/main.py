import sys

from oma import metaheuristica, solvers
from oma.logger import Logger


def main():
    path = "dataset/oma01.dat"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    
    logger = Logger(file_path="./logs/oma01.json")
    
    
    
    
    


if __name__ == "__main__":
    main()
