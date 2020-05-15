# FDGBM
A **F**inder **D**uplicated **G**enes in **B**at**M**an (*Homo Sapiens*)


# Introduction


This pipeline was created for the intership of 2 students in master 2 in [*Université Lyon 1*](https://www.univ-lyon1.fr/).

*Authors* :
- **Thoto** ([Théophile Tesseraud](mailto:theophile.tesseraud@gmail.com))
- **Odd** ([Antoine Heurtel](mailto:antoine.heurtel@gmail.com))

This is a librairy python3.

# Commands

Globaly the commands format is :  
`python3 main.py command -option(s) file`  
They are x possibilities to run this pipeline.

## `parse`

This command allow parse files, like xml (from Uniprot) or tsv (from [innatdb](https://www.innatedb.com))

Options available with parse are :
- -o file : to export data in a data file, this file will we be loading
- -x file : to parse a xml file from uniprot
- -i file : to parse a tsv file from innatdb

### what is a…

- *xml file* : is a xml file downloaded from Uniprot.
- *tsv innatdb* : is a tabular file download from innatedb. Her header must be : `id, species, taxoid, ensembl, entrez, name, fullname, synonym, signature,chromStart, chromEnd, chromStrand, chromName, band, goTerms, function, goFunctions, goLocalizations, cerebralLocalization, nrIntxsValidated, nrIntxsPredicted, transcripts, humanOrthologs, mouseOrthologs, bovineOrthologs, lastModified`

## `blast`

This command

Options available with parse are :
- -o : to export sequence in a fasta file
- -n : the n first gene (default with -o is all genes)

## Other option available

- -l file : to load existings data, their data would be created by FDGBM with -o option.
- -v : to active verbose mode (= info level)
