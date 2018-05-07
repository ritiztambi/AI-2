import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow.python.framework import ops 


def initialize_parameters():
    W1 = tf.get_variable("W1", [784, 300], initializer = tf.truncated_normal_initializer)
    b1 = tf.get_variable("b1", [1, 300], initializer = tf.zeros_initializer())
    W2 = tf.get_variable("W2", [300, 10], initializer = tf.truncated_normal_initializer)
    b2 = tf.get_variable("b2", [1, 10], initializer = tf.zeros_initializer())
    parameters = {"W1": W1,
                  "b1": b1,
                  "W2": W2,
                  "b2": b2}
    return parameters

def forward_prop(X,parameters):
    W1 = parameters['W1']
    b1 = parameters['b1']
    W2 = parameters['W2']
    b2 = parameters['b2']
    Z1 = tf.add(tf.matmul(X,W1), b1)  
    A1 = tf.sigmoid(Z1)                    
    Z2 = tf.add(tf.matmul(A1,W2), b2)                     
    O = tf.sigmoid(Z2)     
    return O
            
            
def compute_error(O,Y):
    error = tf.losses.mean_squared_error(labels = Y, predictions = O)
    return error


def model(X_train, Y_train):   
    ops.reset_default_graph()          
    (training_size,shape)=X_train.shape
    x = tf.placeholder(tf.float32, shape=[None, 784])
    y = tf.placeholder(tf.float32, shape=[None, 10])
    parameters = initialize_parameters()
    y_pred = forward_prop(x,parameters)
    cost = compute_error(y_pred,y)
    optimizer = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
    init = tf.global_variables_initializer()                           
    seed = 1    
    with tf.Session() as sess:
        sess.run(init)
        epoch = 0
        while epoch < 5000:
            epoch = epoch+1
            epoch_cost = 0
            seed = seed + 1
            train_set = tf.concat([X_train, Y_train], 1)
            print(train_set.shape)
            minibatches = tf.train.shuffle_batch([X_train, Y_train],batch_size=32,seed=seed,capacity=50000,min_after_dequeue=10000, enqueue_many=False)
            for minibatch in minibatches:
                print(str(minibatch.shape))
                (minibatch_X, minibatch_Y) = minibatch
                _ , minibatch_cost = sess.run([optimizer, cost], feed_dict={x: minibatch_X, y: minibatch_Y}) 
                epoch_cost += minibatch_cost / num_minibatches
                if epoch % 100 == 0:
                    print ("Cost after epoch %i: %f" % (epoch, epoch_cost))
                

def main():
    mnist = input_data.read_data_sets("MNIST_data", one_hot=True)
    x_train = mnist.train.images
    y_train = mnist.train.labels
    print(str(y_train.shape))
    model(x_train,y_train)

if __name__ == "__main__":
    # calling main function
    main()