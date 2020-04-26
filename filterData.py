import sys
from WvLibs import WVdataIter, ReaderPostProcessor
import re
import json

raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]
new_json_file = sys.argv[3]

dataIter = WVdataIter(annoed_json_dir, raw_json_file, min_anno_filter=1)
filtered_data = []
for item in dataIter:
    redo = False
    for annotation in item['annotations']:
        label = annotation['label']
        if label == 'SocAlrm':
            redo = True
    if redo:
        del item['annotations']
        filtered_data.append(item)

print(len(filtered_data))

with open(new_json_file, 'w') as fj:
    json.dump(filtered_data, fj)
