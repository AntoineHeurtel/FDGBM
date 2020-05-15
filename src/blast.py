#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to blast
##########################################################
from src.logger import logger as log

def fasta(header, sequence, lenght=80):
    """
    Make a header and sequence line in fasta format
    Default lenght lines are 80
    IN : header (str) + sequence (str) + lenght (int)
    """
    line = '>' + header + '\n'
    count = 1
    for ncl in sequence:
        if count % lenght == 0:
            line += '\n'
            count = 1
        else:
            line += ncl
            count += 1
    return line

def exportFasta(data, filename, number=0):
    """
    create a fasta file
    """
    count = 1
    with open(filename, 'w') as fileFasta:
        for gene in data:
            if data[gene].sequence != "":
                if number == 0:
                    line = fasta(data[gene].name, data[gene].sequence)
                    fileFasta.write(line + '\n')
                    count += 1
                if number > 0 and count <= number:
                    line = fasta(data[gene].name, data[gene].sequence)
                    fileFasta.write(line + '\n')
                    count += 1
            log.debug("gene " + data[gene].name + " exported")
    log.info(str(count-1) + " gene(s) exported")
