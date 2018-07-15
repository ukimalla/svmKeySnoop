"""
  Autocompletion of the third character of words
  Given a word with a blank third letter, learn to predict the missing third letter
"""
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np

vocab = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
         'h', 'i', 'j', 'k', 'l', 'm', 'n',
         'o', 'p', 'q', 'r', 's', 't', 'u',
         'v', 'w', 'x', 'y', 'z', '_']

# index array of characters in vocab
v_map = {n: i for i, n in enumerate(vocab)}
v_len = len(v_map)

# training data (character sequences)
# wo_d -> X, r -> Y
# wo_d -> X, o -> Y
# de_p -> X, e -> Y
training_data = ['word', 'wood', 'deep', 'dive', 'cold', 'cool', 'load', 'love', 'kiss', 'kind']
test_data = ['wood', 'deep', 'cold', 'load', 'love', 'dear', 'dove', 'cell', 'life', 'keep']




def make_batch(seq_data):
    input_batch = []
    target_batch = []

    for seq in seq_data:
        # Indices of the first three alphabets of the words
        # [22, 14, 17] [22, 14, 14] [3, 4, 4] [3, 8, 21] ...
        input = [v_map[n] for n in seq[:2]]

        # Inserting a "_" (blank) on the third letter.
        input.append(v_map["_"])
        input.append(v_map[seq[3:]])

        # Indices of the third alphabet of the words
        # 3, 3, 15, 4, 3 ...
        target = v_map[seq[2]]  # Setting the target as the

        # One-hot encoding of the inputs into the sequences of 26-dimensional vectors
        # [0, 1, 2] ==>
        # [[ 1.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
        #  [ 0.  1.  0.  0.  0.  0.  0.  0.  0.  0.]
        #  [ 0.  0.  1.  0.  0.  0.  0.  0.  0.  0.]]
        input_batch.append(np.eye(v_len)[input])

        # We don't apply one-hot encoding for the output,
        # since we'll use sparse_softmax_cross_entropy_with_logits
        # as our loss function
        target_batch.append(target)

    return input_batch, target_batch


learning_rate = 0.01
n_hidden = 10
total_epoch = 100
n_step = 4  # the length of the input sequence
n_input = n_class = v_len  # the size of each input

"""
  Phase 1: Create the computation graph
"""
X = tf.placeholder(tf.float32, [None, n_step, n_input])
Y = tf.placeholder(tf.int32, [None])

W = tf.Variable(tf.random_normal([n_hidden, n_class]))
b = tf.Variable(tf.random_normal([n_class]))

#                   output (pred. of forth letter)
#                       | (W,b)
#                   outputs (hidden)
#       |    |     |    |
# RNN: [t1]-[t2]-[t3]-[t4]-
#       x1   x2   x3   x4

# Create an LSTM cell
cell = tf.nn.rnn_cell.BasicLSTMCell(n_hidden)
# Apply dropout for regularization
# cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=0.75)

# Create the RNN
outputs, states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
# outputs : [batch_size, max_time, cell.output_size]

# Transform the output of RNN to create output values
outputs = tf.transpose(outputs, [1, 0, 2])
outputs = outputs[-1]
# [batch_size, cell.output_size]
model = tf.matmul(outputs, W) + b
# [batch_size, n_classes]

cost = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=model, labels=Y))

optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)

"""
  Phase 2: Train the model
"""
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    input_batch, target_batch = make_batch(training_data)

    for epoch in range(total_epoch):
        _, loss = sess.run([optimizer, cost],
                           feed_dict={X: input_batch, Y: target_batch})

        print('Epoch:', '%04d' % (epoch + 1),
              'cost =', '{:.6f}'.format(loss))

    print('Optimization finished')

    """
      Make predictions
    """
    seq_data = training_data  # test_data
    prediction = tf.cast(tf.argmax(model, 1), tf.int32)
    accuracy = tf.reduce_mean(tf.cast(tf.equal(prediction, Y), tf.float32))

    input_batch, target_batch = make_batch(seq_data)

    predict, accuracy_val = sess.run([prediction, accuracy],
                                     feed_dict={X: input_batch, Y: target_batch})

    predicted = []
    for idx, val in enumerate(seq_data):
        predicted_char = vocab[predict[idx]]
        predicted.append(val[:2] + predicted_char + val[-1:])

    print('\n=== Predictions ===')
    print('Input:', [w[:2] + '_' + w[-1:] for w in seq_data])
    print('Predicted:', predicted)
    print('Accuracy:', accuracy_val)