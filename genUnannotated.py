import sys
import json
from WvLibs import WVdataIter, ReaderPostProcessor
import re
from itertools import combinations
import argparse


def solve_disagreement(annotations):
    reanno = False
    annotation_list = []
    label_list = []
    for annotation in annotations:
        label = annotation['label']
        confident = annotation['confident']
        annotator = annotation['annotator']
        annotation_list.append([label, confident, annotator])
        label_list.append(label)

    label_set = list(set(label_list))
    set_count = [0]*len(label_set)

    for idx, current_label in enumerate(label_set):
        set_count[idx] = label_list.count(current_label)
    sorted_count = sorted(set_count, reverse=True)
    if len(label_set) == 1:
        selected_label = label_set[0]
    elif sorted_count[0] > sorted_count[1]:
        selected_label_idx = set_count.index(sorted_count[0])
        selected_label = label_set[selected_label_idx]
    else:
        reanno = True

    if reanno:
        print(annotation_list)
    return reanno


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_json_file", help="Unannotated Json file")
    parser.add_argument("annoed_json_dir", help="Annotated Json file dir")
    parser.add_argument("annoed_tsv", help="output for annoed tsv")
    parser.add_argument("json_file", help="json file to output")
    parser.add_argument("--ignoreLabel", help="ignore label")
    parser.add_argument("--ignoreUser", help="ignore user")
    parser.add_argument("--min_anno_filter", type=int, default=-1, help="min frequence")
    parser.add_argument("--conf_thres", type=int, default=-1, help="confident threshold")
    args = parser.parse_args()


    raw_json_file = args.raw_json_file
    annoed_json_dir = args.annoed_json_dir
    tsv_file = args.annoed_tsv
    new_json_file = args.json_file
    user2ignor = []
    list2ignor = []

    if args.ignoreLabel:
        list2ignor = args.ignoreLabel.split(',')

    if args.ignoreUser:
        user2ignor = args.ignoreUser.split(',')


    dataIter = WVdataIter(annoed_json_dir, raw_json_file, check_validation=False, ignoreLabelList=list2ignor, ignoreUserList=user2ignor)
    t = 0
    i = 0
    gotoAnno = []
    with open(tsv_file, 'w') as fo:
        outline = 'id\tclaim\texplaination\tlabel1\tconfident1\tannotator1\tlabel2\tconfident2\tannotator2\tlabel3\tconfident3\tannotator3\n'
        fo.write(outline)
        for item in dataIter:
            t += 1
            if len(item['annotations']) == 0:
                #gotoAnno.append(item)
                pass
            elif len(item['annotations']) == 1:
                annotation = item['annotations'][0]
                try:
                    confident = int(annotation['confident'])
                except:
                    confident = -1

                if confident < 5:
                    i+=1
                    #gotoAnno.append(item)
            elif len(item['annotations']) > 1 and len(item['annotations']) <=3:
                reanno = solve_disagreement(item['annotations'])
                if reanno:
                    gotoAnno.append(item)
            else:
                pass


            claim = item['Claim'].strip()
            claim = claim.replace('\t','')
            claim = claim.replace('\n','')
            explaination = item['Explaination'].strip()
            explaination = explaination.replace('\t','')
            explaination = explaination.replace('\n','')
            unique_id = item['unique_wv_id'].strip()
            outline = unique_id+'\t'+claim+'\t'+explaination
            for annotation in item['annotations']:
                #print(annotation)
                label = annotation['label']
                confident = annotation['confident']
                annotator = annotation['annotator']
                outline += '\t'+label+'\t'+confident+'\t'+annotator
            outline += '\n'
            fo.write(outline)
    print(t, i)
    print(len(gotoAnno))
    with open(new_json_file, 'w') as fj:
        json.dump(gotoAnno, fj)





#    for item in dataIter:
#        if len(item['annotations']) == 0:
#            print(item)
#            i+=1
#        t+=1
#    print(t, i)



