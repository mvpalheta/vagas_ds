##########################################################################################################################################
## Este programa produz as wordclouds utilizadas no app e salva as imagens em um bucket do S3. A ideia é otimizar o carregamento do app ##
##########################################################################################################################################

import matplotlib.pyplot as plt
import texthero as hero
from texthero import preprocessing
from nltk.corpus import stopwords
from wordcloud import WordCloud, ImageColorGenerator
import pandas as pd
import boto3
import io

stopwords = set(stopwords.words('portuguese'))
# customizando stopwords
stopwords.update(['dia'])

#carregando a base de dados
df_all = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/gupy_base_ds.csv')

#definindo uma função para criar as wordcloud
def wordcloud(df, var2cloud, width=1600, height=800, max_words=100, figsize=(10,6), background_color="black",
                title='Expressões mais frequentes na variável'):
#Criando uma pipeline customizada para finalizar o pre-processamento dos dados                
    custom_pipeline = [preprocessing.remove_diacritics,
                        preprocessing.remove_punctuation,
                        preprocessing.remove_whitespace,
                        preprocessing.remove_urls]

#excluido registros em branco, removendo dígitos, passando as palavras para caixa baixa, removendo stopwords, aplicando a pipeline definida acima e 
#guardando o resulta para gerar a wordcloud  
    ser1 = df.dropna(subset=[var2cloud], axis=0)[var2cloud]
    ser12 = preprocessing.remove_digits(ser1)
    ser13 = preprocessing.lowercase(ser12)
    ser14 = preprocessing.remove_stopwords(ser13, stopwords=stopwords)
    ser2 = hero.clean(ser14, custom_pipeline)
    ser3 = ser2.to_string(index=False)

#Gerando a wordcloud e retornando a imagem do resultado
    wordcloud = WordCloud(stopwords=stopwords, random_state=123,
                      background_color=background_color,
                      width=width, height=height, max_words=max_words, font_step=1).generate(ser3)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()
    plt.title(title, fontsize=18)
    plt.imshow(wordcloud)
    return plt

#Função para salvar as wordclouds para o S3 
def save2s3(plt, bucket, filename):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id='SUA_CHAVE_AQUI',
        aws_secret_access_key='SUA_CHAVE_AQUI'
    )
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    response = s3_client.put_object(Bucket=bucket, Key=filename, Body=buffer.getvalue(), ACL ='public-read')
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        print("")
        print(f"Arquivo {filename} gravado com successo no S3. Status - {status}")
    else:
        print("")
        print(f"Arquivo {filename} não gravado no S3. Status - {status}")

#gerando a wordcloud para as atribuições e salvando no S3
wordcloud1 = wordcloud(df_all, 'atribuicoes_cleaned', title='Expressões mais frequentes entre as atribuições')
save2s3(wordcloud1, 'vagas-ds-storage', 'wordcloud_atribuicoes.png')

#carregando as qualificações e realizando ajustes em algumas palavras
df_all2 = df_all.copy()
df_all2['qualificacoes_cleaned'] = df_all2.qualificacoes_cleaned.str.lower()
esc2replace = '|'.join(['graduação completa', 'graduação completo', 'graduacao completo', 'graduacao completa', 'superior completo', 'ensino superior', 'superior'])

mod2replace = '|'.join(['modelagem', 'modelage', 'modelo', 'modeloss'])
df_all2['qualificacoes_cleaned'] = df_all2.qualificacoes_cleaned.str.replace(esc2replace,'graduacao')
df_all2['qualificacoes_cleaned'] = df_all2.qualificacoes_cleaned.str.replace('graduacao completo','graduacao')
df_all2['qualificacoes_cleaned'] = df_all2.qualificacoes_cleaned.str.replace(mod2replace,'modelos')
df_all2['qualificacoes_cleaned'] = df_all2.qualificacoes_cleaned.str.replace('modeloss','modelos')

#gerando a wordcloud para as qualificações e salvando no S3
wordcloud2 = wordcloud(df_all2, 'qualificacoes_cleaned', title='Expressões mais frequentes entre as habilidades requeridas')
save2s3(wordcloud2, 'vagas-ds-storage', 'wordcloud_qualificacoes.png')