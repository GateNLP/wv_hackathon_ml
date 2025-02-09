import sys
from WvLibs import WVdataIter, ReaderPostProcessor
import re

raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]
tsv_file = sys.argv[3]

dataIter = WVdataIter(annoed_json_dir, raw_json_file, min_anno_filter=1)
#for item in dataIter:
#    print(item)

with open(tsv_file, 'w') as fo:
    outline = 'link\tclaim\texplaination\tlabel1\tconfident1\tannotator1\tlabel2\tconfident2\tannotator2\tlabel3\tconfident3\tannotator3\n'
    fo.write(outline)
    for item in dataIter:
        claim = item['Claim'].strip()
        claim = claim.replace('\t','')
        explaination = item['Explaination'].strip()
        explaination = explaination.replace('\t','')
        link = item['Link'].strip()
        line = link.replace('\t','')
        outline = link+'\t'+claim+'\t'+explaination
        for annotation in item['annotations']:
            print(annotation)
            label = annotation['label']
            confident = annotation['confident']
            annotator = annotation['annotator']
            outline += '\t'+label+'\t'+confident+'\t'+annotator
        outline += '\n'
        fo.write(outline)

