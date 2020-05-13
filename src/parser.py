#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to parser
##########################################################
import requests

from xml.dom import minidom

class Gene():
    def __init__(self, id, name, fulname, source, function, accession, sequence):
        self.id = id
        self.name = name
        self.fulname = fulname
        self.source = source #name of database
        self.function = function #function of gene (immuno, metabo, reproduction)
        self.accession = accession #code accession Uniprot only
        self.sequence = sequence
        self.goterms = ""
        self.taxid = ""

    def seqUniprot(self):
        """
        get sequence from Uniprot database
        """
        queryURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&accession=" + self.accession
        r = requests.get(queryURL, headers={"Accept": "text/x-fasta"})
        if not r.ok:
            r.raise_for_status()
            log.warnig("error to download the sequence from uniprot")
            pass
        self.sequence = "".join(r.text.split("\n")[1:])


##############################
# Parser
##############################
def innateDbGene(data, filename):
    """
    parser file (tsv) from innateDb
    IN : dic + tsv file
    OUT : dic
    """
    with open(filename, newline='') as csv:
        for row in csvFile.readlines()[1:]:
            column = row.rstrip().split('\t')
            geneID = column[3]
            if geneID not in data:
                data[geneID] = Gene(column[3],column[5],column[6],column[19])
    return data




def uniprotDbGene(data, filename, function):
    """
    parser file (xml) from Uniprot. xml file is list of protein with a same function.
    you need to give the function of these genes in the third argument.
    IN : dic + xml file
    OUT : dic
    """
    xmlFile = minidom.parse(filename)
    Proteinlist = xmlFile.getElementsByTagName('entry')
    for i in Proteinlist:
        fullName=i.getElementsByTagName('fullName')[0].firstChild.data
        print(fullName)
        accession=i.getElementsByTagName('accession')[0].firstChild.data
        print(accession)
        sequence=i.getElementsByTagName('sequence')[0].firstChild.data
        print(sequence)
        Name=i.getElementsByTagName('name')[0].firstChild.data
        print(Name)
        taxID=i.getElementsByTagName('dbReference')[0]
        if taxID.attribut=='NCBI':
            
    return data
