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
import json
import os
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

    def __repr__(self):
        print(self.number + ' ' + self.name)


class Hit():
    def __init__(self, id, name, scores, qSeq, hSeq, mSeq, hSeqLen):
        self.id = id
        self.name = name
        self.scores = scores #dico
        self.qSeq = qSeq
        self.hSeq = hSeq
        self.mSeq = mSeq
        self.lenght = hSeqLen

        #add RefSeq if present in name
        if re.compile('[XN][MPR]\_[0-9]+.?[0-9]?').search(name):
            self.refseq = re.findall('[XN][MPR]\_[0-9]+.?[0-9]?', name)[0].rstrip()#or regex [A-Z][A-Z]\_[0-9]+.?[0-9]?
        else:
            self.refseq = ''
            log.warning(f"Hit {self.id}, {self.name} not have refseq")
        #add specie if present
        if re.compile('PREDICTED: ([A-z]+.[A-z]+)').search(name):
            self.specie = re.findall('PREDICTED: ([A-z]+.[A-z]+)', name)[0].rstrip()
        else:
            self.specie = 'unknow'
            log.warning(f"Hit {self.id}, {self.name} not have specie")

    def __repr__(self):
        print(self.id + ' ' + self.name)

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
                hSeqLen = int(hsp.find('Hsp_align-len').text)
                scores = {'eValue':eValue, 'gaps':gaps, 'identity':identity, 'positive':positive}
                blast[numberQuery][id] = Hit(id, queryDef, scores, qSeq, hSeq, mSeq, hSeqLen)
                count += 1
    log.info(str(len(blast)) + ' sequences was submited')
    log.info(str(count) + ' sequences in total')

def printResult(blast, numberQuery, id, seq = False):
    bufferTexte = ''
    bufferTexte += id + '\t' + blast[numberQuery][id].name + '\n'
    if seq:
        bufferTexte += '\n' + blast[numberQuery][id].hSeq + '\n'
    return bufferTexte


