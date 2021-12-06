import streamlit as st
import pandas as pd
from numpy import load
import requests
import io

@st.cache
def load_data():
    df = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/gupy_base_ds.csv')
    df['id_vaga'] = df['id_vaga'].values.astype(str)
    df.sort_values(by=['empresa'], inplace=True)
    df['url'] = df['url'].apply(make_clickable)
    df['skills_link'] = df['id_vaga'].apply(make_skill_link)
    return df

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = 'Inscrever-se no site oficial'
    return f'<a target="_blank" href="{link}">{text}</a>'

def make_skill_link(id_vaga):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = 'Mais...'
    #return f'<a target="_blank" href=https://vagas-ds-skills-resp.herokuapp.com/?idvaga={id_vaga}>{text}</a>'
    return f'<a target="_blank" href=http://www.detalhesvaga.vagasds.com/?idvaga={id_vaga}>{text}</a>' 


@st.cache
def load_cosine_sim():
    response = requests.get('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/cosine_sim.npy')
    response.raise_for_status()
    data_sim = load(io.BytesIO(response.content))
    return data_sim


def get_recommendations(df, id_vaga, sim_matrix):
    indices = pd.Series(df.index, index=df['id_vaga']).drop_duplicates()
    # Retornando o índice da vaga que corresponde ao id
    idx = indices[id_vaga]

    # Retornando as vagas mais similares
    sim_scores = list(enumerate(sim_matrix[idx]))

    # Ordenando as vagas com base nos scores de similaridade, em ordem decrescente
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Retornando os scores das 5 vagas mais similares
    sim_scores = sim_scores[1:6]

    # Pegando os índices destas vagas
    movie_indices = [i[0] for i in sim_scores]
    
    return df[['skills_link', 'cargo', 'empresa', 'tp_contratacao', 'trab_remoto', 'url']].iloc[movie_indices].reset_index()