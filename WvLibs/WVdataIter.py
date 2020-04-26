from .DataReader import DataReader
import random

class WVdataIter(DataReader):
    def __init__(self, annoed_json_dir, raw_json, min_anno_filter=-1, postProcessor=None, shuffle=True, ignoreLabelList=[], ignoreUserList=[], confThres=-1, check_validation=True):
        if min_anno_filter > 0:
            ignore_empty = True
        else:
            ignore_empty = False
        super().__init__(annoed_json_dir, raw_json, ignoreLabelList=ignoreLabelList, ignoreUserList=ignoreUserList, confThres=confThres, ignore_empty=ignore_empty)
    #def __init__(self, *args, min_anno_filter=1, postProcessor=None, shuffle=True, **kwargs):
    #    super().__init__(*args, kwargs)
        self.shuffle = shuffle
        self.check_validation = check_validation
        self.filterByMinAnno(min_anno_filter)
        self._reset_iter()
        self.postProcessor = postProcessor


    def filterByMinAnno(self, min_anno_filter):
        self.min_anno_filter = min_anno_filter
        all_links = []
        for link in self.data_dict:
            num_annotations = len(self.data_dict[link]['annotations'])
            if num_annotations >= self.min_anno_filter:
                if self.check_validation:
                    if self._check_annotation_valid(self.data_dict[link]['annotations']):
                        all_links.append(link)
                else:
                    all_links.append(link)

        self.all_links = all_links


    def _check_annotation_valid(self, annotation):
        at_least_one_ture = False
        for item in annotation:
            current_label = item['label']
            current_confident = item['confident']
            if len(current_label) > 0 and len(current_confident)>0:
                at_least_one_ture = True
        return at_least_one_ture

        
    def __iter__(self):
        if self.shuffle:
            random.shuffle(self.all_links)

        self._reset_iter()
        return self

    def __next__(self):
        if self.current_sample_idx < len(self.all_links):
            current_sample = self._readNextSample()
            self.current_sample_idx += 1
            if self.postProcessor:
                return self.postProcessor(current_sample)
            else:
                return current_sample

        else:
            self._reset_iter()
            raise StopIteration


    def _readNextSample(self):
        current_link = self.all_links[self.current_sample_idx]
        current_sample = self.data_dict[current_link]
        return current_sample


    def __len__(self):
        return len(self.all_links)

    def _reset_iter(self):
        self.current_sample_idx = 0



