import pkuseg


class Segmenter(object):
    def __init__(self, language):
        self.language = language
        if language == 'zh':
            self.segmenter = pkuseg.pkuseg()

    def cut(self, sentence):
        if self.language == 'zh':
            return ' '.join(self.segmenter.cut(sentence))
        else:
            return sentence
