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
