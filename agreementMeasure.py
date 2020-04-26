import sys
from WvLibs import WVdataIter, ReaderPostProcessor
import re
from itertools import combinations
import argparse


def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)
    return list


def check_pare(ann1, ann2, agreeDict):
    combine1 = ann1+'|'+ann2
    combine2 = ann2+'|'+ann1
    combines = [combine1, combine2]
    combineInDict = False
    for combine in combines:
        if combine in agreeDict:
            combineInDict = True
            break
    return combine, combineInDict


def update_disagreement_dict(disagreeLabel1, disagreeLabel2, class_disagree_check_dict):
    if disagreeLabel1 not in class_disagree_check_dict:
        class_disagree_check_dict[disagreeLabel1] = {}
    if disagreeLabel2 not in class_disagree_check_dict[disagreeLabel1]:
        class_disagree_check_dict[disagreeLabel1][disagreeLabel2] = 0

    class_disagree_check_dict[disagreeLabel1][disagreeLabel2] += 1
    return class_disagree_check_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_json_file", help="Unannotated Json file")
    parser.add_argument("annoed_json_dir", help="Annotated Json file dir")
    parser.add_argument("tsv_file", help="tsv file to output")
    parser.add_argument("--ignoreLabel", help="ignore label")
    parser.add_argument("--ignoreUser", help="ignore user")
    parser.add_argument("--min_anno_filter", type=int, default=2, help="min frequence")
    parser.add_argument("--conf_thres", type=int, default=-1, help="confident threshold")
    args = parser.parse_args()


    raw_json_file = args.raw_json_file
    annoed_json_dir = args.annoed_json_dir
    tsv_file = args.tsv_file
    min_frequence = args.min_anno_filter
    conf_thres = args.conf_thres

    list2ignor = []
    user2ignor = []
    if args.ignoreLabel:
        list2ignor = args.ignoreLabel.split(',')

    if args.ignoreUser:
        user2ignor = args.ignoreUser.split(',')



    dataIter = WVdataIter(annoed_json_dir, raw_json_file, min_anno_filter=min_frequence, ignoreLabelList=list2ignor, ignoreUserList=user2ignor, confThres=conf_thres)

    compare_list = []


    with open(tsv_file, 'w') as fo:
        outline = 'link\tclaim\texplaination\tlabel1\tconfident1\tannotator1\tlabel2\tconfident2\tannotator2\tlabel3\tconfident3\tannotator3\n'
        fo.write(outline)
        for item in dataIter:
            tmp_list = []
            anno_list = []
            claim = item['Claim'].strip()
            claim = claim.replace('\t','')
            explaination = item['Explaination'].strip()
            explaination = explaination.replace('\t','')
            link = item['Link'].strip()
            line = link.replace('\t','')
            outline = link+'\t'+claim+'\t'+explaination
            for annotation in item['annotations']:
                #print(annotation)
                label = annotation['label']
                confident = annotation['confident']
                annotator = annotation['annotator']
                if annotator not in anno_list:
                    anno_list.append(annotator)
                    tmp_list.append([annotator, label])
    
                combine_list = list(combinations(tmp_list, 2))  
                compare_list += combine_list
                outline += '\t'+label+'\t'+confident+'\t'+annotator
            outline += '\n'
            fo.write(outline)
    
    #print(compare_list)
    t=0
    a=0
    agreeDict = {}

    for compare_pair in compare_list:
        ann1 = compare_pair[0][0]
        label1 = compare_pair[0][1]
        ann2 = compare_pair[1][0]
        label2 = compare_pair[1][1]
        if (label1 not in list2ignor) and (label2 not in list2ignor) and (ann1 not in user2ignor) and (ann2 not in user2ignor):
            t+=1
            combine, combineInDict = check_pare(ann1, ann2, agreeDict)

            if combineInDict:
                agreeDict[combine]['t'] += 1
            else:
                agreeDict[combine] = {}
                agreeDict[combine]['t'] = 1
                agreeDict[combine]['a'] = 0
                agreeDict[combine]['disagree'] = {}
                agreeDict[combine]['disagree'][ann1] = []
                agreeDict[combine]['disagree'][ann2] = []

            if label1 == label2:
                a+=1
                agreeDict[combine]['a'] += 1
            else:
                agreeDict[combine]['disagree'][ann1].append(label1)
                agreeDict[combine]['disagree'][ann2].append(label2)



    pa = a/t
    pe = 1/11
    kappa = (pa-pe)/(1-pe)
    print('overall agreement: ', pa)
    print('overall kappa: ', kappa)
    print('total pair compareed: ', t)
    print('annotator pair agreement kappa num_compared')
    class_disagree_check_dict = {}
    for annPair in agreeDict:
        print('\n')
        print('============')
        num_compared = agreeDict[annPair]['t']
        cpa = agreeDict[annPair]['a']/agreeDict[annPair]['t']
        kappa = (cpa-pe)/(1-pe)
        print(annPair, cpa, kappa, num_compared)
        keys = getList(agreeDict[annPair]['disagree'])
        print(keys)
        for i in range(len(agreeDict[annPair]['disagree'][keys[0]])):
            disagreeLabel1 = agreeDict[annPair]['disagree'][keys[0]][i]
            disagreeLabel2 = agreeDict[annPair]['disagree'][keys[1]][i]
            print(disagreeLabel1, disagreeLabel2)
            class_disagree_check_dict = update_disagreement_dict(disagreeLabel1, disagreeLabel2, class_disagree_check_dict)
            class_disagree_check_dict = update_disagreement_dict(disagreeLabel2, disagreeLabel1, class_disagree_check_dict)
    
    print('\n')
    print('=========================')
    print('class level disagreement')
    print('=========================')
    for item_label in class_disagree_check_dict:
        print(item_label)
        print(class_disagree_check_dict[item_label])
        print('===================')
        print('\n')
    
    
    
    
