import tensorflow as tf
from d2l import tensorflow as d2l

batch_size, num_steps = 32, 35
train_iter, vocab = d2l.load_data_time_machine(batch_size, num_steps)

num_hiddens = 256  # 隐层单元数量
# 利用单元级(Cell)的API，实现对单个时间步长的处理
rnn_cell = tf.keras.layers.SimpleRNNCell(num_hiddens, kernel_initializer='glorot_uniform')
# 再将Cell包裹入RNN layer，使得RNN可以处理成批次的数据输入
rnn_layer = tf.keras.layers.RNN(rnn_cell, time_major=True, return_sequences=True, return_state=True)

# 隐状态初始化
state = rnn_cell.get_initial_state(batch_size=batch_size, dtype=tf.float32)
# state.shape

# 测试
X = tf.random.uniform((num_steps, batch_size, len(vocab)))
Y, state_new = rnn_layer(X, state)
print(Y.shape, len(state_new), state_new[0].shape)

# 封装RNN模块成一个keras的Layer
class My_RNN_Layer(tf.keras.layers.Layer):
    def __init__(self, rnn_layer, vocab_size):
        super(My_RNN_Layer, self).__init__()
        self.rnn = rnn_layer
        self.vocab_size = vocab_size
        self.dense = tf.keras.layers.Dense(vocab_size)  # 输出层

    def call(self, inputs, state):
        X = tf.one_hot(tf.transpose(inputs), self.vocab_size)  # 这里的transpose是和d2l的time machine的数据有关
        # rnn返回两个以上的值
        Y, *state = self.rnn(X, state)
        output = self.dense(tf.reshape(Y, (-1, Y.shape[-1])))
        return output, state
        
    def begin_state(self, *args, **kwargs):
        return self.rnn.cell.get_initial_state(*args, **kwargs)

# 训练与预测
device_name = d2l.try_gpu()._device_name
strategy = tf.distribute.OneDeviceStrategy(device_name)
with strategy.scope():
    net = My_RNN_Layer(rnn_layer, vocab_size=len(vocab))
# 先对未训练网络进行一次预测
d2l.predict_ch8('time traveller', 10, net, vocab)
# 具体的网络训练
num_epochs, lr = 500, 1
d2l.train_ch8(net, train_iter, vocab, lr, num_epochs, strategy)






