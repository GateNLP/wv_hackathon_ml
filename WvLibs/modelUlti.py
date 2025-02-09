import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os
from pathlib import Path

class modelUlti:
    def __init__(self, net, gpu=False):
        self.net = net
        self.gpu = gpu
        if self.gpu:
            self.net.cuda()

    def train(self, trainBatchIter, num_epohs=100, valBatchIter=None, cache_path=None):
        self.cache_path = cache_path

        self.evaluation_history = []
        self.optimizer = optim.Adam(self.net.parameters())
        self.criterion = nn.CrossEntropyLoss()
        if self.gpu:
            self.criterion.cuda()
        for epoch in range(num_epohs):
            all_loss = []
            trainIter = self.pred(trainBatchIter, train=True)
            for pred, y in trainIter:
                loss = self.criterion(pred, y)
                loss.backward()
                self.optimizer.step()
                loss_value = float(loss.data.item())
                all_loss.append(loss_value)
            print("             ")
            if valBatchIter:
                output_dict = self.eval(valBatchIter)
                stop_signal = self.earlyStop(output_dict)
                if stop_signal:
                    print('stop signal received, stop training')
                    cache_load_path = os.path.join(self.cachePath, 'best_net.model')
                    print('finish training, load model from ', cache_load_path)
                    self.loadWeights(cache_load_path)

                
            print('epoch ', epoch, 'loss', sum(all_loss)/len(all_loss), ' val acc: ', output_dict['accuracy'])


    def earlyStop(self, output_dict, metric='accuracy', patience=5):
        result = output_dict['accuracy']
        stop_signal = False
        self.evaluation_history.append(result)
        num_epochs = len(self.evaluation_history)
        max_result = max(self.evaluation_history)
        max_epoch = self.evaluation_history.index(max_result)
        max_passed = num_epochs - max_epoch
        if max_passed >= patience:
            stop_signal = True

        if max_passed == 1:
            print('caching best')
            cache_path = os.path.join(self.cache_path, 'best_net.model')
            self.saveWeights(cache_path)


    def pred(self, batchGen, train=False):
        if train:
            self.net.train()
            self.optimizer.zero_grad()
        else:
            self.net.eval()
        i=0
        for x, y, mask in batchGen:
            i+=1
            print("processing batch", i, end='\r')
            if self.gpu:
                x = x.type(torch.cuda.LongTensor)
                mask = mask.type(torch.cuda.LongTensor)
                y = y.type(torch.cuda.LongTensor)
                x.cuda()
                mask.cuda()
                y.cuda()
            pred = self.net(x, mask)
            yield pred, y

    def eval(self, batchGen):
        output_dict = {}
        all_prediction = []
        all_true_label = []
        for pred, y in self.pred(batchGen):
            current_batch_out = F.softmax(pred, dim=-1)
            label_prediction = torch.max(current_batch_out, -1)[1]
            current_batch_out_list = current_batch_out.to('cpu').detach().numpy()
            label_prediction_list = label_prediction.to('cpu').detach().numpy()
            y_list = y.to('cpu').detach().numpy()
            all_prediction.append(label_prediction_list)
            all_true_label.append(y_list)

        all_prediction = np.concatenate(all_prediction)
        all_true_label = np.concatenate(all_true_label)
        num_correct = (all_prediction == all_true_label).sum()
        accuracy = num_correct / len(all_prediction)
        output_dict['accuracy'] = accuracy
        output_dict['f-measure'] = {}
        for class_id in list(range(12)):
            f_measure_score = self.fMeasure(all_prediction, all_true_label, class_id)
            output_dict['f-measure']['class '+str(class_id)] = f_measure_score

        return output_dict


    def saveWeights(self, save_path):
        torch.save(self.net.state_dict(), save_path)

    def loadWeights(self, load_path, cpu=True):
        if cpu:
            self.net.load_state_dict(torch.load(load_path, map_location=torch.device('cpu')), strict=False)
        else:
            self.net.load_state_dict(torch.load(load_path), strict=False)
        self.net.eval()


    def fMeasure(self, all_prediction, true_label, class_id, ignoreid=None):
        mask = [class_id] * len(all_prediction)
        mask_arrary = np.array(mask)
        pred_mask = np.argwhere(all_prediction==class_id)
        #print(pred_mask)
        true_mask = np.argwhere(true_label==class_id)

        total_pred = 0
        total_true = 0
        pc = 0
        for i in pred_mask:
            if all_prediction[i[0]] == true_label[i[0]]:
                pc+=1
            if true_label[i[0]] != ignoreid:
                total_pred += 1


        rc = 0
        for i in true_mask:
            if all_prediction[i[0]] == true_label[i[0]]:
                rc+=1
            if true_label[i[0]] != ignoreid:
                total_true += 1

        if total_pred == 0:
            precision = 0
        else:
            precision = float(pc)/total_pred
        if total_true == 0:
            recall = 0
        else:
            recall = float(rc)/total_true
        if (precision+recall)==0:
            f_measure = 0
        else:
            f_measure = 2*((precision*recall)/(precision+recall))
        return precision, recall, f_measure
