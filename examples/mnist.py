#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chainer.datasets import get_mnist
from tfchain import totf

import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
import os
import tensorflow as tf


class LeNet5(chainer.Chain):

    def __init__(self):
        super(LeNet5, self).__init__(
            conv1=L.Convolution2D(1, 6, 5),
            conv2=L.Convolution2D(6, 16, 5),
            fc3=L.Linear(None, 120),
            fc4=L.Linear(120, 84),
            fc5=L.Linear(84, 10)
        )
        self.train = True

    @totf
    def __call__(self, x):
        h = F.max_pooling_2d(F.relu(self.conv1(x)), 2, 2)
        h = F.max_pooling_2d(F.relu(self.conv2(h)), 2, 2)
        h = F.relu(self.fc3(h))
        h = F.relu(self.fc4(h))
        h = self.fc5(h)
        return h


if __name__ == '__main__':
    model = LeNet5()
    train, valid = get_mnist(ndim=3)
    batchsize = 32
    for epoch in range(3):
        for i in range(0, len(train), batchsize):
            x, t = [], []
            for d in train[i:i + batchsize]:
                x.append(d[0])
                t.append(d[1])
            x = chainer.Variable(np.array(x, dtype=np.float32))
            t = chainer.Variable(np.array(t, dtype=np.int32))
            y = model(x)

    out_dir = 'examples/mnist_results'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    writer = tf.train.SummaryWriter(out_dir, graph=model.session.graph)
    writer.flush()
    if hasattr(model, 'session'):
        model.session.close()
