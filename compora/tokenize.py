import re
from yoolkit.xmlscape import encode, decode
from yoolkit.text import unicode_category

from compora.nb_prefix import nb_prefix


def tokenize(sentence, language, split_aggressive_hyphen=True):
    # seperate out all special characters that are not in 'L' and 'Nd' categories
    sentence = encode(sentence)
    sentence = re.sub(r'([^\w\d\s\'\-,.])', ' \g<1> ', sentence)

    if split_aggressive_hyphen:
        sentence = re.sub(r'([\w\d])-(?=[\w\d])', '\g<1> @-@ ', sentence) 

    # Do not split multi-dots
    sentence = re.sub(r'\.(\.+)', ' MULTIDOT\g<1>', sentence)
    while re.search(r'MULTIDOT\.', sentence) is not None:
        sentence = re.sub(r'MULTIDOT\.([^\.])', 'MULTIMULTIDOT \g<1>', sentence)
        sentence = re.sub(r'MULTIDOT\.', 'MULTIMULTIDOT', sentence)

    # if pattern is not the form of digit,digit, seperate ','
    sentence = re.sub(r'([^\d]),', '\g<1> , ', sentence)
    sentence = re.sub(r',([^\d])', ' , \g<1>', sentence)

    sentence = re.sub(r'([\d]),$', '\g<1> ,', sentence)

    # split contractions
    if language in {'en', }:
        # right side split
        sentence = re.sub(r'([^\w])\'([^\w])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\w])\'([^\w])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([^\w\d])\'([\w])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([\w])\'([\w])', '\g<1> \'\g<2>', sentence)
        sentence = re.sub(r'([\d])\'([s])', '\g<1> \'\g<2>', sentence)
    elif language in {'fr', 'it', 'ga'}:
        # left side split
        sentence = re.sub(r'([^\w])\'([^\w])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\w])\'([^\w])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([^\w])\'([\w])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\w])\'([\w])', '\g<1>\' \g<2>', sentence)

    else:
        sentence = re.sub(r'\'', '\' ', sentence)

    words = sentence.split()
    for index in range(len(words)):
        word = words[index]
        if re.search(r'^(\S+)\.$', word) is not None:
            prefix = re.search(r'^(\S+)\.$', word).group(1)
            if re.search(r'\.', prefix) and re.search(r'\w', prefix):
                pass
            elif prefix in nb_prefix[language]['1']:
                pass
            elif index < len(words) - 1 and unicode_category(words[index+1][0]) == 'Ll':
                pass
            elif prefix in nb_prefix[language]['2'] and index < len(words) - 1 and re.search(r'^[0-9]+', words[index+1]):
                pass
            else:
                word = prefix + ' .'
        words[index] = word
    sentence = ' '.join(words)
    sentence = ' '.join(sentence.split())
    sentence = re.sub(r'\.\' ?$', ' . \' ', sentence)

    while re.search(r'MULTIMULTIDOT', sentence):
        sentence = re.sub(r'MULTIMULTIDOT', 'MULTIDOT.', sentence)
    sentence = re.sub(r'MULTIDOT', '.', sentence)
    sentence = decode(sentence)

    return sentence
