import nltk
import re

def find_relationship(sentence):
    person_regex = r'([A-Z][a-zA-Z]+)'
    relationship_regex = r'(is|are|was|were|be|being|been|am)'
    
    tokens = nltk.word_tokenize(sentence)
    pos_tags = nltk.pos_tag(tokens)
    
    person1 = None
    person2 = None
    for word, pos in pos_tags:
        if re.match(person_regex, word) and pos == 'NNP':
            if person1 is None:
                person1 = word
            else:
                person2 = word
    
    if person1 is not None and person2 is not None:
        relationship = None
        for word, pos in pos_tags:
            if re.match(relationship_regex, word.lower()):
                relationship = word
                break
        
        if relationship is not None:
            relationship_statement = f"{person1} {relationship} {person2}"
            return relationship_statement
    
    return "Unable to determine the relationship"

# Example usage
sentence = "John is the brother of Mary"
result = find_relationship(sentence)
print(result)
