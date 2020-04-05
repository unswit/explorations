#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 21:11:53 2020

@author: rian-van-den-ander
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from keras.models import Sequential
from keras import layers
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np


def create_embedding_matrix(filepath, word_index, embedding_dim):
    vocab_size = len(word_index) + 1  # Adding again 1 because of reserved 0 index
    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    with open(filepath,encoding='utf-8') as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word]
                embedding_matrix[idx] = np.array(
                    vector, dtype=np.float32)[:embedding_dim]

    return embedding_matrix

df = pd.read_csv('../../data/aita/aita_clean.csv')

X = df['body'].values
X= np.char.lower(X.astype(str))
y = df['is_asshole'].values

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

#TODO: num_words constant here. how do I decide what to make it?
#5000: accuracy 72.5

tokenizer = Tokenizer(num_words=5000) 
tokenizer.fit_on_texts(X_train)
X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)
vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index

#500: accuracy 72.5%
#1000: 72.8%
#3000: 72.8%
maxlen = 1000
X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

input_dim = X_train.shape[1] # set feature dimensions

#Using glove:
#50 dimensions: 72.8%
#100 dimensions: 72.54
#lower amount of dimensions not an option

#TODO: using other embedding sources
#Glove: 51% embedding accuracy, 72.54% model accuracy
#Fasttext: 56%, 
embedding_dim = 300
#Glove: embedding_matrix = create_embedding_matrix('../../data/embedding/glove/glove.6B.50d.txt', tokenizer.word_index, embedding_dim)
embedding_matrix = create_embedding_matrix('../../data/embedding/fasttext/wiki-news-300d-1M-subword.vec', tokenizer.word_index, embedding_dim)

nonzero_elements = np.count_nonzero(np.count_nonzero(embedding_matrix, axis=1))
embedding_accuracy = nonzero_elements / vocab_size
print('embedding accuracy: ' + str(embedding_accuracy))

#TODO: fiddle with the size of these layers. maybe overnight grid search.
model = Sequential()
model.add(layers.Embedding(vocab_size, embedding_dim, input_length=maxlen, trainable=True))
model.add(layers.Conv1D(128, 5, activation='relu'))
model.add(layers.GlobalMaxPooling1D())
model.add(layers.Dense(10, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

res = model.fit(X_train, y_train, epochs=20, verbose=True, validation_data=(X_test, y_test), batch_size=10)

loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
print("Training Accuracy: {:.4f}".format(accuracy))
loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
print("Testing Accuracy:  {:.4f}".format(accuracy))