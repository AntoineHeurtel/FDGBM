# FDGBM
A **F**inder **D**uplicated **G**enes in **B**at**M**an (*Homo Sapiens*)


# Introduction


This pipeline was created for the internship of 2 students in master 2 in [*Université Lyon 1*](https://www.univ-lyon1.fr/).

*Authors* :
- **Thoto** ([Théophile Tesseraud](mailto:theophile.tesseraud@gmail.com))
- **Odd** ([Antoine Heurtel](mailto:antoine.heurtel@gmail.com))

This is a librairy python3.

Package dependant : `requests`

# Commands

Globaly the commands format is :  
`python3 main.py command -option(s) file`  
They are x possibilities to run this pipeline.

## `parser`

This command allow parse files, like xml (from Uniprot) or tsv (from [innatdb](https://www.innatedb.com))

Options available with parse are :
- -o file : to export data in a data file, this file will we be loading
- -u file : to parse a xml file from uniprot
- -i file : to parse a tsv file from innatdb

If you want to parse multi file, it’s possible ! In fact, you can give multi path or file in arguments, like `-i file1 file2 file3`.

### what is a…

- *xml file* : is a xml file downloaded from Uniprot.
- *tsv innatdb* : is a tabular file download from innatedb. Her header must be : `id, species, taxoid, ensembl, entrez, name, fullname, synonym, signature,chromStart, chromEnd, chromStrand, chromName, band, goTerms, function, goFunctions, goLocalizations, cerebralLocalization, nrIntxsValidated, nrIntxsPredicted, transcripts, humanOrthologs, mouseOrthologs, bovineOrthologs, lastModified`

## `blast`

This commands allow user to manipulate a blast result.

Options available with parse are :
- -fa : to export sequence in a fasta file
- -n : the n first gene (n is optional, by default, with -o, is all genes). If n is < 0 (like `-n -20`), the genes will random draw.
- -b : to parse a xml file from a tblastn.
- -o : to export results of blast in a tabular file

If you want to export a xml blast result you can apply a filter to exporting data. The filter can take arguments like :
- -id : to define a percent filter of identity
- -n : to define a number of gene to exporting

## Other option available with any command

- -l file : to load existing data, their data would be created by FDGBM with -o option.
- -v : to active verbose mode (= info level)
- -f : to force the overwrite
