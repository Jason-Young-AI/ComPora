#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2021-04-29 23:07
#
# This source code is licensed under the WTFPL license found in the
# LICENSE file in the root directory of this source tree.


import regex as re


from yoolkit.text import unicode_category

from compora.nb_prefix import nb_prefix


def tokenize(sentence, language):
    # seperate out all special characters that are not in 'L' and 'Nd' categories
    if language in {'fi', 'sv', }:
        # In Finnish and Swedish, the colon can be used inside words as an apostrophe-like character:
        # USA:n, 20:een, EU:ssa, USA:s, S:t
        sentence = re.sub(r'([^\p{IsAlnum}\s\'\-\.`,:])', ' \g<1> ', sentence)
        # If a colon is not immediately followed by lower-case characters, separate it out anyway
        sentence = re.sub(r'(:)(?=$|[^\p{Ll}])', ' \g<1> ', sentence)
    elif language in {'tdt', }:
        # In Tetun, the apostrophe can be used inside words as an apostrophe-like character:
        sentence = re.sub(r'([^\p{IsAlnum}\s\'\-\.`,])', ' \g<1> ', sentence)
        # If an apostrophe is not immediately followed by lower-case characters, separate it out anyway
        sentence = re.sub(r'(\')(?=$|[^\p{Ll}])', ' \g<1> ', sentence)
    elif language in {'ca', }:
        # In Catalan, the middle dot can be used inside words:
        # il·lusio
        sentence = re.sub(r'([^\p{IsAlnum}\s\'\-\.`,·])', ' \g<1> ', sentence)
        # If a middot is not immediately followed by lower-case characters, separate it out anyway
        sentence = re.sub(r'(·)(?=$|[^\p{Ll}])', ' \g<1> ', sentence)
    else:
        sentence = re.sub(r'([^\p{IsAlnum}\s\'\-\.`,])', ' \g<1> ', sentence)

    # Do not split multi-dots
    sentence = re.sub(r'\.(\.+)', ' MULTIDOT\g<1>', sentence)
    while re.search(r'MULTIDOT\.', sentence) is not None:
        sentence = re.sub(r'MULTIDOT\.([^\.])', 'MULTIMULTIDOT \g<1>', sentence)
        sentence = re.sub(r'MULTIDOT\.', 'MULTIMULTIDOT', sentence)

    # if pattern is not the form of digit,digit, seperate ','
    sentence = re.sub(r'([^\p{N}]),', '\g<1> , ', sentence)
    sentence = re.sub(r',([^\p{N}])', ' , \g<1>', sentence)

    sentence = re.sub(r'([\p{N}]),$', '\g<1> ,', sentence)

    # split contractions
    if language in {'en', }:
        # Contractions' right side split
        sentence = re.sub(r'([^\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([^\p{IsAlpha}\p{N}])\'([\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([\p{IsAlpha}])\'([\p{IsAlpha}])', '\g<1> \'\g<2>', sentence)

        # Special case for "1990's"
        sentence = re.sub(r'([\p{N}])\'([s])', '\g<1> \'\g<2>', sentence)

    elif language in {'fr', 'it', 'ga', 'ca', }:
        # Contractions' left side split
        sentence = re.sub(r'([^\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)

        sentence = re.sub(r'([^\p{IsAlpha}])\'([\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\p{IsAlpha}])\'([\p{IsAlpha}])', '\g<1>\' \g<2>', sentence)

    elif language in {'so', 'tdt', }:
        # Don't split glottals
        sentence = re.sub(r'([^\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([\p{IsAlpha}])\'([^\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)
        sentence = re.sub(r'([^\p{IsAlpha}])\'([\p{IsAlpha}])', '\g<1> \' \g<2>', sentence)

    else:
        sentence = re.sub(r'\'', '\' ', sentence)

    words = sentence.split()
    for index in range(len(words)):
        word = words[index]
        if re.search(r'^(\S+)\.$', word) is not None:
            prefix = re.search(r'^(\S+)\.$', word).group(1)
            if re.search(r'\.', prefix) and re.search(r'\p{IsAlpha}', prefix):
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

    return sentence


def split_aggressive_hyphen(sentence):
    sentence = re.sub(r'([\p{IsAlnum}])-(?=[\p{IsAlnum}])', '\g<1> @-@ ', sentence) 
    return sentence
