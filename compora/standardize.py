import re


def standardize(sentence, language):
    return standardize_punctuation(sentence, language)


def standardize_punctuation(sentence, language):
    # General Punctuation
    sentence = re.sub(r'\(', ' (', sentence)
    sentence = re.sub(r'\)', ') ', sentence)
    sentence = re.sub(r'\( ', '(', sentence)
    sentence = re.sub(r' \)', ')', sentence)
    sentence = re.sub(r' ([%:;,.!?])', '\g<1>', sentence)

    # Quotation Punctuation
    re.sub(r'\'\'', '"', sentence)
    if language in {'en', }:
        # English "quotation," followed by comma, style
        sentence = re.sub(r'"([,.]+)', '\g<1>"', sentence)
    if language in {'cs', 'cz'}:
        # Czech is confused
        pass
    if language in {'de', 'es', 'fr', 'zh'}:
        # German/Spanish/French/Chinese "quotation", followed by comma, style
        sentence = re.sub(r',"', '",', sentence)
        sentence = re.sub(r'(\.+)"(\s*[^<])', '"\g<1>\g<2>', sentence)# Don't fix period at end of sentence

    # Numerical Punctuation
    if language in {'de', 'es', 'cz', 'cs', 'fr'}:
        sentence = re.sub(r'(\d) (\d)', '\g<1>,\g<2>', sentence)
    else:
        sentence = re.sub(r'(\d) (\d)', '\g<1>.\g<2>', sentence)

    return sentence
