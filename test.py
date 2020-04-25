import sys
from WvLibs import WVdataIter, ReaderPostProcessor, BatchIterBert, modelUlti
from WvLibs.models import BERT_Simple
from configobj import ConfigObj
import torch

def maskedBertBatchProcessor(x, y):
    word_ids = [s[0] for s in x]
    mask = [s[1] for s in x]
    y = y
    return torch.tensor(word_ids), torch.tensor(y), torch.tensor(mask)


raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]
config_file = sys.argv[3]

config = ConfigObj(config_file)

postProcessor = ReaderPostProcessor(tokenizer='bert', config=config, word2id=True, return_mask=True, remove_single_list=True)
#postProcessor = ReaderPostProcessor()

dataIter = WVdataIter(annoed_json_dir, raw_json_file, postProcessor=postProcessor.postProcess)
#print(next(dataIter))

#testIter = WVdataIter(annoed_json_dir, raw_json_file)
#print(next(testIter))

#batchIter = BatchIterBert(dataIter)
#print(next(batchIter))



batchIter = BatchIterBert(dataIter, filling_last_batch=True, postProcessor=maskedBertBatchProcessor)
net = BERT_Simple(config)
mUlti = modelUlti(net, gpu=True)
mUlti.train(batchIter)
