#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
##########################################################
import src.logger as logger
import src.parser as parser


#####
# Parser
#####
collection = {}

parser.uniprotDbGene(collection, 'data/test.xml', "test")

print(len(collection))
