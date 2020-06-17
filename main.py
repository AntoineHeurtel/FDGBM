#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
# version 1.1-beta
##########################################################
import os
import src.parser as parser
import src.blast as blast

from src.logger import logger as log
from src.logger import args


#define dico for us data
collection = {} #contain import data from database like InnateDB and Uniprot
blastData = {} #contain data parsed from xml file blast

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
    if args.fasta and verifFile(args.fasta):
        log.info('export data in ' + args.fasta)
        if args.number:
            blast.exportFasta(collection, args.fasta, int(args.number))
        else:
            blast.exportFasta(collection, args.fasta)
    #parse a xml file
    if args.blast:
        for file in args.blast:
            log.info('parsing a xml blast result')
            blast.tblastn(file, blastData)
        #export data parsed from xml
        if args.output and verifFile(args.output):
            #make a dico contain parameters use to filter data
            #recall : parameters availables are : eValue, identity, positive, cover and number
            #consult README for more informations
            #filter = {'eValue':args.evalue, 'idt':args.identity, 'pst':args.positive,'cover':args.cover, 'number':args.number}
            filter = {'idt':args.identity}
            parsedData = blast.parser(blastData, filter)
            blast.export(args.output, parsedData)

log.debug("end code")
