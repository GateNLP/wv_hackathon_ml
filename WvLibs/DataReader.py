import json
import glob
import os
import re

class DataReader:
    def __init__(self, annoed_json_dir, raw_json):
        self._anno_user_regex()
        self._read_raw_json(raw_json)
        self._read_annoed_data(annoed_json_dir)
        print(self.data_dict)
        
    def _anno_user_regex(self):
        self.label_field_regex = re.compile('ann\d*\_label')
        self.annotator_id_regex = re.compile('(?<=ann)\d*(?=\_label)')
        self.confident_field_regex = re.compile('ann\d*\_conf')
        self.remark_field_regex = re.compile('ann\d*\_remarks')

    def _read_annoed_data(self, annoed_json_dir):
        all_jsons = glob.glob(annoed_json_dir+'/*')
        for each_annoed_json_file in all_jsons:
            self._read_annoed_json(each_annoed_json_file)
        #print(all_jsons)

    def _read_annoed_json(self, annoed_json):
        with open(annoed_json, 'r') as f_json:
            all_json_data = json.load(f_json)
        for each_annoed_data in all_json_data:
            data_link = each_annoed_data['Link']
            annotation_info = self._get_annotation_info(each_annoed_data)
            self.data_dict[data_link]['annotations'].append(annotation_info)

            
    def _get_annotation_info(self, dict_data):
        annotation_info_dict = {}
        dict_keys = dict_data.keys()
        for current_key in dict_keys:
            m_label = self.label_field_regex.match(current_key)
            if m_label:
                raw_label_field = m_label.group()
                print(raw_label_field)
                annotator_id = self.annotator_id_regex.search(raw_label_field).group()
                print(annotator_id)
                annotation_info_dict['annotator'] = annotator_id
                label = dict_data[raw_label_field]
                print(label)
                annotation_info_dict['label'] = label
            m_conf = self.confident_field_regex.match(current_key)
            if m_conf:
                raw_conf_field = m_conf.group()
                confident = dict_data[raw_conf_field]
                print(confident)
                annotation_info_dict['confident'] = confident

            m_remark = self.remark_field_regex.match(current_key)
            if m_remark:
                raw_remark_field = m_remark.group()
                remark = dict_data[raw_remark_field]
                print(remark)
                annotation_info_dict['remark'] = remark
        return annotation_info_dict

                



    def _read_raw_json(self, raw_json):
        self.data_dict = {}
        with open(raw_json, 'r') as f_json:
            raw_data = json.load(f_json)
        duplicated = 0
        total_data = 0
        for each_data in raw_data:
            data_link = each_data['Link']
            if data_link not in self.data_dict:
                each_data['id'] = total_data
                each_data['annotations'] = []
                self.data_dict[data_link] = each_data
            else:
                duplicated += 1
                #print(data_link)
                #print('id: ', self.data_dict[data_link]['id'])
                #print(self.data_dict[data_link])
                #print('id: ', total_data)
                #print(each_data)
                #print('\n')
            total_data += 1

        print('num duplicated: ', duplicated)
        print('total num data: ', total_data)





