import sys
import math
from WvLibs import WVdataIter, ReaderPostProcessor, BatchIterBert, modelUlti
from WvLibs.models import BERT_Simple
from configobj import ConfigObj
import torch
import argparse
import copy
from sklearn.model_selection import KFold
import random
import os
from pathlib import Path



def maskedBertBatchProcessor(x, y):
    word_ids = [s[0] for s in x]
    mask = [s[1] for s in x]
    y = y
    return torch.tensor(word_ids), torch.tensor(y), torch.tensor(mask)


def reconstruct_ids(each_fold, all_ids):
        output_ids = [[],[]] #[train_ids, test_ids]
        for sp_id in range(len(each_fold)):
            current_output_ids = output_ids[sp_id]
            current_fold_ids = each_fold[sp_id]
            for doc_id in current_fold_ids:
                current_output_ids.append(all_ids[doc_id])
        return output_ids

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_json_file", help="Unannotated Json file")
    parser.add_argument("annoed_json_dir", help="Annotated Json file")
    parser.add_argument("--configFile", help="config files if needed")
    parser.add_argument("--cachePath", help="save models")
    parser.add_argument("--nFold", type=int, default=10, help="config files if needed")
    parser.add_argument("--randomSeed", type=int, help="randomSeed for reproduction")
    args = parser.parse_args()

    raw_json_file = args.raw_json_file
    annoed_json_dir = args.annoed_json_dir
    config_file = args.configFile
    cache_path = args.cachePath
    if args.randomSeed:
        random.seed(args.randomSeed)




    config = ConfigObj(config_file)
    postProcessor = ReaderPostProcessor(tokenizer='bert', config=config, word2id=True, return_mask=True, remove_single_list=True)
    dataIter = WVdataIter(annoed_json_dir, raw_json_file, postProcessor=postProcessor.postProcess)

    all_ids = copy.deepcopy(dataIter.all_links)
    random.shuffle(all_ids)

    kf = KFold(n_splits=args.nFold)
    fold_index = 1
    for each_fold in kf.split(all_ids):
        print('running fold', str(fold_index))
        #print(each_fold[1])
        train_val_links, test_links = reconstruct_ids(each_fold, all_ids)
        #print(test_links[0])

        random.shuffle(train_val_links)
        top90_train = math.floor(len(train_val_links) * 0.9)
        train_links = train_val_links[:top90_train]
        val_links = train_val_links[top90_train:]

        trainDataIter = copy.deepcopy(dataIter)
        valDataIter = copy.deepcopy(dataIter)
        testDataIter = copy.deepcopy(dataIter)

        trainDataIter.all_links = train_links
        valDataIter.all_links = val_links
        testDataIter.all_links = test_links
        trainBatchIter = BatchIterBert(trainDataIter, filling_last_batch=True, postProcessor=maskedBertBatchProcessor)
        testBatchIter = BatchIterBert(testDataIter, filling_last_batch=False, postProcessor=maskedBertBatchProcessor)
        valBatchIter = BatchIterBert(valDataIter, filling_last_batch=False, postProcessor=maskedBertBatchProcessor)
        net = BERT_Simple(config)
        mUlti = modelUlti(net, gpu=True)
        fold_cache_path = os.path.join(cache_path, 'fold'+str(fold_index))
        path = Path(fold_cache_path)
        path.mkdir(parents=True, exist_ok=True)
        mUlti.train(trainBatchIter, valBatchIter=valBatchIter, cache_path=fold_cache_path)
        results = mUlti.eval(testBatchIter)
        print(results)
        fold_index += 1




    


    #batchIter = BatchIterBert(dataIter, filling_last_batch=True, postProcessor=maskedBertBatchProcessor)
    #net = BERT_Simple(config)
    #mUlti = modelUlti(net, gpu=True)
    #mUlti.train(batchIter)









