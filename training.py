import nltk, random, json, pickle
# nltk.download('punkt');nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import tensorflow


class Training:
    def __init__(self):
        self.classes = None
        self.documents = None
        self.tags = None
        self.pattern = None
        self.words = None
        data_file = open('data/intents.json').read()
        # Load the  contents of the root element of data
        self.intents = json.loads(data_file)['intents']
        # Slice, categorize and sort data to form we will need
        self.select_data()

        self.train_data()

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
        self.tags = sorted(list(set(self.tags)))

    def train_data(self):
        cv = CountVectorizer(tokenizer=lambda txt: txt.split(), analyzer="word", stop_words=None)
        training = []
        for doc in self.documents:
            # Lower case and lemmatize the pattern words
            sentences = list(map(str.lower, doc[0]))
            # Complete sentence we are considering
            sentences = ' '.join(list(map(nltk.stem.WordNetLemmatizer().lemmatize, sentences)))

            # Mark words included in the sentence as 1 int the collection of all words
            word_vector = cv.fit([' '.join(self.words)]).transform([sentences]).toarray().tolist()[0]

            # Make vector of 0 of the amount of all tags
            mark_tags = [0] * len(self.tags)
            # If the sentence is marked by one of the tags mark 1 in the vector
            mark_tags[self.tags.index(doc[1])] = 1

            # Add matching pair of words included and the tags that are associated with it
            training.append([word_vector, mark_tags])

        # Shuffle the output, so it is possible to change input data
        random.shuffle(training)
        training = np.array(training, dtype=object)
        train_x = list(training[:, 0])  # sentences
        train_y = list(training[:, 1])  # tags

        return train_x, train_y


train = Training()
