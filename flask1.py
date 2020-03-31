#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 17:08:03 2020

@author: harshanandandivvela
"""

from flask import Flask,Response, redirect, url_for, request,make_response,render_template
import io
import pyarrow.parquet as pq
from pathlib import Path
import s3fs
import os
import time
import pandas as pd
app = Flask(__name__)
mess=""
@app.route('/')
def home1():
   return render_template('parquet.html')
@app.route('/',methods=['POST'])
def home2():
    global user
    mess=""
    if request.method == 'POST':
        bucket=request.form['bucket']
        dim_or_fact_type=request.form['dim_or_fact_type']
        dim_or_fact_name=request.form['dim_or_fact_name']
        # Fetching the environment variables
        
        key = os.getenv('ACCESS_KEY_ID')
        secret = os.getenv('SECRET_ACCESS_KEY')
        endpoint_url = os.getenv('ENDPOINT_URL')
        
        s3 = s3fs.S3FileSystem(anon=False,
                               key=key,
                               secret=secret,
                               client_kwargs={'endpoint_url': endpoint_url})
                               
        ####### you will have to fetch the below three variables from the front end ########
        #bucket = "epm-pricing-staging"
        #dim_or_fact_type = "dimension"
        #dim_or_fact_name = "CURRENCY_DIMENSION"
        ####################################################################################
        
        desktop_path = str(Path.home())
        time_string = time.strftime("%Y_%m_%d-%H_%M_%S")
        dim_or_fact_folder_name = dim_or_fact_name.replace("/", "_")
        destination_path = desktop_path + "/" + dim_or_fact_folder_name + "_" + time_string + ".csv"
        df = pd.DataFrame(list())
        df.to_csv(destination_path,date_format='%Y-%m-%dT%H:%M:%S', index=False)
        if(dim_or_fact_type=="fact"):
            df=pd.DataFrame()
            Partition_Years=s3.ls(bucket + "/" + dim_or_fact_type + "/" + dim_or_fact_name)
            df=pd.concat(
                pq.ParquetDataset(j, filesystem=s3).read().to_pandas()
                for i in range(1,len(Partition_Years)) for j in s3.ls(Partition_Years[i])
                )
            df.to_csv(destination_path,mode='a')      
        else:    
            file_path = bucket + "/" + dim_or_fact_type + "/" + dim_or_fact_name + "/" + "transform.parquet"
            print("Fetching parquet from cos path: " + file_path)

            print("The csv will be added to the path: " + destination_path)

            parquet_file = pq.ParquetDataset(file_path, filesystem=s3).read()

            df = parquet_file.to_pandas()
            csv_data = df.to_csv(destination_path, date_format='%Y-%m-%dT%H:%M:%S', index=False)
            mess="Parquet Created"
    return render_template('parquet.html',message=mess)
if __name__ == '__main__':
    app.run(port=8000)
