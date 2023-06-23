from nltk.corpus import stopwords,wordnet as wn
from nltk import ne_chunk, pos_tag, word_tokenize,sent_tokenize
from nltk.tree import Tree
from nltk.sentiment import SentimentIntensityAnalyzer
from gingerit.gingerit import GingerIt
from app import create_Node , predict_gender,create_relation,relationships
import truecase
import random
import socket

def synonyms(word):
    synonym=[]
    mysyn= wn.synsets(word)
    for syn in mysyn:
        # print(type(syn))
        for lemma in syn.lemmas():
            # print(type(lemma))
            # print(lemma)
            synonym.append(lemma.name())
    return synonym  

def autospellcorrect(query):
    if query[-1:]!='.':
        query= query+'.'
    parser=GingerIt()
    result=truecase.get_true_case(query)
    result= parser.parse(result)['result']
    return  result

def getstopwords(query):
    stopword = stopwords.words('english')
    word_tokens = set(word_tokenize(query))
    removing_stopwords = set(word_tokens)-set(stopword)
    return (removing_stopwords)

def getIpAdrress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    s = s.getsockname()[0]
    netaddres = ''
    count=0
    for bit in s:
        if bit=='.':
            count = count + 1
        netaddres = netaddres + bit
        if count==3:
            return netaddres
        
def replace_withname(query, name):
    tokens = word_tokenize(query)
    modified_tokens = []
    for token in tokens:
        if token.lower() in ['i', 'me', 'my', 'mine']:
            modified_tokens.append(name)
        else:
            modified_tokens.append(token)
    final_sent = " ".join(modified_tokens)
    print(final_sent)
    return final_sent

def Ner(text, user):
    print("ner called")
    text = replace_withname(text, user)
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    name_rel = []
    for nltk_result in nltk_results:
        if len(name_rel) == 3:
            create_relation(name_rel)
            name_rel.clear()
        if len(nltk_result) > 1:
            tag = nltk_result[1]
            if type(tag) != tuple:
                if tag.startswith("N") or tag.startswith("V"):
                    rel = relationships()
                    if nltk_result[0].upper() in rel:
                        name_rel.append(nltk_result[0].upper())
        if type(nltk_result) == Tree:
            for nltk_result_leaf in nltk_result.leaves():
                name_rel.append(nltk_result_leaf[0])
                gender = predict_gender(nltk_result_leaf[0])
                create_Node(nltk_result_leaf[0], gender)

def print_random_string(strings):
    random_string = random.choice(strings)
    return random_string

def get_definition(query):
    try:
        syno = synonyms(query)
        syn = wn.synsets(query)
        definition = syn[1].definition()
        if syn:
            return (definition + " or may we can say " + syno[0]).capitalize()
    except:
        return None
def chart(query):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(query)
    values=list(sentiment_scores.values())
    return values