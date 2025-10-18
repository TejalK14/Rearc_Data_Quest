#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -f ../generate_reports.zip
rm -rf package
pip install -r requirements.txt -t ./package
cd package
zip -r9 ../../generate_reports.zip .
cd ..
zip -g ../generate_reports.zip generate_reports_lambda.py