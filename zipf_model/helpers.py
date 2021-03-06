import re
from concurrent.futures import ThreadPoolExecutor


def create_key_stroke_to_cust_line_table(customer_service_line_key, 
                                         number_of_chars_in_ngram, 
                                         corpus_ctr_dict, 
                                         lookup_table={}
                                         ):
    '''
    It walks through the n-gram string character-by-character and creates a dictionary 
    of all the possible lines this sequence of keystrokes could be leading to
    e.g.

        g {u'great was my pleasure helping you': 1}
        gr {u'great was my pleasure helping you': 1}
        ...
        great was my {u'great was my pleasure helping you': 1}

    I: string written by the customer service rep, number of characters (int), frequency distribution dictionary
    O: master lookup of table (dictionary)
    '''
    
    
    #change to key_stroke_sequence
    for index in range(1, number_of_chars_in_ngram + 1):
        key_stroke_gram = customer_service_line_key[:index]
        count_of_this_particular_line = corpus_ctr_dict[customer_service_line_key]
        
        if key_stroke_gram not in lookup_table:
            
            lookup_table[key_stroke_gram] = {}
            lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line 
        
        # if the customer service line not in the lookup_table
        elif customer_service_line_key not in lookup_table[key_stroke_gram]:
            lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line
    
    return lookup_table

def find_num_chars_in_n_gram(target_str, number_of_grams):
    '''
    calculates the number of characters of a 
    the beginning ngram
    
    I: string, ngram size (int)
    O: length (int)
    '''
    
    return len(' '.join(target_str.split(' ')[:number_of_grams])) 

def format_suggestions_properly(list_of_strs):
    '''
    I: list of string
    O: properly formatted list of strings
    
    to dos
    ------
    * grammar corrections for punctuations
    '''
    output = []
    for str_ in list_of_strs:
        str_ = str_.capitalize()
        str_ = str_.replace(' i ', ' I ')

            
        #need to think about how to add grammar
        output.append(str_)
    return output



def retrieve_suggestions(key_strokes, look_up_table, top_x_lines):
    try:
        sub_dict_of_suggestions = look_up_table[key_strokes]

        #grabs the top X number of lines sorted by count (most popular)
        suggestions = sorted(sub_dict_of_suggestions.items(), key=lambda x:x[1], reverse=True)[:top_x_lines]

        return [tuple_[0] for tuple_ in suggestions]
    except KeyError:
        return None

def add_question_mark_or_period_to_sentence(target_str):
    '''
    Just adds a period or a question mark to the end of the string. 
    Hacky short term fix for the sentence type detection. 

    I: string
    O: formatted string
    '''
    
    if '?' in target_str: 
        return target_str
    
    begining_words_of_questions = {
        'what',
        'when',
        'will',
        'why',       
        'is',
        'have',
        'did',
        'will',
        'can',
        'do',
        'how',
        'could'
    }

    starting_word = target_str.split(' ', 1)[0]
    if starting_word in begining_words_of_questions:
        return target_str + '?'
    else:
        if target_str[-1] != '.': return target_str + '.'
    return target_str


def multithread_map(fn, work_list, num_workers=50):
    '''
    spawns a threadpool and assigns num_workers to some 
    list, array, or any other container. Motivation behind 
    this was for functions that involve scraping.
    '''

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        return list(executor.map(fn, work_list))

ABREVIATIONS_DICT = {
    "'m":' am',
    "'ve":' have',
    "'ll":" will",
    "'d":" would",
    "'s":" is",
    "'re":" are",
    "  ":" ",
    "' s": " is",
}

def multiple_replace(text, adict=ABREVIATIONS_DICT):
    '''
    Does a multiple find/replace
    '''
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)


def custome_refine(target_str):
    words_to_replace = {
    'welcomed': 'welcome'
    }

    return multiple_replace(target_str, words_to_replace)
