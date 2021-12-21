import streamlit as st
import pandas as pd
import io
import boto3

def make_clickable(link):
    text = 'ir para a vaga'
    return f'<a target="_blank" href="{link}">{text}</a>'

@st.cache(ttl=60*60)
def load_data(df_source):
    df = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/' + df_source)
    df.sort_values(by=['empresa'], inplace=True)
    df['url2'] = df['url'].apply(make_clickable)
    df['id_vaga'] = df['id_vaga'].apply(make_skill_link)    
    return df

@st.cache(ttl=60*60)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def make_skill_link(id_vaga):
    text = 'Mais...'
     #return f'<a target="_blank" href=https://vagas-ds-skills-resp.herokuapp.com/?idvaga={id_vaga}>{text}</a>'
    return f'<a target="_blank" href=http://www.detalhesvaga.vagasds.com/?idvaga={id_vaga}>{text}</a>'


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