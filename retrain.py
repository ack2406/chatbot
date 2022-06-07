import json

import nltk

import training


class Retrain:
    def __init__(self):
        self.tags = None
        self.sets_of_words = None
        self.intents = None
        self.pattern = None

    def on_train(self):
        sentence = input("Write sentence: ")
        data_file = open('data/intents.json').read()
        # Load the  contents of the root element of data
        self.intents = json.loads(data_file)['intents']
        self.pattern = list(map(lambda x: x["patterns"], self.intents))
        # Extract sets of words for sentences that are already in file
        self.sets_of_words = list(map(nltk.tokenize.word_tokenize, nltk.flatten(self.pattern)))
        # Clear the provided sentence to normalized form we need
        sentence = self.clear_sentence(sentence)
        tmp = list(map(nltk.tokenize.word_tokenize, nltk.flatten(sentence)))
        # Check if set based on provided sentence matches any normalized set from out file
        for i in self.sets_of_words:
            sentence_tmp = list(map(str.lower, i))
            sentence_tmp = list(filter(lambda x: x not in list("!@#$%^&*?"), sentence_tmp))
            sentence_tmp = list(map(nltk.stem.WordNetLemmatizer().lemmatize, sentence_tmp))
            # If we managed to find this sentence we stop here, because we don't want to multiply
            # same sentences in the file
            if tmp[0] == sentence_tmp:
                print("This sentence is already in the file")
                return
        # If the sentence was not found we normalize all tags from our data
        self.tags = list(map(lambda x: x["tag"], self.intents))
        self.tags = list(map(str.lower, self.tags))
        self.tags = list(filter(lambda x: x not in list("!@#$%^&*?"), self.tags))
        self.tags = list(map(nltk.stem.WordNetLemmatizer().lemmatize, self.tags))
        # We provide and clear tag which we are interested in
        tag = input("Write tag: ")
        tag = self.clear_sentence(tag)
        # We use counter so we will be able to know on which index the existing tag is
        counter = 0
        for t in self.tags:
            # If we find matching tag we load data from the file and add element to list that is associated
            # with this tag
            # Then switch the content of the file for content with out changed list
            if t == tag:
                with open('data/intents.json', 'r+') as json_file:
                    file_data = json.load(json_file)
                    print(file_data)
                    file_data["intents"][counter]["patterns"].append(sentence)
                    print(file_data)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=1)
                training.Training()
                break
            counter = counter + 1
        # If we didn't match any of the existing tags with the provided one
        # We are asked to write response and append the whole content to the file
        else:
            response = input("Write response: ")
            response = list(map(str.lower, response))
            response = list(filter(lambda x: x not in list("!@#$%^&*?"), response))
            response = list(map(nltk.stem.WordNetLemmatizer().lemmatize, response))
            response = "".join(response)
            with open('data/intents.json', 'r+') as json_file:
                file_data = json.load(json_file)
                file_data['intents'].append({
                    "tag": tag,
                    "patterns": [sentence],
                    "responses": [response]
                })
                json_file.seek(0)
                json.dump(file_data, json_file, indent=1)
            training.Training()
        print("Trained Successfully")

    # Clear provided sentence, that is tokenize, lowerize, lemmatize it and remove certain characters
    # and then join it with spaces and return it
    def clear_sentence(self, sentence):
        sentence_words = nltk.tokenize.word_tokenize(sentence.lower())
        sentence_words = list(map(nltk.stem.WordNetLemmatizer().lemmatize, sentence_words))
        sentence_words = list(filter(lambda x: x not in list("!@#$%^&*?"), sentence_words))
        sentence_words = ' '.join(sentence_words)
        return sentence_words


retrainer = Retrain()

retrainer.on_train()
