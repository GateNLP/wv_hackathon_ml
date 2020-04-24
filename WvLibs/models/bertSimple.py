from transformers import BertModel
import os
import torch.nn.functional as F
import torch
import torch.nn as nn


class BERT_Simple(nn.Module):
    def __init__(self, config, n_classes=12):
        super().__init__()

        self.n_classes = n_classes
        bert_model_path = os.path.join(config['BERT'].get('bert_path'), 'model')
        bert_dim = int(config['BERT'].get('bert_dim'))
        self.bert = BertModel.from_pretrained(bert_model_path)
        for p in self.bert.parameters():
            p.requires_grad = False

        hidden_dim = 100
        self.hidden = nn.Linear(bert_dim, hidden_dim)
        self.nonlin = torch.nn.Tanh()
        self.layer_output = torch.nn.Linear(hidden_dim, self.n_classes)


    def forward(self, x, mask):
        #print(x.shape)
        #print(mask.shape)
        bert_rep = self.bert(x, attention_mask=mask)[0]
        bert_rep = bert_rep[:,0]
        hidden = self.nonlin(self.hidden(bert_rep))
        out = self.layer_output(hidden)
        return out

