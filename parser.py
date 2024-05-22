#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import sys

filename = sys.argv[1]

file = open(filename, 'r')
data = json.loads(file.read())

for result in data['results']:
    print(f"{round(result['predicted'], 2)}")