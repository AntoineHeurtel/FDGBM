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


#define dico for us data
collection = {}

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
# Load data
#####
if args.load:
    for file in args.load:
        if os.path.exists(file):
            log.info('load data from ' + file)
            parser.loadData(collection, file)
    log.info("Load " + str(len(collection)) + " genes")


#####
# Parser
#####
if args.COMMANDS == "parser":
    #parsing a tsv file download from innateDB
    if args.innatedb:
        for file in args.innatedb:
            #to take multi file
            log.info("parsing file InnateDB")
            parser.innateDbGene(collection, file)

    #parsing a xml file download from uniprot
    if args.uniprot:
        for file in args.uniprot:
            #to take multi file
            log.info("parsing file Uniprot")
            parser.uniprotDbGene(collection, file)

    #save data in tsv file
    if args.output and verifFile(args.output):
        log.info('export data in ' + args.output)
        parser.writter(collection, args.output)


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
