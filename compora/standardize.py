#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2021-04-29 16:32
#
# This source code is licensed under the WTFPL license found in the
# LICENSE file in the root directory of this source tree.


import regex as re


def standardize(sentence, language):
    return standardize_punctuation(sentence, language)


def standardize_punctuation(sentence, language):
    # General Punctuation
    sentence = re.sub(r'\(', ' (', sentence)
    sentence = re.sub(r'\)', ') ', sentence)
    sentence = re.sub(r'\( ', '(', sentence)
    sentence = re.sub(r' \)', ')', sentence)
    sentence = re.sub(r' ([\.\?%!,:;])', '\g<1>', sentence)

    # Quotation Punctuation
    re.sub(r'\'\'', '"', sentence)
    if language in {'en', }:
        # English "quotation," followed by comma, style
        sentence = re.sub(r'"([\.,]+)', '\g<1>"', sentence)
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
