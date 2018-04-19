import os
import random
import pickle
import numpy as np
from keras import Sequential
from keras.layers import LSTM, GRU
from keras.optimizers import Adam


def state2score(input_shape=(None, 200, 176, )):
    model = Sequential()
    model.add(GRU(batch_input_shape=input_shape,
                   activation='relu',
                   units=1,
                   return_sequences=False))
    model.compile(optimizer=Adam(lr=1e-2), loss='mse')
    return model


def load_pickle(record_id):
    returns = None
    file_path = os.path.join('./records', 'memory-' + str(record_id) + '.pkl')
    with open(file_path, 'rb') as pkl_file:
        tmp_queue = pickle.load(pkl_file)
    return tmp_queue


def main():
    function_g = state2score()

    while True:
        states = []
        scores = []
        cur_id = random.randint(1, 6)
        print('id=' + str(cur_id))
        records = load_pickle(cur_id)
        for record in records:
            config, state, score = record
            #print(score)
            states.append(state)
            scores.append(score)

        function_g.fit(np.array(states), np.array(scores), batch_size=len(scores), epochs=10, validation_split=0.2)


if __name__ == '__main__':
    main()
