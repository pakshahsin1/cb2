from flask import Flask, request, jsonify
import os
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import random
from keras.models import load_model
import json
import pickle

# Initialize Flask app
app = Flask(__name__)

# Load data and model
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

model = load_model('/mnt/data/models/chatbot_model.h5')
intents = json.loads(open('/mnt/data/models/buttons.json').read())
words = pickle.load(open('/mnt/data/models/words.pkl', 'rb'))
classes = pickle.load(open('/mnt/data/models/classes.pkl', 'rb'))
lemmatizer = WordNetLemmatizer()

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"found in bag: {w}")
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data['message']
    ints = predict_class(message, model)
    res = getResponse(ints, intents)
    return jsonify({"response": res})

if __name__ == '__main__':
    app.run(debug=True)
