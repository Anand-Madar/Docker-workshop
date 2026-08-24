#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

import click

@click.command()
@click.option('--pg_user', default='root', help='Username for PostgreSQL')
@click.option('--pg_pass', default='root', help='Password for PostgreSQL')
@click.option('--pg_host', default='localhost', help='Host for PostgreSQL')
@click.option('--pg_port', default=5432, help='Port for PostgreSQL')
@click.option('--pg_db', default='ny_taxi', help='Database name for PostgreSQL')
@click.option('--year', default=2021, help='Year of the trip data')
@click.option('--month', default=1, help='Month of the trip data')
@click.option('--chunksize', default=100000, help='Chunk size for reading CSV')
@click.option('--target_table', default='yellow_taxi_data', help='Target table in PostgreSQL')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
    # Notice we format the month with :02d so '1' becomes '01' to prevent 404 errors!
    url = f'{prefix}/yellow/yellow_tripdata_{year}-{month:02d}.csv.gz'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first = True
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(n=0).to_sql(name=target_table, con=engine, if_exists='replace')
            first = False   
        df_chunk.to_sql(name=target_table, con=engine, if_exists='append')

if __name__ == '__main__':
    run()