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

#log.info("parsing file 'data/InnateDB_genes.tsv'")
#parser.innateDbGene(collection, 'data/InnateDB_genes.tsv')

log.info("parsing file Uniprot")
parser.uniprotDbGene(collection,'data/Uniprot_immune_HomoSapiens.xml',"immunite")
print(len(collection))

#if args.output and verifFile(args.output):
#    log.info('export data in ' + args.output)
#    parser.writter(collection, args.output)

#if args.load and verifFile(args.load):
#    log.info('load data from ' + args.load)
#    collection = {}
#    collection2 = parser.loadData(collection, args.load)
#    print(collection2)
log.debug("end")
