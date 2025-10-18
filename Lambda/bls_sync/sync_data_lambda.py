import boto3
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib
import os
import json


# Configurations (use environment variables in Lambda)
BLS_URL =  "https://download.bls.gov/pub/time.series/pr/"
S3_BUCKET = os.environ["S3_BUCKET"]

s3 = boto3.client('s3')


# List files in s3
def list_s3_files(bucket):
    paginator = s3.get_paginator("list_objects_v2")
    files = {}
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            if obj["Key"] == "population_data.json":
                continue
            files[obj["Key"]] = obj["ETag"].strip('"')
    return files

def md5_file_content(content):
    return hashlib.md5(content).hexdigest()

def get_bls_file_list(base_url):
    headers = {"User-Agent": "Tejal Kanase (tejal.s.kanase14@gmail.com)  - for data access"} 
    resp = requests.get(base_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    file_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("../"):
            file_links.append(href)
    return file_links[1:]

def sync_file_to_s3(file_url, bucket):
    file_name = file_url.split("/")[-1]
    s3_key = f"{file_name}"
    headers = {"User-Agent": "Tejal Kanase (tejal.s.kanase14@gmail.com)  - for data access"}
    resp = requests.get(file_url, headers=headers)
    resp.raise_for_status()
    content = resp.content
    
    new_hash = md5_file_content(content)
    existing_files = list_s3_files(bucket)
    
    if s3_key in existing_files and existing_files[s3_key] == new_hash:
        print(f"Skipping {file_name} (no changes)")
        return
    
    s3.put_object(Bucket=bucket, Key=s3_key, Body=content)
    print(f"Uploaded {file_name} to S3")

def delete_removed_s3_files(bls_files, bucket):
    s3_files = list_s3_files(bucket)
    bls_file_names = [f.split("/")[-1] for f in bls_files]
    
    for s3_key in s3_files:
        file_name = s3_key.split("/")[-1]
        if file_name not in bls_file_names:
            s3.delete_object(Bucket=bucket, Key=s3_key)
            print(f"Deleted {file_name} from S3 (no longer on source)")

def fetch_and_save_population_data():
    API_URL = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"
    try:
        # Fetch data from API
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Convert to string for upload
        json_data = json.dumps(data)
        file_name = "population_data.json"
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=json_data,
            ContentType="application/json"
        )
    except Exception as e:
        print(f"Error fetching or uploading data: {str(e)}")
        return {"status": "error", "message": str(e)}

# Lambda Handler
def lambda_handler(event, context):
    print("uploading population json file...")
    fetch_and_save_population_data()

    print("Starting BLS to S3 sync...")
    bls_files = get_bls_file_list(BLS_URL)
    
    for file_link in bls_files:
        file_url = urljoin(BLS_URL, file_link)
        sync_file_to_s3(file_url, S3_BUCKET)
    
    delete_removed_s3_files(bls_files, S3_BUCKET)
    print("Sync complete!")
    return {"status": "success", "files_synced": len(bls_files)}
