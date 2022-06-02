import nltk
import random
import json
import pickle
# nltk.download('punkt');nltk.download('wordnet')
from keras.applications.densenet import layers
from keras.optimizers import SGD
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import tensorflow


class Training:
    def __init__(self):
        self.documents = None
        self.tags = None
        self.pattern = None
        self.words = None
        data_file = open('data/intents.json').read()
        # Load the  contents of the root element of data
        self.intents = json.loads(data_file)['intents']
        # Slice, categorize and sort data to form we will need
        self.select_data()
        self.create_model()

    def select_data(self):
        # Make lists of elements we will want to use, such as patterns which are input or tags which are category
        # for the input
        self.pattern = list(map(lambda x: x["patterns"], self.intents))
        self.words = list(map(nltk.tokenize.word_tokenize, nltk.flatten(self.pattern)))
        self.tags = nltk.flatten([[x["tag"]] * len(y) for x, y in zip(self.intents, self.pattern)])
        self.documents = list(map(lambda x, y: (x, y), self.words, self.tags))
        # Make words lowercase and delete signs that don't matter
        self.words = list(map(str.lower, nltk.flatten(self.words)))
        self.words = list(filter(lambda x: x not in list("!@#$%^&*?"), self.words))
        # Lemmatize words, which means making them their base form
        self.words = list(map(nltk.stem.WordNetLemmatizer().lemmatize, self.words))
        # Sort lists that were provided to this point
        self.words = sorted(list(set(self.words)))
        # Create and save model and data for later usage
        self.tags = sorted(list(set(self.tags)))

    def train_data(self):
        # Initialize vector that will let us mark splited words as 0 and 1
        word_vector = CountVectorizer(tokenizer=lambda txt: txt.split())
        training = []
        for doc in self.documents:
            # Lower case and lemmatize the pattern words
            sentences = list(map(str.lower, doc[0]))
            # Complete sentence we are considering
            sentences = ' '.join(list(map(nltk.stem.WordNetLemmatizer().lemmatize, sentences)))

            # Mark words included in the sentence as 1 int the collection of all words
            word_vector = word_vector.fit([' '.join(self.words)]).transform([sentences]).toarray().tolist()[0]

            # Make vector of 0 of the amount of all tags
            mark_tags = [0] * len(self.tags)
            # If the sentence is marked by one of the tags mark 1 in the vector
            mark_tags[self.tags.index(doc[1])] = 1

            # Add matching pair of words included and the tags that are associated with it
            training.append([word_vector, mark_tags])

        # Shuffle the output, so it is possible to change input data
        random.shuffle(training)
        training = np.array(training, dtype=object)
        sentences_output = list(training[:, 0])
        tags_output = list(training[:, 1])

        return sentences_output, tags_output

    def create_model(self):
        sentences_input, tags_input = self.train_data()
        # 3-layered model with dropouts at 0.5 to avoid overfitting
        model = tensorflow.keras.Sequential(
            [
                # RELU - if  x>0 ret x else ret 0
                layers.Dense(128, input_shape=(len(sentences_input[0]),), activation="relu", name="input_layer"),
                layers.Dropout(0.5),
                layers.Dense(64, activation="relu", name="hidden_layer"),
                layers.Dropout(0.5),
                # SOFTMAX - Return vector of probabilities that sum to 1
                layers.Dense(len(tags_input[0]), activation='softmax'),
            ]
        )
        # Decay = learning rate decay over each update
        # Nesterov momentum prevents us from going too fast and overshooting the optima
        # it lets us searching for it slower and more precisely
        # Momentum accelerates gradient descent in the relevant direction
        # Learning rate states for time to adapt to problem
        # the lower learning rate requires more epochs
        sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        # Metrics stands for our goal of evaluation
        # We set prepared optimizer
        # Loss function is set to categorical_crossentropy and measures the performance of the classification model
        # it is used to minimize the loss in our model
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        # Batch_size stands for number of samples per gradient update
        # Epoch is number of iterations for this model
        # Verbose used for now 1 - progress bar, 2 - one line per iteration, 0 - silent
        # The other two are input data and target data
        result_model = model.fit(np.array(sentences_input), np.array(tags_input), epochs=200, batch_size=10, verbose=1)
        # Save model and data that will be useful for prediction
        model.save('data/model.h5', result_model)
        pickle.dump({'words': self.words, 'tags': self.tags, 'sentences_input': sentences_input,
                     'tags_input': tags_input}, open("data/training_data", "wb"))


train = Training()
