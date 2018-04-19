from keras import Sequential
from keras.layers import LSTM


def state2score(input_shape=(None, 200, 176, )):
    model = Sequential()
    model.add(LSTM(batch_input_shape=input_shape,
                   units=1,
                   return_sequences=False))
    model.compile(optimizer='adam', loss='mse')
    return model


def config2state(input_shape=(33,)):
    raise NotImplementedError()
