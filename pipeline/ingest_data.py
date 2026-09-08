#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click
from pathlib import Path

# Create the data folder automatically if it doesn't exist
data_dir = Path("data/")
data_dir.mkdir(exist_ok=True, parents=True)

#Parameterize
year=2021
month=1
chunksize=100000
pg_user="root"
pg_pass="root"
pg_host="localhost"
pg_port=5432
pg_db="ny_taxi"
target_table="yellow_taxi_data"

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

@click.command()
@click.option('--pg-user', default=pg_user, help='PostgreSQL user')
@click.option('--pg-pass', default=pg_pass, help='PostgreSQL password')
@click.option('--pg-host', default=pg_host, help='PostgreSQL host')
@click.option('--pg-port', default=pg_port, type=int, help='PostgreSQL port')
@click.option('--pg-db', default=pg_db, help='PostgreSQL database name')
@click.option('--year', default=year, type=int, help='Year of the data')
@click.option('--month', default=month, type=int, help='Month of the data')
@click.option('--target-table', default=f'yellow_taxi_data_{month:02d}_{year}', help='Target table name')
@click.option('--chunksize', default=chunksize, type=int, help='Chunk size for reading CSV')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    file_name = f'yellow_tripdata_{year}-{month:02d}.csv.gz'

    df_iter = pd.read_csv(
        prefix + file_name,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize
    )

    isTableInitialized = True

    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    for df_chunk in tqdm(df_iter):
        if isTableInitialized:
            # Create table structure
            df_chunk.to_sql(name=f'{target_table}', con=engine, if_exists='replace')
            isTableInitialized = False 
        # Data append
        df_chunk.to_sql(name=f'{target_table}', con=engine, if_exists='append')
       
if __name__ == '__main__':
    run()
