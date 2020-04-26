import json
import glob
import os
import re
import hashlib

class DataReader:
    def __init__(self, annoed_json_dir, raw_json, ignoreLabelList=[], ignoreUserList=[], confThres=0, filter_no_conf=False, ignore_empty=False):
        self.ignoreLabelList = ignoreLabelList
        self.ignoreUserList = ignoreUserList
        self.confThres = confThres
        self.filter_no_conf = filter_no_conf
        self.ignore_empty = ignore_empty
        #print(self.ignoreLabelList)
        #print(self.ignoreUserList)

        self._anno_user_regex()
        self._read_raw_json(raw_json)
        self._read_annoed_data(annoed_json_dir)

    def _anno_user_regex(self):
        self.label_field_regex = re.compile('ann\d*\_label')
        self.annotator_id_regex = re.compile('(?<=ann)\d*(?=\_label)')
        self.confident_field_regex = re.compile('ann\d*\_conf')
        self.remark_field_regex = re.compile('ann\d*\_remarks')

    def _read_annoed_data(self, annoed_json_dir):
        all_jsons = glob.glob(annoed_json_dir+'/*.json')
        for each_annoed_json_file in all_jsons:
            self._read_annoed_json(each_annoed_json_file)
        #print(all_jsons)

    def _read_annoed_json(self, annoed_json):
        with open(annoed_json, 'r') as f_json:
            all_json_data = json.load(f_json)
        for each_annoed_data in all_json_data:
            uniqueIdentifier = self._get_unique_identifier(each_annoed_data)
            #data_link = each_annoed_data['Link']
            annotation_info, include = self._get_annotation_info(each_annoed_data)
            
            if len(annotation_info['label']) < 0 and ignore_empty:
                include = False
            
            if include:
                self.data_dict[uniqueIdentifier]['annotations'].append(annotation_info)

            
    def _get_annotation_info(self, dict_data):
        annotation_info_dict = {}
        dict_keys = dict_data.keys()
        include = True
        for current_key in dict_keys:
            m_label = self.label_field_regex.match(current_key)
            if m_label:
                raw_label_field = m_label.group()
                #print(raw_label_field)
                annotator_id = self.annotator_id_regex.search(raw_label_field).group()
                #print(annotator_id)
                annotation_info_dict['annotator'] = annotator_id
                label = dict_data[raw_label_field]
                #print(label)
                annotation_info_dict['label'] = label
                if label in self.ignoreLabelList:
                    include = False
                if annotator_id in self.ignoreUserList:
                    include = False
            m_conf = self.confident_field_regex.match(current_key)
            if m_conf:
                raw_conf_field = m_conf.group()
                confident = dict_data[raw_conf_field]
                #print(confident)
                annotation_info_dict['confident'] = confident
                if len(confident) < 1:
                    if self.filter_no_conf:
                        include = False
                elif (int(confident) <= self.confThres):
                    include = False

            m_remark = self.remark_field_regex.match(current_key)
            if m_remark:
                raw_remark_field = m_remark.group()
                remark = dict_data[raw_remark_field]
                #print(remark)
                annotation_info_dict['remark'] = remark

        return annotation_info_dict, include

                

    def _get_unique_identifier(self, each_data):
        source_link = each_data['Source'].strip()
        claim = each_data['Claim'].strip()
        explaination = each_data['Explaination'].strip()
        sourceToken = source_link.split('/')
        top3Source = ' '.join(sourceToken[:3])
        top200claim = claim[:200]
        top200expl = explaination[:200]
        uniqueString = top200claim+top200expl+top3Source

        #sourceQuesionToken = source_link.split('?')
        #uniqueString = sourceQuesionToken[0]
        #print(uniqueString)

        uniqueIdentifier = hashlib.sha224(uniqueString.encode('utf-8')).hexdigest()
        return uniqueIdentifier


    def _read_raw_json(self, raw_json):
        self.data_dict = {}
        with open(raw_json, 'r') as f_json:
            raw_data = json.load(f_json)
        duplicated = 0
        total_data = 0
        for each_data in raw_data:
            data_link = each_data['Link']
            uniqueIdentifier = self._get_unique_identifier(each_data)
            if uniqueIdentifier not in self.data_dict:
                each_data['unique_wv_id'] = uniqueIdentifier
                each_data['annotations'] = []
                self.data_dict[uniqueIdentifier] = each_data
            else:
                duplicated += 1
                #print(uniqueIdentifier)
                #print('id: ', self.data_dict[uniqueIdentifier]['unique_wv_id'])
                #print(self.data_dict[uniqueIdentifier])
                #print(each_data)
                #print('\n')
            total_data += 1

        print('num duplicated: ', duplicated)
        print('total num data: ', total_data)





