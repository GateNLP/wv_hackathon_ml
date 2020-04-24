import nltk

class ReaderPostProcessor:
    def __init__(self, tokenizer='nltk', x_fields=['Claim', 'Explaination'], x_output_mode='concat', y_fields=['label'], y_output_mode='high_conf', keep_case=False, label2id=True):
        self.tokenizer = tokenizer
        self.x_fields = x_fields
        self.x_output_mode = x_output_mode
        self.y_fields = y_fields
        self.y_output_mode = y_output_mode
        self.keep_case = keep_case
        self.label2id = label2id
        self.labelsFields = ['PubAuthAction', 'CommSpread', 'GenMedAdv', 'PromActs', 'Consp', 'VirTrans', 'VirOrgn', 'PubPrep', 'Vacc', 'Prot', 'SocAlrm', 'None']
        self.initProcessor()

        
    def initProcessor(self):
        if self.tokenizer == 'nltk':
            self.tokenizerProcessor = self.nltkTokenizer


    def postProcess(self, sample):
        split_x = []
        for x_field in self.x_fields:
            current_rawx = sample[x_field]
            if self.keep_case == False:
                current_rawx = current_rawx.lower()
            current_x = self.x_pipeline(current_rawx)
            split_x.append(current_x)
        x = self.output_x(split_x) 

        split_y = []
        for y_field in self.y_fields:
            current_y_list = []
            for annotation in sample['annotations']:
                print(annotation)
                #current_label = annotation['label']
                current_confident = annotation['confident']
                #current_annotator = annotation['annotator']
                current_selected_field = annotation[y_field]
                if y_field == 'label' and self.label2id:
                    current_selected_field = self.label2ids(current_selected_field)

                current_y_list.append([current_selected_field, current_confident])
            current_y = self.select_y(current_y_list)
            split_y.append(current_y)
        y = split_y
        y = self._removeYSingleList(y)
        return x, y

    def _removeYSingleList(self, y):
        if len(y) == 1:
            return y[0]
        else:
            return y

    def output_x(self, split_x):
        output_x = []
        if self.x_output_mode == 'concat':
            for item in split_x:
                output_x += item

        return output_x

    def select_y(self, current_y):
        #print(current_y)
        selected_y = None
        if self.y_output_mode == 'high_conf':
            sorted_current_y = sorted(current_y, key=lambda s:s[1], reverse=True)
            #print(sorted_current_y)
            selected_y = sorted_current_y[0][0]
        return selected_y


    def label2ids(self, label):
        label_index = self.labelsFields.index(label)
        return label_index





    def x_pipeline(self, raw_x):
        if self.tokenizer:
            raw_x = self.tokenizerProcessor(raw_x)
        return raw_x


    def nltkTokenizer(self, text):
        return nltk.word_tokenize(text)

