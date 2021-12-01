import streamlit as st
import pandas as pd
from numpy import load
import requests
import io
import boto3

#Função para salvar cada cancelamento em um arquivo csv no S3. Por questões de segurança, todos os arquivos são salvos como privados
def save2s3(df, bucket, filename):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id='SUA_CHAVE_AQUI',
        aws_secret_access_key='SUA_CHAVE_AQUI'
    )
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    response = s3_client.put_object(Bucket=bucket, Key=filename, Body=csv_buffer.getvalue())
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    return status