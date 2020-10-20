'''
@description: 
    Generate Sports articles using Tensorflow's LSTM RNN!
    Final project for Auburn University's COMP 5660.
@author(s):
    Omar Barazanji
@date: 
    10/19/2020
@sources: 
    https://www.neuralnine.com/generating-texts-with-recurrent-neural-networks-in-python/
'''

import random
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.layers import Activation, Dense, LSTM

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) # turn off errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.seterr(divide = 'ignore') 

class LSTM_RNN:
    def __init__(self, article_count=0):
        self.count = article_count
        self.text = ''
        self.length_seq = 50
        self.model = Sequential()

    # from official Keras docs
    def sample(self, preds, temperature=1.0):
        predictions = np.asarray(preds).astype('float64')
        predictions = np.log(predictions) / temperature
        exp_preds = np.exp(predictions)
        predictions = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, predictions, 1)
        return np.argmax(probas)

    # from official Keras docs
    def generate_text(self, length, temperature):
        start_index = random.randint(0, len(self.text) - self.length_seq - 1)
        generated = ''
        sentence = self.text[start_index: start_index + self.length_seq]
        generated += sentence
        for i in range(length):
            x_predictions = np.zeros((1, self.length_seq, len(self.characters)))
            for t, char in enumerate(sentence):
                x_predictions[0, t, self.char_to_ndx[char]] = 1

            predictions = self.model.predict(x_predictions, verbose=0)[0]
            next_index = self.sample(predictions,
                                    temperature)
            next_character = self.ndx_to_char[next_index]

            generated += next_character
            sentence = sentence[1:] + next_character
        print("Robot says: \n")
        print("\n")
        return generated

    def grab_text(self, cached=True):
        str_size = 7
        big_text = ''

        if not cached:
            for article_num in range(1,self.count+1):
                artical_title = str(article_num)
                article = artical_title.rjust(str_size,'0')
                with open("./database/news_%s.json" % (article), 'r') as f:
                    try:
                        data = json.load(f)
                    except UnicodeDecodeError:
                        continue
                with open("./texts/news_%s.txt" % (article), 'w') as w:
                    w.write(data['text'])
                    big_text += " %s" % (data['text'])
            with open('text.txt', 'w') as w:
                w.write(big_text)

        self.text = open("text.txt", 'rb').read().decode(encoding='utf-8').lower()
        self.characters = sorted(set(self.text))
        self.char_to_ndx = dict((c, i) for i, c in enumerate(self.characters))
        self.ndx_to_char = dict((i, c) for i, c in enumerate(self.characters))

    def train(self):
        step = 2
        sentences = []
        next_char = []

        for i in range(0, len(self.text) - self.length_seq, step):
            segment = self.text[i: i+self.length_seq]
            sentences.append(segment)
            next_char.append(self.text[i+self.length_seq])

        x = np.zeros((len(sentences), self.length_seq, len(self.characters)), dtype=np.bool)
        y = np.zeros((len(sentences), len(self.characters)), dtype=np.bool)

        for i, sent in enumerate(sentences):
            for t, char in enumerate(sent):
                x[i, t, self.char_to_ndx[char]] = 1
            y[i, self.char_to_ndx[next_char[i]]] = 1


        # building RNN
        self.model.add(LSTM(128, input_shape=(self.length_seq, len(self.characters))))
        self.model.add(Dense(len(self.characters)))

        # scales values to add up to 100%
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01))
        self.model.fit(x, y, batch_size=256, epochs=4)

        # run this once
        self.model.save('textgen.model')



if __name__ == "__main__":
    initial = False # Change to true if first time...

    print("Please wait while the robot types a story...\n")

    if initial: # initial setup
        network = LSTM_RNN(3000)
        network.grab_text()
        network.train()

    else:       # run pre-trained neural network
        network = LSTM_RNN(3000)
        network.grab_text(cached=False)
        network.model = tf.keras.models.load_model('textgen.model')

    print(network.generate_text(3000, 1.0))
    print("\n The end.\n")
