import chainer
import numpy as np
import tensorflow as tf
import tfchain


class Linear(tfchain.Link):

    def __init__(self, *args):
        super(Linear, self).__init__(*args)

    def forward(self, x):
        if isinstance(x, tf.Tensor):
            shape = x.get_shape()
            x = tf.reshape(
                x, (int(shape[0]), int(np.prod(shape[1:]))))
        elif isinstance(x, chainer.Variable):
            shape = x.shape
            x = x.reshape((shape[0], np.prod(shape[1:])))
        return tf.matmul(x, tf.transpose(self.W)) + self.b