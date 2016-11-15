from operator import itemgetter as ig
from tfchain import session

import chainer
import heapq
import numpy as np
import tensorflow as tf
import tfchain.functions as F
import tfchain.links as L


def totf(forward):

    def f(model, x):
        feed_x = x.data.transpose(0, 2, 3, 1) if x.ndim == 4 else x.data
        input_x = tf.Variable(feed_x)

        if not hasattr(model, 'tf_graph'):
            y = forward(model, x)
            cand_funcs = []
            comp_graph = []
            seen_set = set()

            def add_cand(cand):
                if cand not in seen_set:
                    # Negate since heapq is min-heap
                    heapq.heappush(
                        cand_funcs, (-cand.rank, len(seen_set), cand))
                    seen_set.add(cand)

            add_cand(y.creator)
            while cand_funcs:
                _, _, func = heapq.heappop(cand_funcs)
                comp_graph.append((func, func.inputs[1:]))
                for func_x in func.inputs:
                    if func_x.creator is not None:
                        add_cand(func_x.creator)

            model.tf_graph = []
            for link, param in reversed(comp_graph):
                label = link.label
                if label == 'Convolution2DFunction':
                    param = param + [(link.sy, link.sx)] + [(link.ph, link.pw)]
                    model.tf_graph.append(L.Convolution2D(*param))
                elif label == 'LinearFunction':
                    model.tf_graph.append(L.Linear(*param))
                elif label == 'MaxPooling2D':
                    ksize = (link.kh, link.kw)
                    stride = (link.sy, link.sx)
                    pad = (link.ph, link.pw)
                    model.tf_graph.append(F.MaxPooling2D(ksize, stride, pad))
                elif label == 'ReLU':
                    model.tf_graph.append(F.ReLU())

            y = input_x
            for f in model.tf_graph:
                y = f(y)
            model.op = y

        if not hasattr(model, 'session'):
            model.session = session.get_session()
            model.session.run(tf.initialize_all_variables())

        if isinstance(x, chainer.Variable):
            x = x.data
        if hasattr(x, 'ndim') and x.ndim == 4:
            x = x.transpose(0, 2, 3, 1)  # to NHWC

        return model.session.run(model.op, feed_dict={input_x: feed_x})

    return f