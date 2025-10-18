#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -f ../bls_sync.zip
pip install -r requirements.txt -t ./package
cd package
zip -r9 ../../bls_sync.zip .
cd ..
zip -g ../bls_sync.zip sync_data_lambda.py