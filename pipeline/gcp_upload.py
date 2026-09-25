import os
import urllib.request
from google.cloud import storage
from google.cloud import bigquery

# --- Configuration ---
PROJECT_ID = "test-terraform-507819"
BUCKET_NAME = "test-terraform-507819-terra-bucket"
DATASET_NAME = "demo_dataset"
TABLE_NAME = "yellow_taxi_data_bq"

# The URL from your ingest script (Example: January 2021 data)
FILE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
LOCAL_FILE_PATH = "yellow_tripdata_2021-01.csv.gz"
DESTINATION_BLOB_NAME = LOCAL_FILE_PATH

def download_data(url, local_path):
    """Downloads the dataset directly from the web."""
    print(f"Downloading dataset from {url}...")
    urllib.request.urlretrieve(url, local_path)
    print("Download complete!")

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the Google Cloud Storage bucket."""
    print(f"Uploading {source_file_name} to gs://{bucket_name}/{destination_blob_name}...")
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)
    print("Upload to Cloud Storage complete!")

def load_gcs_to_bigquery(bucket_name, blob_name, dataset_name, table_name):
    """Loads a file from GCS into a BigQuery table."""
    table_id = f"{PROJECT_ID}.{dataset_name}.{table_name}"
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    
    print(f"Loading data from {gcs_uri} into BigQuery table {table_id}...")
    bq_client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
        # BigQuery can automatically decompress .csv.gz files!
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    load_job = bq_client.load_table_from_uri(
        gcs_uri, table_id, job_config=job_config
    )
    load_job.result()
    
    destination_table = bq_client.get_table(table_id)
    print(f"Success! Loaded {destination_table.num_rows} rows into {table_id}.")

if __name__ == "__main__":
    # 1. Download file to VM
    download_data(FILE_URL, LOCAL_FILE_PATH)
    
    # 2. Upload to Data Lake
    upload_to_gcs(BUCKET_NAME, LOCAL_FILE_PATH, DESTINATION_BLOB_NAME)
    
    # 3. Load into Data Warehouse
    load_gcs_to_bigquery(BUCKET_NAME, DESTINATION_BLOB_NAME, DATASET_NAME, TABLE_NAME)
    
    # 4. Clean up the local file to save VM space
    os.remove(LOCAL_FILE_PATH)
    print("Cleaned up local file.")