################################################################################################################################################
## Este programa calcula a matriz de similaridades entre as vagas extraídas do site da Gupy e salva esta matriz em um bucket do S3            ##
## A matriz é calculada com base no nome da empresa, atribuições e qualificações das vagas, tipo de contratação e se é trabalho remoto ou não ##
################################################################################################################################################

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import pandas as pd
from texthero import preprocessing
import texthero as hero
import os
from numpy import save
import boto3
import io

# Setando as stopwords para portugues e adicionando a palavra 'dia'
stopwords = set(stopwords.words('portuguese'))
stopwords.update(['dia'])

df = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/gupy_base_ds.csv')

#Substituindo NaN com uma string em branco, excluindo espaços em branco indesejados no início e final e removendo dígitos
#das descrições das atribuições qualificações
df['atribuicoes_cleaned'] = df['atribuicoes_cleaned'].fillna('').str.strip()
df['qualificacoes_cleaned'] = df['qualificacoes_cleaned'].fillna('').str.strip()

df['atribuicoes_cleaned'] = preprocessing.remove_digits(df['atribuicoes_cleaned'])
df['qualificacoes_cleaned'] = preprocessing.remove_digits(df['qualificacoes_cleaned'])

#Removendo espaços em branco para que o vetorizador não conte, por exemplo, o "Brasil" de Santander Brasil e Infotec Brasil como os mesmos.
df['empresa'] = df['empresa'].str.replace(' ', '')
df['tp_contratacao'] = df['tp_contratacao'].str.replace(' ', '')

#Criando campo com os metadados necessários para vetorização
#Agora iremos criar um campo no dataframe contendo todos os metadados (empresa, atribuições, qualificações, tipo de contratação e trabalho remoto) que serão utilizados 
#na vetorização. A função **create_soup** irá juntar as variáveis necessárias, separadas por um espaço em branco.
def create_soup(x):
    return x['empresa'] + ' ' + x['atribuicoes_cleaned'] + ' '+ x['qualificacoes_cleaned'] + ' '+ x['tp_contratacao'] + ' '+ x['trab_remoto']

# Criando a nova feature 'soup', para guardar os metadados para vetorização
df['soup'] = df.apply(create_soup, axis=1)

#Colocando todas as palavras em caixa baixa e removendo stopwords
df['soup'] = preprocessing.lowercase(df['soup'])
df['soup'] = preprocessing.remove_stopwords(df['soup'], stopwords=stopwords)

#Criando uma pipeline customizada para finalizar o pre-processamento dos dados
custom_pipeline = [preprocessing.remove_diacritics,
                    preprocessing.remove_punctuation,
                    preprocessing.remove_whitespace,
                    preprocessing.remove_urls,
                    preprocessing.remove_html_tags]

#Aplicando a pipeline ao campo com os metadodos para vetorização
df['soup'] = hero.clean(df['soup'], custom_pipeline)

#Computando a matriz TF-IDF
#Instanciando um objeto TF-IDF Vectorizer. Neste caso, a matriz esparsa será criada utilizando tanto unigram quanto bigram.
tfidf = TfidfVectorizer(ngram_range=(1, 2))

#Construindo a matriz TF-IDF, através do treino e transformação do corpus
tfidf_matrix = tfidf.fit_transform(df['soup'])

#Computando a matriz de similaridades
cosine_sim = cosine_similarity(tfidf_matrix)

# save to npy file
save('cosine_sim.npy', cosine_sim)


#Creating Session With Boto3.
session = boto3.Session(
aws_access_key_id='SUA_CHAVE_AQUI',
aws_secret_access_key='SUA_CHAVE_AQUI'
)

buffer = io.BytesIO()
save(buffer, cosine_sim)

#Salvando para o S3
s3 = session.resource('s3')

result = s3.meta.client.put_object(Body=buffer.getvalue(), Bucket='vagas-ds-storage', Key='cosine_sim.npy', ACL ='public-read')

res = result.get('ResponseMetadata')

if res.get('HTTPStatusCode') == 200:
    print('Sistema de recomendacao gravado com sucesso')
else:
    print('Sistema de recomendacao não gravado')