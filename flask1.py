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

app = Flask(__name__)
mess=""
@app.route('/')
def home():
   return render_template('login.html')
@app.route('/',methods=['POST'])
def home1():
    if(request.method=='POST'):
        return redirect("http://localhost:8888")
@app.route('/parquet')
def home2():
   return render_template('parquet.html')
@app.route('/parquet',methods=['POST'])
def home3():
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
        
        file_path = bucket + "/" + dim_or_fact_type + "/" + dim_or_fact_name + "/" + "transform.parquet"
        print("Fetching parquet from cos path: " + file_path)
        destination_path = desktop_path + "/" + dim_or_fact_folder_name + "_" + time_string + ".csv"
        print("The csv will be added to the path: " + destination_path)
        
        parquet_file = pq.ParquetDataset(file_path, filesystem=s3).read()
        
        df = parquet_file.to_pandas()
        csv_data = df.to_csv(destination_path, date_format='%Y-%m-%dT%H:%M:%S', index=False)

    return render_template('parquet.html',message=mess)
if __name__ == '__main__':
    app.run()