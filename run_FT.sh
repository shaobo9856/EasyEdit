#!/bin/bash

LANGS=("vi" "ru" "zh-cn") #"es" 
DATAS=("MzsRE/mzsre_test_duplicate_en" "MCounterFact/mcounterfact_test_en" "WikiFactDiff/wfd_test_en")
CUDA=0

for DATA in "${DATAS[@]}";do
    for LANG in "${LANGS[@]}";do
        echo "currently processing language: $LANG with data: $DATA"
        CUDA_VISIBLE_DEVICES=$CUDA python run_zsre_llama2.py --lang1 en --lang2 $LANG --editing_method FT --hparams_dir ./hparams/FT/llama-7b.yaml  --data_dir $DATA 
    done
done
