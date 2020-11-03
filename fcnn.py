# -*- coding: utf-8 -*-
"""CSC420ProjectFCNN

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13Y-N7xzOP8ufDl84do1UeknoY3JQH6OZ
"""

!pip install torch
!pip3 install torchvision
!pip install quickdraw

import torch
from torchvision import transforms

def get_image_data(group, label, start=0, stop=100):
  if group == None:
    return [], []
  qd = QuickDrawDataGroup(group, print_messages=False)
  data = []
  labels = []

  for drawing in itertools.islice(qd.drawings, start, stop):
    image = drawing.image#.convert('L')
    image = transforms.ToTensor()(image)
    data.append(image)
    labels.append(label)
  
  return data, labels

from torch.utils.data import Dataset
 
class DrawingDataset(Dataset):
  def __init__(self, cat1, cat2=None, cat3=None, cat4=None, cat5=None, cat6=None, cat7=None, cat8=None, cat9=None, cat10=None, start=0, stop=100):
    data1, labels1 = get_image_data(cat1, 0, start, stop)
    data2, labels2 = get_image_data(cat2, 1, start, stop)
    data3, labels3 = get_image_data(cat3, 2, start, stop)
    data4, labels4 = get_image_data(cat4, 3, start, stop)
    data5, labels5 = get_image_data(cat5, 4, start, stop)
    data6, labels6 = get_image_data(cat6, 5, start, stop)
    data7, labels7 = get_image_data(cat7, 6, start, stop)
    data8, labels8 = get_image_data(cat8, 7, start, stop)
    data9, labels9 = get_image_data(cat9, 8, start, stop)
    data10, labels10 = get_image_data(cat10, 9, start, stop)
    self.data = data1 + data2 + data3 + data4 + data5 + data6 + data7 + data8 + data9 + data10
    self.labels = labels1 + labels2 + labels3 + labels4 + labels5 + labels6 + labels7 + labels8 + labels9 + labels10
 
  def __len__(self):
      return len(self.data)
 
  def __getitem__(self, idx):
      return self.data[idx], self.labels[idx]

import itertools
import matplotlib.pyplot as plt
from quickdraw import QuickDrawDataGroup
import numpy as np

train_dataset = DrawingDataset('apple', 'basketball', 'cookie', 'dolphin', 'envelope', 'fish', 'golf club', 'headphones', 'ice cream', 'light bulb')
val_dataset = DrawingDataset('apple', 'basketball', 'cookie', 'dolphin', 'envelope', 'fish', 'golf club', 'headphones', 'ice cream', 'light bulb', 100, 120)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=80, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=20)

import torch
import helper
from torchvision import datasets, transforms
from torch import nn, optim
import torch.nn.functional as F

"""## Fully Connected Network"""

class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(256*7*7, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 10)
        #self.fc3 = nn.Linear(32, 16)
        #self.fc4 = nn.Linear(16, 10)
        
    def forward(self, x):
        # make sure input tensor is flattened
        print(x.shape)
        x = x.view(-1, x.shape[0])
        print(x.shape)
        x = F.relu(self.fc1(x))
        print(x.shape)
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.log_softmax(self.fc4(x), dim=1)
        return x

"""## Convolutional Network"""

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.fc = nn.Linear(63*63*32, 10)
        
    def forward(self, x):
        #print(x.shape)
        out = self.layer1(x)
        #print(out.shape)
        out = self.layer2(out)
        #print(out.shape)
        out = out.view(out.size(0), -1)
        #print(out.shape)
        out = self.fc(out)
        return F.log_softmax(out, dim=1)

model = CNN()
print(model)

def get_accuracy(model, dataloader, class_acc=False):
    correct, total = 0, 0
    for imgs, labels in dataloader:
      imgs = imgs.squeeze()

      #To Enable GPU Usage
      if use_cuda and torch.cuda.is_available():
        imgs = imgs.cuda()
        labels = labels.cuda()
      
      output = model(imgs)
      #select index with maximum prediction score
      pred = output.max(1, keepdim=True)[1]
      correct += pred.eq(labels.view_as(pred)).sum().item()
      total += imgs.shape[0]

      if class_acc:
        classes = ['Apple', 'Basketball', 'Cookie', 'Dolphin', 'Envelope', 'Fish', 'Golf Club', 'Headphones', 'Ice Cream', 'Light Bulb']
        print('{} Classification Accuracy: {:.3f}'.format(classes[labels[0]], correct/total))
    
    if class_acc:
      return

    return correct / total

import copy

def train(model, train_loader, val_loader, batch_size=64, num_epochs=5):
    criterion = nn.CrossEntropyLoss()
    # criterion = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.005, momentum=0.9)
    # optimizer = optim.Adam(model.parameters(), lr=0.003)
    iters, losses, train_acc, val_acc = [], [], [], []
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    # training
    n = 0 # the number of iterations
    for epoch in range(num_epochs):
        for imgs, labels in train_loader:
            imgs = imgs.squeeze()

            #To Enable GPU Usage
            if use_cuda and torch.cuda.is_available():
              imgs = imgs.cuda()
              labels = labels.cuda()
             
            out = model(imgs)
            #print(out)
            #print(labels)
            loss = criterion(out, labels) # compute the total loss
            loss.backward()               # backward pass (compute parameter updates)
            optimizer.step()              # make the updates for each parameter
            optimizer.zero_grad()         # a clean up step for PyTorch

        # save the current training information
        iters.append(n)
        losses.append(float(loss)/batch_size)             # compute *average* loss
        
        train_acc.append(get_accuracy(model, train_loader)) # compute training accuracy 
        val_acc.append(get_accuracy(model, val_loader))  # compute validation accuracy
        print("Epoch {} Training Accuracy: {}".format(n, train_acc[-1]))
        print("Epoch {} Validation Accuracy: {}".format(n, val_acc[-1]))
        
        n += 1
        # deep copy the model
        if val_acc[-1] > best_acc:
          best_acc = val_acc[-1]
          best_model_wts = copy.deepcopy(model.state_dict())

    #plotting
    plt.title("Training Curve")
    plt.plot(iters, losses, label="Train")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.show()

    plt.title("Training Curve")
    plt.plot(iters, train_acc, label="Train")
    plt.plot(iters, val_acc, label="Validation")
    plt.xlabel("Iterations")
    plt.ylabel("Training Accuracy")
    plt.legend(loc='best')
    plt.show()

    # load best model weights
    model.load_state_dict(best_model_wts)
    print("Final Training Accuracy: {}".format(train_acc[-1]))
    print("Final Validation Accuracy: {}".format(val_acc[-1]))
    return model

model = CNN()

use_cuda = True
if use_cuda and torch.cuda.is_available():
  model.cuda()
  print('CUDA is available!  Training on GPU ...')

trained_model = train(model, train_loader, val_loader, num_epochs=3)

get_accuracy(trained_model, val_loader, class_acc=True)