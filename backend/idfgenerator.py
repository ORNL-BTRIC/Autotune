#!/usr/bin/env python
import argparse
import os
import re
import sys
sys.path.append(os.getcwd())
import generation
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonparams')
    args, unknown = parser.parse_known_args()
    j = args.jsonparams
    j = j.replace('\'', '"')
    idf_file = generation.generate_idf_string(j)
    print(idf_file)

    
if __name__ == '__main__':
    main()