def parser(blast, filter):
    """
    Function to export data parsed from xml blast
    IN : dico blast : blast[numberQuery][id] = Hit(id, queryDef, scores, qSeq, hSeq, mSeq)
    OUT : file
    """

    def loadIsoform(file = 'isoformsList.json', read = False, write = False):
        """
        simple fonction to load an existing list of RefSeq
        """
        if read:
            if not os.path.exists(file):
                return {}
            with open(file, 'r') as inputfile:
                return json.load(inputfile)
        if write:
            with open(file, 'w') as outfile:
                json.dump(isoformsDic, outfile)


    ##requests in data
    isoformsDic = loadIsoform(file = 'isoformsList.json', read = True)
    parsedData = {} #contain results data

    for numberQuery in blast:
        #blast[numberQuery] is an object Query
        totalCount = 0
        count = 0
        listAccNCBI = [] #list of all RefSeq returned by tblastn
        for id in blast[numberQuery]:
            ##blast[numberQuery][id] === Hit_id
            ##calculated the percent identity
            identityCalculated = blast[numberQuery][id].scores['identity'] / blast[numberQuery][id].lenght * 100
            if filter['idt'] is not None and identityCalculated >= filter['idt']:
                #prepare text
                #list ncbi accession
                ##tuple because we need id to export results
                listAccNCBI.append((blast[numberQuery][id].refseq, id))
                count += 1
            totalCount += 1
        #log.info(f"{blast[numberQuery].name} : {count} hits filtred on {totalCount} tblastn hits")

        ##get isosoform from NCBI by accession
        #isoformsList = [] #list of tuple (refSeq, length)
        for accRefSeq_Name in listAccNCBI:
            ##check if isoform in json file, else get from ncbi
            if accRefSeq_Name[0] not in isoformsDic:
            #if accRefSeq_Name[0] not in isoformsDic or len(isoformsDic[accRefSeq_Name[0]]) == 0:
                #url request to ncbi
                prefixUrl = 'https://www.ncbi.nlm.nih.gov/gene/?term='
                suffixUrl = '&report=gene_table&format=text'
                ncbi = True #is a simple boolean variable to requet ncbi…
                essai = 0 #number of try to request ncbi
                while ncbi:
                    try:
                        r = requests.get(prefixUrl + accRefSeq_Name[0] + suffixUrl)
                        if r.ok:
                            ncbi = False
                    except Exception as e:
                        log.debug(e)
                        if essai < 5:
                            time.sleep(5)
                            essai += 1
                        else:
                            ncbi = False
                #regex to parse text : get variant number/RefSeq and lenght
                ##regex = variant.*(X[MPR]\_[0-9]+.?[0-9]?).*length:.([0-9]+)
                #isoform is a list of tuple
                isoforms = re.findall('variant.*(X[MPR]\_[0-9]+.?[0-9]?).*length:.([0-9]+)', r.text)
                isoformsDic[accRefSeq_Name[0]] = isoforms
                log.debug(f"new isoform {accRefSeq_Name} : {isoforms}")

        ##keep the longgest isoform
        goodListAccNCBI = [] #all RefSeq blast filtred and with longgest isoform
        list_accRefSeq_Name_removed = [] #all RefSeq not keep cause smaller isoform
        for accRefSeq_Name in listAccNCBI:
            buffer_list_isoform = isoformsDic[accRefSeq_Name[0]]
            ##case no isoform
            if len(buffer_list_isoform) == 0:
                if accRefSeq_Name[0] not in goodListAccNCBI:
                    goodListAccNCBI.append(accRefSeq_Name[0])
            ##case multiple isoform
            else:
                buffer_list_sorted = sorted(buffer_list_isoform, key=lambda x: int(x[1]), reverse=True)
                if buffer_list_sorted[0][0] not in list_accRefSeq_Name_removed and buffer_list_sorted[0][0] not in goodListAccNCBI:
                    goodListAccNCBI.append(buffer_list_sorted[0][0])
                else:
                    pass
                ##conserving list of RefSeq removed
                for tuple_element in buffer_list_sorted[1:]:
                    if tuple_element[0] not in list_accRefSeq_Name_removed:
                        list_accRefSeq_Name_removed.append(tuple_element[0])

        ##write results
        file = open('export/' + blast[numberQuery].name + '.txt', 'w')
        ##write header
        header = "#FDGBM by Odd 2020\n#results parsed from a xml tblastn\n"
        file.write(header)
        ## write body
        listSpecie = []
        count = 0
        for tupleRefID in listAccNCBI:
            if tupleRefID[0] in goodListAccNCBI:
                # TODO: few element in goodListAccNCBI will not write in file
                specie = blast[numberQuery][tupleRefID[1]].specie
                name = blast[numberQuery][tupleRefID[1]].name
                listSpecie.append(specie)
                file.write(f"{specie}\t{name}\n")
                log.debug(f"{specie}\t{name}")
                count += 1
        parsedData[blast[numberQuery].name] = {}
        parsedData[blast[numberQuery].name]['result'] = listSpecie
        ##write footer
        # TODO: improve statistiques footer (min max evalue… id…)
        #footer = '#Total hits exported : ' + str(len(goodListAccNCBI)) + '\n#Total hits found by blast : ' + str(totalCount) + '\n'
        footer = '#Total hits exported : ' + str(count) + '\n#Total hits found by blast : ' + str(totalCount) + '\n'
        if filter['idt'] is not None:
            footer += '#value of filtred identity : ' + str(filter['idt'])
        file.write(footer)
        file.close
        #log.info(f"{blast[numberQuery].name} : {len(goodListAccNCBI)} hits exported from {len(listAccNCBI)} hits filtred on {totalCount} tblastn hits")
        log.info(f"{blast[numberQuery].name} : {count} hits exported from {len(listAccNCBI)} hits filtred on {totalCount} tblastn hits")
        ##add total count and other stat
        parsedData[blast[numberQuery].name]['stat'] = {'totalBlast':totalCount, 'totalExported':count}
    loadIsoform(file = 'isoformsList.json', write = True)
    return parsedData

def export(fileName, parsedData):
    """
    exporter les résultats tabulés et tout…
    """
    fileOutput = open(fileName, 'w')
    results = {}

    log.debug(parsedData)
    listSpecie = []
    for geneName in parsedData:
        if len(parsedData[geneName]['result']) == 0:
            if geneName not in results:
                results[geneName] = {}
            results[geneName]['noSpecie'] = 0
        for specie in parsedData[geneName]['result']:
            if specie not in listSpecie:
                listSpecie.append(specie)
            count = parsedData[geneName]['result'].count(specie)
            if geneName not in results:
                results[geneName] = {}
            results[geneName][specie] = count

    header = 'gene\ttotal Blast found\ttotal exported'
    for specie in listSpecie:
        header += '\t' + specie
    fileOutput.write(header + '\n')
    log.info(header)

    for geneName in results:
        line = f"{geneName}\t{parsedData[geneName]['stat']['totalBlast']}\t{parsedData[geneName]['stat']['totalExported']}"
        if geneName == 'noSpecie':
            for specie in listSpecie:
                line += '0\t'
        else:
            for specie in listSpecie:
                try:
                    line += '\t' + str(results[geneName][specie])
                except KeyError:
                    line += '\t' + '0' #warning, 0 result and/or the specie was not found by blast
        fileOutput.write(line + '\n')
        log.info(line)
    fileOutput.close()
