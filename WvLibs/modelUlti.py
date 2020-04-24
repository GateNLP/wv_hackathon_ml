import torch
import torch.nn as nn
import torch.optim as optim

class modelUlti:
    def __init__(self, net, gpu=False):
        self.net = net
        self.gpu = gpu
        if self.gpu:
            self.net.cuda()

    def train(self, trainBatchIter, num_epohs=10):
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
            print('epoch ', epoch, 'loss', sum(all_loss)/len(all_loss))




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













