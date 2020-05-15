#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
##########################################################
import os
import src.parser as parser
import src.blast as blast

from src.logger import logger as log
from src.logger import args


#####
# Functions
#####
def verifFile(filename):
    if os.path.exists(filename) and not args.force:
        log.warning(filename + " already exist, you can overwrite with -f option")
        return False
    elif os.path.exists(filename) and args.force:
        log.debug(filename + " will be overwrite")
        return True
    else:
        return True


#####
# Parser
#####
if args.COMMANDS == "parser":
    collection = {}
    #parsing a tsv file download from innateDB
    if args.innatedb:
        log.info("parsing file 'data/InnateDB_genes.tsv'")
        parser.innateDbGene(collection, args.innatedb)

    #parsing a xml file download from uniprot
    if args.uniprot:
        log.info("parsing file Uniprot")
        parser.uniprotDbGene(collection, args.uniprot)

    #save data in tsv file
    if args.output and verifFile(args.output):
        log.info('export data in ' + args.output)
        parser.writter(collection, args.output)


#####
# Load data
#####
if args.load and os.path.exists(args.load):
    log.info('load data from ' + args.load)
    collection = {}
    collection = parser.loadData(collection, args.load)
    log.info("Load " + str(len(collection)) + " genes")


#####
# blast
#####
if args.COMMANDS == 'blast':
    #generate a fasta file
    if args.output and verifFile(args.output):
        log.info('export data in ' + args.output)
        if args.number:
            blast.exportFasta(collection, args.output, int(args.number))
        else:
            blast.exportFasta(collection, args.output)


log.debug("end code")
