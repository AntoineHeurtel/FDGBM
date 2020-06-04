#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to blast
##########################################################
import random
import requests
import time
import re
import xml.etree.ElementTree as ET

from src.logger import logger as log

##############################
# Class
##############################
class Query(dict):
    def __init__(self, number, name, lenght):
        self.number = number
        self.name = name
        self.lenght = lenght


class Hit():
    def __init__(self, id, name, scores, qSeq, hSeq, mSeq):
        self.id = id
        self.name = name
        self.scores = scores #dico
        self.qSeq = qSeq
        self.hSeq = hSeq
        self.mSeq = mSeq

        #add RefSeq if present in name
        if re.compile('X[MPR]\_[0-9]+.?[0-9]?').search(name):
            self.refseq = re.findall('X[MPR]\_[0-9]+.?[0-9]?', name)[0].rstrip()

    def __repr__(self):
        print(self.id)

##############################
# Fonctions
##############################
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
    with open(filename, 'w') as fileFasta:
        if number < 0:
            #gene random draw
            listGenes = []
            number = abs(number)
            count = number
            while count != 0:
                #random draw in data and make sur of gene have a sequence
                idGene = random.choice(list(data))
                if data[idGene].sequence != "" and idGene not in listGenes:
                    listGenes.append(idGene)
                    count -= 1
        else:
            listGenes = data.keys()
        count = 1
        for gene in listGenes:
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

def tblastn(file, blast):
    """
    parse a xml file result of a tblastn
    """
    count = 0 #counter of result in blast xml
    #verification if file is a xml
    f = open(file, 'r')
    header = f.readline()
    if '<?xml version="1.0"?>' not in header:
        log.critical("Make sure of your file is an xml")
        return False
    f.close()
    #initialisation for parsing file
    tree = ET.parse(file)
    root = tree.getroot()
    for iteration in root.findall('./BlastOutput_iterations/Iteration'):
        #a iteration is a query sequence
        numberQuery = int(iteration[0].text)
        name = iteration[2].text
        lenght = iteration[3].text
        blast[numberQuery] = Query(numberQuery, name, lenght)
        for hit in iteration[4]:
            #a hit is a resultat of blast, a hit in xml file
            id = hit[1].text
            queryDef = hit[2].text
            log.debug(queryDef)
            for hsp in hit[5]:
                #a hsp is result of blast hit, like sequence or score… ; is hit_hsps°in xml
                eValue = float(hsp.find('Hsp_evalue').text)
                gaps = int(hsp.find('Hsp_gaps').text)
                identity = int(hsp.find('Hsp_identity').text)
                positive = int(hsp.find('Hsp_positive').text)
                qSeq = hsp.find('Hsp_qseq').text
                mSeq = hsp.find('Hsp_midline').text
                hSeq = hsp.find('Hsp_hseq').text
                scores = {'eValue':eValue, 'gaps':gaps, 'identity':identity, 'positive':positive}
                blast[numberQuery][id] = Hit(id, queryDef, scores, qSeq, hSeq, mSeq)
                count += 1
    log.info(str(len(blast)) + ' sequences was submited')
    log.info(str(count) + ' sequences in total')

def printResult(blast, numberQuery, id, seq = False):
    bufferTexte = ''
    bufferTexte += id + '\t' + blast[numberQuery][id].name + '\n'
    if seq:
        bufferTexte += '\n' + blast[numberQuery][id].hSeq + '\n'
    return bufferTexte

def export(file, blast, filter):
    """
    Function to export data parsed from xml blast
    IN : dico blast : blast[numberQuery][id] = Hit(id, queryDef, scores, qSeq, hSeq, mSeq)
    OUT : file
    """
    def writer(file, text):
        """
        text must be a list (a tuple is better) with a header, the main content and a footer
        """
        file = open(file, 'w')
        delimiter = '\n'
        file.write(str(text[0]) + delimiter)
        if isinstance(text[1], list):
            for elementString in text:
                file.write(str(elementString) + delimiter)
        else:
            file.write(str(text[1]) + delimiter)
        file.write(str(text[2]) + delimiter)
        file.close

    bufferText = '' #text will write in file
    header = "FDGBM by Odd 2020\nresults parsed from a xmlFile tblastn\n"

    #requests in data
    totalCount = 0
    for numberQuery in blast:
        #blast[numberQuery] is an object
        count = 0
        listAccNCBI = []
        for id in blast[numberQuery]:
            #id === Hit_id
            if (filter['eValue'] is not None and blast[numberQuery][id].scores['eValue'] <= filter['eValue']) or (filter['idt'] is not None and blast[numberQuery][id].scores['identity'] >= filter['idt']) or (filter['pst'] is not None and blast[numberQuery][id].scores['positive'] >= filter['pst']):
                #prepare text
                #bufferText += printResult(blast, numberQuery, id)
                #list ncbi accession
                listAccNCBI.append(blast[numberQuery][id].refseq)
                count += 1
        totalCount += count
        #get isosoform from NCBI by accession
        isoformsList = []
        for accRefSeq in listAccNCBI:
            #url request to ncbi
            prefixUrl = 'https://www.ncbi.nlm.nih.gov/gene/?term='
            suffixUrl = '&report=gene_table&format=text'
            danny = True #is a simple boolean variable to requet ncbi…
            essai = 0 #number of try to request ncbi
            while danny:
                try:
                    r = requests.get(prefixUrl + accRefSeq + suffixUrl)
                    if r.ok:
                        danny = False
                except Exception as e:
                    log.debug(e.code)
                    if essai < 5:
                        time.sleep(5)
                        essai += 1
                    else:
                        danny = False
            #regex to parse text
            ##regex = variant.*(X[MPR]\_[0-9]+.?[0-9]?)
            isoformsList.append(re.findall('variant.*(X[MPR]\_[0-9]+.?[0-9]?)', r.text))
        #remove isoform if in listAccNCBI
        goodListAccNCBI = []
        for accRefSeq in listAccNCBI:
            if accRefSeq not in isoformsList:
                goodListAccNCBI.append(accRefSeq)
        #finish for a query
        #export results
        footer = 'Total hits found = ' + str(totalCount)
        writer(str(blast[numberQuery].name) + '.txt', [header, goodListAccNCBI, footer])
        log.info(str(count) + ' hits found for id ' + str(blast[numberQuery].name))
