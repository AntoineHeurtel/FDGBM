#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ©2020 Thot'Odd

##########################################################
# Librairie pour le stage M1 2020  #
##########################################################

import argparse
import logging

from logging.handlers import RotatingFileHandler


#####################
# Arguments #
#####################
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Programme Python Stage M1 2020
        --------------------------------
    Pour plus d’information consulter le ReadMe.
    ''',
    epilog='''le mode de fonctionnement de ce programme est le suivant :
    x.py
    ''')

parser.add_argument('-v', '--verbose', action="store_true",
                    help="Active le mode verbose (mode level debug INFO)")
args = parser.parse_args()


#####################
# Log #
#####################
logger = logging.getLogger()
# if "-v" in sys.argv:
if args.verbose:
    LEVEL = "DEBUG"  #INFO# celui du logger
    LOG_LEVEL = logging.DEBUG
    PRINT_LEVEL = logging.DEBUG
else:
    LEVEL = "INFO"
    LOG_LEVEL = logging.INFO
    PRINT_LEVEL = logging.INFO
logger.setLevel(LEVEL)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] :: %(message)s')

file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(PRINT_LEVEL)
stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(stream_handler)