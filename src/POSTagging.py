import pandas
import pickle
import nltk
from collections import Counter

def pos_tagging(csv_path):
    # load the csv file
    df = pandas.read_csv(csv_path)

    nltk.download('punkt')

    # load the pos tagging model (or alternatively use the maxent_pos_tagger.pkl)
    with open('../models/pos_tagging/crf_pos_tagger.pkl', 'rb') as file:
        model = pickle.load(file)

    # extracts features for each word in a sentence
    def get_word_features(sentence, i):
        word = sentence[i]
        features = {
            'word': word,
            'is_first': i == 0,  # if the word is a first word
            'is_last': i == len(sentence) - 1,  # if the word is a last word
            'is_capitalized': word[0].upper() == word[0],
            'is_all_caps': word.upper() == word,  # word is in uppercase
            'is_all_lower': word.lower() == word,  # word is in lowercase
            # prefix of the word
            'prefix-1': word[0],
            'prefix-2': word[:2],
            'prefix-3': word[:3],
            # suffix of the word
            'suffix-1': word[-1],
            'suffix-2': word[-2:],
            'suffix-3': word[-3:],
            # extracting previous word
            'prev_word': '' if i == 0 else sentence[i - 1],
            # extracting next word
            'next_word': '' if i == len(sentence) - 1 else sentence[i + 1],
            'has_hyphen': '-' in word,  # if word has hyphen
            'is_numeric': word.isdigit(),  # if word is in numeric
            'capitals_inside': word[1:].lower() != word[1:]  # if capital letters in word
        }
        return features

    # predict POS tags for a sentence
    def predict_pos_tags(sentence, input_model):
        features = [get_word_features(sentence, i) for i in range(len(sentence))]
        # if CRF model
        predicted_labels = input_model.predict([features])[0]
        # if MaxEnt model
        # predicted_labels = [input_model.classify(f) for f in features]
        return list(zip(sentence, predicted_labels))

    # get the x (or all by default) comments
    x = 100
    comments = df['Comment'].iloc[1:]  # excluding the first row (header)

    # initialize counters for nouns and adjectives
    noun_counter = Counter()
    adj_counter = Counter()

    # tokenize comments and predict POS tags
    for index, comment in enumerate(comments):
        if not isinstance(comment, str):
            print(f"Non-string comment at index {index}: {comment} (type: {type(comment)})")
            continue
        tokens = nltk.word_tokenize(comment)
        pos_tags = predict_pos_tags(tokens, model)

        # count nouns and adjectives
        nouns = [word for word, label in pos_tags
                 if label in ['NN', 'NNS'] and
                 word.lower() not in ['am', 'btw', 'get', 'youre', 'its', 'theres', 'whos', 'thats', 'i']]
        adjectives = [word for word, label in pos_tags
                      if label in ['JJ', 'JJR', 'JJS'] and
                      word.lower() not in ['more', 'many', 'other', 'such', 'much', 'own', 'im', 'cant', 'didnt', 'ive','u']]

        noun_counter.update(nouns)
        adj_counter.update(adjectives)

    # get top 100 most used nouns and adjectives
    top_100_nouns = noun_counter.most_common(100)
    top_100_adjectives = adj_counter.most_common(100)

    return top_100_nouns, top_100_adjectives
