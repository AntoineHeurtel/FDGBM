#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to parser
##########################################################
import requests
import re

from xml.dom import minidom
from src.logger import logger as log

class Gene():
    def __init__(self, id, name, fulname, source, function, accession, sequence, taxid, goterms):
        self.id = id
        self.name = name
        self.fulname = fulname
        self.source = source #name of database
        self.function = function #function of gene (immuno, metabo, reproduction)
        self.accession = accession #code accession Uniprot only
        self.sequence = sequence
        self.goterms = goterms
        self.taxid = taxid

    def __str__(self):
        return f"{self.taxid}:{self.id}, {self.name} from {self.source}"

    def seqUniprot(self):
        """
        get sequence from Uniprot database
        """
        queryURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&accession=" + self.accession
        r = requests.get(queryURL, headers={"Accept": "text/x-fasta"})
        if not r.ok:
            r.raise_for_status()
            log.warning("error to download the sequence from uniprot")
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
    with open(filename, newline='') as tsvFile:
        for row in tsvFile.readlines()[1:]:
            column = row.rstrip().split('\t')
            geneID = column[3]
            if geneID not in data:
                #traitement GO terms
                goTerms = re.findall("GO:[0-9]+", column[14])
                data[geneID] = Gene(geneID, column[5], column[6], "innateDb", column[15], "", "", column[2], ",".join(goTerms))
                log.debug(str(data[geneID]))
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
        if not i.getElementsByTagName('sequence')[0].firstChild:
            sequence=""
        else:
            sequence = i.getElementsByTagName('sequence')[0].firstChild.data
        Name = i.getElementsByTagName('name')[0].firstChild.data
        taxID = i.getElementsByTagName('dbReference')[0]
        if taxID.getAttribute('type')=='NCBI Taxonomy':
            taxID=taxID.getAttribute('id')
        property= i.getElementsByTagName('property')
        for j in property:
            if j.getAttribute('type')=='gene ID':
                geneID=j.getAttribute('value')
        Golist=list()
        dbref= i.getElementsByTagName('dbReference')
        for z in dbref:
            if z.getAttribute('type')=='GO':
                Goterme=z.getElementsByTagName('property')[0]
                Goterme=Goterme.getAttribute('value')
                Golist.append(Goterme)
        data[geneID] = Gene(geneID,Name, fullName, "Uniprot", function, accession, sequence, taxID, Golist)
    return data


def writter(data, filename):
    """
    IN : dic + filename
    OUT : write a tsv filename
    """
    header = 'id\ttaxid\tname\tfulname\tfunction\tgoterms\tsequence'
    with open(filename, 'w') as file:
        file.write(header + '\n')
        for geneID in data:
            id = data[geneID].id
            taxid = data[geneID].taxid
            name = data[geneID].name
            function = data[geneID].function
            goterms = data[geneID].goterms
            seq = data[geneID].sequence
            line = f"{id}\t{taxid}\t{name}\t{function}\t{goterms}\t{seq}"
            file.write(line + '\n')
