import tensorflow as tf

hello = tf.constant('hello tensorflow')

with tf.Session() as sess:
    print(sess.run(hello))