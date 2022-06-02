import nltk
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from tensorflow.python.keras.models import load_model


class Tester:
    def __init__(self):
        # Load data provided by the trainer and extract data which we will use
        # Set answer threshold, so chatbot won't output tag that is not sure
        data = pickle.load(open("data/training_data", "rb"))
        self.words = data['words']
        self.tags = data['tags']
        self.model = load_model('data/model.h5')
        self.answer_threshold = 0.5

    def provide_word_vector(self, sentence):
        # Initialize vector which will be returned
        word_vector = CountVectorizer(tokenizer=lambda txt: txt.split())
        # Tokenize, lemmatize and clear from symbols that doesn't matter provided sentence
        sentence_words = nltk.tokenize.word_tokenize(sentence.lower())
        sentence_words = list(map(nltk.stem.WordNetLemmatizer().lemmatize, sentence_words))
        sentence_words = list(filter(lambda x: x not in list("!@#$%^&*?"), sentence_words))
        # Vector functions require as to add ' '
        sentence_words = ' '.join(sentence_words)
        words = ' '.join(self.words)
        # It marks as 0 and 1 words that were used in the sentence
        word_vector = word_vector.fit([words]).transform([sentence_words]).toarray().tolist()[0]
        return np.array(word_vector)

    def classify(self, sentence):
        # Make probability of the tags, the sentence can belong to
        results = self.model.predict(np.array([self.provide_word_vector(sentence)]))[0]
        # Pack together indexes of tags and their probability and delete all below threshold
        results = list(map(lambda x: [x[0], x[1]], enumerate(results)))
        results = list(filter(lambda x: x[1] > self.answer_threshold, results))
        # Check if any tag was above threshold
        if len(results) > 0:
            # Sort tags by their probability, the best goes first
            results.sort(key=lambda x: x[1], reverse=True)
            # Return tag that is associated with the best matching index
            return self.tags[results[0][0]]
        # If none of the tags was good enough return None
        return None