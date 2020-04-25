import sys
from WvLibs import WVdataIter, ReaderPostProcessor
import re

raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]
tsv_file = sys.argv[3]

dataIter = WVdataIter(annoed_json_dir, raw_json_file, min_anno_filter=2)

with open(tsv_file, 'w') as fo:
    outline = 'link\tclaim\texplaination\tlabel1\tconfident1\tannotator1\tlabel2\tconfident2\tannotator2\tlabel3\tconfident3\tannotator3\n'
    fo.write(outline)
    t=0
    a=0
    for item in dataIter:
        #t+=1
        claim = item['Claim'].strip()
        claim = claim.replace('\t','')
        explaination = item['Explaination'].strip()
        explaination = explaination.replace('\t','')
        link = item['Link'].strip()
        line = link.replace('\t','')
        outline = link+'\t'+claim+'\t'+explaination
        label1 = item['annotations'][0]['label']
        label2 = item['annotations'][1]['label']
        annotator1 = item['annotations'][0]['annotator']
        annotator2 = item['annotations'][1]['annotator']
        if annotator1 != annotator2:
            t+=1
        if label1 == label2:
            a += 1
        for annotation in item['annotations']:
            print(annotation)
            label = annotation['label']
            confident = annotation['confident']
            annotator = annotation['annotator']
            outline += '\t'+label+'\t'+confident+'\t'+annotator
        outline += '\n'
        fo.write(outline)


pa = a/t
pe = 1/12

k = (pa-pe)/(1-pe)
print(t)
print(pa)
print(k)

