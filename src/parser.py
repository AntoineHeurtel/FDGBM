#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
#      Sub module to parser
##########################################################
from xml.dom import minidom


class Gene():
    def __init__(self, id, name, fulname,nrIntxsValidated):
        self.id = id
        self.name = name
        self.fulname = fulname
        self.nbrExpValInteract = nrIntxsValidated



def peack(data, number):
    listeGene = []
    mini = [0]
    for geneID in data:
        if len(listeGene) < number and min(mini) > int(data[geneID].nbrExpValInteract):
            listeType.append((data[geneID].nbrExpValInteract,data[geneID].id))
            mini.append(data[geneID].nbrExpValInteract)
        elif int(data[geneID].nbrExpValInteract) > min(mini):
            for c, value in enumerate(listeGene):
                if int(value[0]) > min(mini):
                    listeGene[c] = (data[geneID].nbrExpValInteract,data[geneID].id)
        else:
            pass
    return listeGene
##############################
# Parser
##############################
def innateDbGene(data, filename):
    """
    parser file (tsv) from innateDb
    IN : dic + tsv file
    OUT : dic
    """
    with open(filename, newline='') as csvFile:
        for row in csvFile.readlines()[1:]:
            column = row.rstrip().split('\t')
            geneID = column[3]
            if geneID not in data:
                data[geneID] = Gene(column[3],column[5],column[6],column[19])
    return data

def uniprotDbGene(data, filename):
    """
    parser file (xml) from Uniprot
    IN : dic + tsv file
    OUT : dic
    """
    xmlFile = minidom.parse(filename)
    itemlist = xmlFile.getElementsByTagName('protein')
