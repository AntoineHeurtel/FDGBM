#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
##########################################################
import os
import src.parser as parser

from src.logger import logger as log
from src.logger import args


#####
# Functions
#####
def verifFile(filename):
    if os.path.exists(filename) and not args.force:
        log.warning(filename + " already exist")
        return False
    elif os.path.exists(filename) and args.force:
        log.debug(filename + " will be overwrite")
        return True
    else:
        return True

#####
# Parser
#####
log.debug("Start")
collection = {}

log.info("parsing file 'data/InnateDB_genes.tsv'")
parser.innateDbGene(collection, 'data/InnateDB_genes.tsv')

print(len(collection))

if args.output and verifFile(args.output):
    parser.writter(collection, args.output)
log.debug("end")
