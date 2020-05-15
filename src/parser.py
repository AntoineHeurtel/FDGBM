#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to parser
##########################################################
import requests
import re
import urllib.parse
import urllib.request

from xml.dom import minidom
from src.logger import logger as log

class Gene():
    def __init__(self, id, name, fulname, source, function, accession, sequence, taxid, goterms):
        #function write : header = 'id\ttaxid\tname\tfulname\taccession\tsource\tfunction\tgoterms\tsequence'
        self.id = id
        self.taxid = taxid
        self.name = name
        self.fulname = fulname
        self.accession = accession #code accession Uniprot only
        self.source = source #name of database
        self.function = function #function of gene (immuno, metabo, reproduction)
        self.goterms = goterms
        self.sequence = sequence

    def __str__(self):
        return f"{self.taxid}:{self.id}, {self.name} from {self.source}"

    def seqUniprot(self):
        """
        get sequence from Uniprot database
        """
        queryURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&accession=" + self.accession
        r = requests.get(queryURL, headers={"Accept": "text/x-fasta"})
        if not r.ok:
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                log.critical(str(e) + " with id " + self.id)
            log.warning("error to download the sequence from uniprot")
            self.sequence = ""
        else:
            self.sequence = "".join(r.text.split("\n")[1:])

    def accEnsembl(self):
        """
        Get accession from Ensemble ID to Uniprot
        """
        url = 'https://www.uniprot.org/uploadlists/'
        params = {'from': 'ENSEMBL_ID', 'to': 'ACC', 'format': 'tab', 'query': self.id}
        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        req = urllib.request.Request(url, data)
        with urllib.request.urlopen(req) as f:
            response = f.read()
        accList = re.findall('[0-9A-Z]+',response.decode('utf-8'))
        #Verification of good request
        if len(accList[-1]) >= 5:
            self.accession = accList[-1]
        elif len(accList) == 2:
            #maybe no have accession found
            self.accession = ""
            log.warning("no accession uniprot found with id " + self.id)
        else:
            log.critical("unknow error with id " + self.id)

    def echo(self, sep='\t'):
        """
        write all attributs
        """
        line = []
        for attribute in self.__dict__:
            if isinstance(self.__dict__[attribute], list):
                buffer = ",".join(self.__dict__[attribute])
                line.append(buffer)
            else:
                line.append(self.__dict__[attribute])
        return sep.join(line)


##############################
# Parser
##############################
def innateDbGene(data, filename):
    """
    parser file (tsv) from innateDb
    IN : dic + tsv file
    OUT : dic
    """
    number = 0
    with open(filename, newline='') as tsvFile:
        for row in tsvFile.readlines()[1:]:
            column = row.rstrip().split('\t')
            geneID = column[3]
            if geneID not in data:
                #traitement GO terms
                goTerms = re.findall("GO:[0-9]+", column[14])
                data[geneID] = Gene(geneID, column[5], column[6], "innateDb", column[15], "", "", column[2], ",".join(goTerms))
                if data[geneID].accession == "":
                    data[geneID].accEnsembl()
                if data[geneID].sequence == "" and data[geneID].accession != "":
                    data[geneID].seqUniprot()
                #log.debug(str(data[geneID].echo()))
            number += 1
    log.info("Parsed " + str(number) + " lines")
    return data


def uniprotDbGene(data, filename,function):
    """
    parser file (xml) from Uniprot. xml file is list of protein with a same function.
    you need to give the function of these genes in the third argument.
    IN : dic + xml file
    OUT : dic
    """
    xmlFile = minidom.parse(filename)
    for i in xmlFile.getElementsByTagName('entry'):
        fullName = i.getElementsByTagName('fullName')[0].firstChild.data
        print(fullName)
        accession = i.getElementsByTagName('accession')[0].firstChild.data
        test= i.getElementsByTagName('sequence')
        sequence=test[-1].firstChild.data
        Name = i.getElementsByTagName('name')[0].firstChild.data
        taxID = i.getElementsByTagName('dbReference')[0]
        if taxID.getAttribute('type') == 'NCBI Taxonomy':
            taxID = taxID.getAttribute('id')
        property = i.getElementsByTagName('property')
        for j in property:
            if j.getAttribute('type') == 'gene ID':
                geneID = j.getAttribute('value')
        Golist = list()
        dbref = i.getElementsByTagName('dbReference')
        for z in dbref:
            if z.getAttribute('type') == 'GO':
                Goterme = z.getElementsByTagName('property')[0]
                Goterme = Goterme.getAttribute('value')
                Golist.append(Goterme)
        data[geneID] = Gene(geneID,Name, fullName, "Uniprot", function, accession, sequence , taxID, Golist)
    return data


def writter(data, filename):
    """
    IN : dic + filename
    OUT : write a tsv filename
    """
    header = 'id\ttaxid\tname\tfulname\taccession\tsource\tfunction\tgoterms\tsequence'
    with open(filename, 'w') as file:
        file.write(header + '\n')
        for geneID in data:
            file.write(data[geneID].echo() + '\n')


def loadData(data, filename):
    """
    Load data from a tsvfile (writed by script)
    IN : data (void dic) + filename
    OUT : data (dic)
    """
    with open(filename, 'r') as tsvFile:
        for row in tsvFile.readlines()[1:]:
            column = row.rstrip().split('\t')
            if column[0] not in data:
                try:
                    goTerms = column[7].split(',')
                    data[column[0]] = Gene(column[0], column[2], column[3], column[5], column[6], column[4], column[8], column[1], goTerms)
                    log.debug(data[column[0]])
                except IndexError as e:
                    if len(column) == 8:
                        data[column[0]] = Gene(column[0], column[2], column[3], column[5], column[6], column[4], "", column[1], goTerms)
                        log.debug(data[column[0]])
                    if len(column) <= 7:
                        pass
    return data
