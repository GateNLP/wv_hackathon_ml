import sys
from WvLibs import WVdataIter, ReaderPostProcessor
import re
from itertools import combinations
import argparse
import json

def solve_disagreement(annotations):
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
        sorted_annotation_list = sorted(annotation_list, key=lambda s:s[1], reverse=True)
        selected_label = sorted_annotation_list[0][0]
    #print(selected_label, annotation_list)
    return selected_label


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_json_file", help="Unannotated Json file")
    parser.add_argument("annoed_json_dir", help="Annotated Json file dir")
    parser.add_argument("merged_json", help="merged json")
    parser.add_argument("--ignoreLabel", help="ignore label")
    parser.add_argument("--ignoreUser", help="ignore user")
    parser.add_argument("--min_anno_filter", type=int, default=1, help="min frequence")
    args = parser.parse_args()


    raw_json_file = args.raw_json_file
    annoed_json_dir = args.annoed_json_dir
    merged_json = args.merged_json
    min_frequence = args.min_anno_filter

    list2ignor = []
    user2ignor = []
    if args.ignoreLabel:
        list2ignor = args.ignoreLabel.split(',')

    if args.ignoreUser:
        user2ignor = args.ignoreUser.split(',')



    dataIter = WVdataIter(annoed_json_dir, raw_json_file, min_anno_filter=min_frequence, ignoreLabelList=list2ignor, ignoreUserList=user2ignor)


    unique_claim = []
    unique_source = []
    unique_link = []
    unique_expalain = []

    data2merge = []
    unique_identifier = 0
    for item in dataIter:
        claim = item['Claim'].strip()
        link = item['Link'].strip()
        source = item['Source'].strip()
        explain = item['Explaination']
        annotations = item['annotations']
        if claim not in unique_claim:
        #if True:
            unique_claim.append(claim)
            unique_source.append(source)
            unique_link.append(link)
            unique_expalain.append(explain)
            if len(annotations) > 1:
                label = solve_disagreement(annotations)
                confident = 'conf_solve'
                annotator = 'conf_solve'

            else:
                label = item['annotations'][0]['label']
                confident = item['annotations'][0]['confident']
                annotator = item['annotations'][0]['annotator']
            item['annotation'] = label
            data2merge.append(item)
            
        else:
            ci=unique_claim.index(claim)
            print('claim: ', claim)
            print('source1: ', source)
            print('source2: ', unique_source[ci])
            print('explain1: ', explain)
            print('explain2:', unique_expalain[ci])
        #    pass

    with open(merged_json, 'w') as fj:
        json.dump(data2merge, fj)





