#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2021-04-29 15:48
#
# This source code is licensed under the WTFPL license found in the
# LICENSE file in the root directory of this source tree.


import regex as re


from yoolkit.text import is_CJK_char


def detokenize(sentence, language):

    words = sentence.split()
    detokenized_sentence = ""
    prepend_space = ""
    quote_mark_count = dict()

    index = 0
    while index < len(words):
        if is_CJK_char(words[index][0]):
            if (index > 0 and is_CJK_char(words[index-1][-1])) and language in {'zh', 'ja', }:
                detokenized_sentence += words[index]
            else:
                detokenized_sentence += prepend_space + words[index]
            prepend_space = " "
        elif re.search(r'^[\p{Sc}\(\[\{¿¡]+$', words[index]):
            detokenized_sentence += prepend_space + words[index]
            prepend_space = ""
        elif re.search(r'^[\\\)\]\}\.\?%!,:;]+$', words[index]):
            if language in {'fr', } and re.search(r'^[\\\?%!:;]+$', words[index]):
                detokenized_sentence += " "
            detokenized_sentence += words[index]
            prepend_space = " "
        elif language in {'en', } and index > 0 and re.search('[\p{IsAlnum}]$', words[index-1]) and re.search(r'^[\'][\p{IsAlpha}]', words[index]):
            detokenized_sentence += words[index]
            prepend_space = " "
        elif language in {'cs', } and index > 1 and re.search('^[0-9]+$', words[index-2]) and re.search(r'^[.,]$', words[index-1]) and re.search(r'^[0-9]+$', words[index]):
            detokenized_sentence += words[index]
            prepend_space = " "
        elif language in {'fr', 'it', } and index < len(words)-1 and re.search('[\p{IsAlpha}][\']$', words[index]) and re.search(r'^[\p{IsAlpha}]', words[index+1]):
            detokenized_sentence += prepend_space + words[index]
            prepend_space = ""
        elif language in {'cs', } and index < len(words)-2 and re.search('[\p{IsAlpha}]$', words[index]) and re.search(r'^[\-–]$', words[index+1]) and re.search(r'^li$|^mail.*', words[index+2], flags=re.IGNORECASE):
            detokenized_sentence += prepend_space + words[index] + words[index + 1]
            prepend_space = ""
            index += 1
        elif re.search(r'^[\'\"„“`]+$', words[index]):
            normalized_quote_mark = words[index]
            if re.search(r'^[„“”]+$', words[index]):
                normalized_quote_mark = '"'
            if normalized_quote_mark not in quote_mark_count:
                quote_mark_count[normalized_quote_mark] = 0
            if language in {'cs', } and words[index] == "„":
                # This is always the starting quote in Czech
                quote_mark_count[normalized_quote_mark] = 0
            if language in {'cs', } and words[index] == "“":
                # This is usually the ending quote in Czech
                quote_mark_count[normalized_quote_mark] = 1
            if quote_mark_count[normalized_quote_mark] % 2 == 0:
                if language in {'en', } and words[index] == "'" and index > 0 and re.search(r'[s]$', words[index-1]):
                    detokenized_sentence += words[index]
                    prepend_space = " "
                else:
                    detokenized_sentence += prepend_space + words[index]
                    prepend_space = ""
                    quote_mark_count[normalized_quote_mark] += 1
            else:
                detokenized_sentence += words[index]
                prepend_space = " "
                quote_mark_count[normalized_quote_mark] += 1
        elif language in {'fi', } and re.search(r':$', words[index-1]) and re.search(r'^(N|n|A|a|Ä|ä|ssa|Ssa|ssä|Ssä|sta|stä|Sta|Stä|hun|Hun|hyn|Hyn|han|Han|hän|Hän|hön|Hön|un|Un|yn|Yn|an|An|än|Än|ön|Ön|seen|Seen|lla|Lla|llä|Llä|lta|Lta|ltä|Ltä|lle|Lle|ksi|Ksi|kse|Kse|tta|Tta|ine|Ine)(ni|si|mme|nne|nsa)?(ko|kö|han|hän|pa|pä|kaan|kään|kin)?$', words[index]):
            # Finnish : without intervening space if followed by case suffix
            # EU:N EU:n EU:ssa EU:sta EU:hun EU:iin ...
            detokenized_sentence += words[index].lower()
            prepend_space = " "
        else:
            detokenized_sentence += prepend_space + words[index]
            prepend_space = " "

        index += 1

    detokenized_sentence = ' '.join(detokenized_sentence.split())

    return detokenized_sentence


def merge_aggressive_hyphen(sentence):
    sentence = re.sub(r' @-@ ', '-', sentence) 
    return sentence
