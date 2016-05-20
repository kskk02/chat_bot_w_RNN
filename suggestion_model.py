import json
import nltk.data
import spell_checker

class Suggestion_Generator(object):
    '''
    This class builds a retrieval based chatbot 
    and it's based off a frequency of n-grams in 
    a target corpus of text. It uses the reverse of 
    zipf's law to predict sentences by each key 
    stroke.

    Methods
    --------
    train
    predict
    read_in_corpus
        I: file name
        O: list
    print_corpus
        I: 
        O: print to text file or screen
    '''
    
    corpus = []
    
    def train(self, target_corpus_filename, filename_for_storage='n_gram_frequencies_dict.pkl'):
        
        #read
        self.corpus = self.read_in_corpus(target_corpus_filename)

        #preprocess
        self.corpus = self.preprocess(self.corpus)
        
        #make counter dict
        self.key_stroke_lookup_table = self.create_frequency_dict()
    
    def create_frequency_dict(self):
        key_stroke_lookup_table = {}

        #change: line_frequency_table
        corpus_ctr_dict = Counter(self.corpus)

        for customer_service_line_key in corpus_ctr_dict.keys():

            number_of_chars_in_ngram = find_num_chars_in_n_gram(customer_service_line_key, 3)
            key_stroke_lookup_table = create_key_stroke_to_cust_line_table(customer_service_line_key, number_of_chars_in_ngram, corpus_ctr_dict, key_stroke_lookup_table)

        #saving lookup table
        cPickle.dump(key_stroke_lookup_table, open('key_stroke_lookup_table.pkl','wb'))

        return key_stroke_lookup_table

    
    def read_in_corpus(self, target_corpus_filename):
        '''
        alternative options to read-in the json would've been pandas 
        but that would be very unassuming to size of the file.
        '''

        corpus_json = json.load(open(target_corpus_filename))
        Issues_json = corpus_json['Issues']
        all_customer_service_lines = []

        for issue_dialogue in Issues_json:
            customer_service_lines = [message['Text'] for message in issue_dialogue['Messages'] \
             if not message['IsFromCustomer']]

            all_customer_service_lines.extend(customer_service_lines)

        return all_customer_service_lines

    def find_suggestions(key_stroke_sequence_str, top_x_lines=5):
        '''
        I: key stroke sequence e.g 'what th' (string), max number of suggestions (int) 
        O: suggestions that attempt to accurately complete the key stroke sequence (list of strings)
        '''

        look_this_up = key_stroke_sequence_str.lower()
        number_of_words = len(key_stroke_sequence_str.split())

        if number_of_words <= 2:

            #pull up the most frequently occuring line
            most_frequent_lines = retrieve_suggestions(look_this_up, key_stroke_lookup_table, top_x_lines)

        else:   

            #truncate the target sequence of key strokes to the first tri-gram
            #perhaps we could have something similar in our lookup table
            len_of_key_strokes = find_num_chars_in_n_gram(look_this_up, 3)
            truncated_key_strokes = look_this_up[:len_of_key_strokes - 1]
            most_frequent_lines = retrieve_suggestions(truncated_key_strokes, key_stroke_lookup_table, top_x_lines)

        return most_frequent_lines

    
    def preprocess(self, corpus):
        '''
        This iterates through the corpus line by line tokenizing, 
        spellchecking, normalizing abbreviations, etc.

        I: list of text strings
        O: preprocessed list of text strings

        It's debatable how you want to tokenize, I chose to do it by sentence
        but it could be done with regex like so "[\w' ]+" which would give you 
        smaller phrases.

        to dos:
        -------
        * fix grammar
        * remove first names
        * think about how to deal with punctuation
        * find nltk package to replace abbreviations
        * removing infrequent terms potentially
        * multithread the spellchecker
        * iterate through with a string fuzzy matching algo to dedupe typos
        * unit tests
        '''
        
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        
                                    #lowercase and tokenize by sentence
        corpus_formatted = [tokenized_line for line in corpus \
                            for tokenized_line in sent_detector.tokenize(line.strip().lower())]

        #expanding the abreviations
        corpus_formatted_expanded = [abreviation_expander(line) for line in corpus_formatted]

        #spell check
        #note this function takes quite a bit of time
        corpus_formatted_expanded_correct = [' '.join([spell_checker.correct(word) for word in line.strip().split()]) 
                                             for line in corpus_formatted_expanded]
 
        
        return corpus_formatted_expanded_correct
