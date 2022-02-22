#!/bin/bash

DATA_RAW_FOLDER=data/raw

mkdir $DATA_RAW_FOLDER
cd $DATA_RAW_FOLDER
curl -o 20news.tar.gz http://qwone.com/~jason/20Newsgroups/20news-bydate.tar.gz
tar -xf 20news.tar.gz
rm 20news.tar.gz
