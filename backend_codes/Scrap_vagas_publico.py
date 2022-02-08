################################################################################################################################
## Este programa realiza o scraping de vagas no site da gupy, tratamento dos dados e salva a base de dados em um bucket do S3 ##
################################################################################################################################

import requests
import time
import re
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
#from tqdm import tqdm
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import io
import boto3
from datetime import datetime
import os


start_time = datetime.now()
#Checa se o site foi aberto no formato desejado
def check_element_css_exists():
    try:
        driver.find_element_by_css_selector("button[aria-label='Next Page']")
    except NoSuchElementException:
        return False
    return True
    
#Checa se a página foi carregada
def wait_page_load(driver, timeout):
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Next Page']"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        return False
    return True

#Checa se está sendo exibida a caixa de texto de avaliação do site 
def check_modal_is_show():
    try:
        driver.find_element_by_css_selector("button[aria-label='Fechar']")
    except NoSuchElementException:
        return False
    return True

#Se for exibida a caixa de texto de avaliação do site, então fechar
def close_modal():
    if check_modal_is_show() == True:
        driver.find_element_by_css_selector("button[aria-label='Fechar']").click()
    else:
        pass
#Salva dataframe em um bucket do S3 da AWS        
def save2s3(df, bucket, filename):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id='SUA_CHAVE_AQUI',
        aws_secret_access_key='SUA_CHAVE_AQUI'
    )
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    response = s3_client.put_object(Bucket=bucket, Key=filename, Body=csv_buffer.getvalue(), ACL ='public-read')
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print("")
        print(f"Arquivo {filename} gravado com successo no S3. Status - {status}")
    else:
        print("")
        print(f"Arquivo {filename} não gravado no S3. Status - {status}")

#Função para retornar um arquivo de uma pasta        
def get_s3_csv(csv_file, bucket):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id='SUA_CHAVE_AQUI',
        aws_secret_access_key='SUA_CHAVE_AQUI'
    )
    response = s3_client.get_object(Bucket=bucket, Key=csv_file)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
            print(f"Successful S3 get_object response. Status - {status}")
            df = pd.read_csv(response.get("Body"))
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")
    return df        

#definindo os termos a serem buscados no site da gupy
searchterm = "'cientista de dados' 'data scientist' 'ciência de dados' 'data science'"
url = "https://portal.gupy.io/vagas?searchTerm=" + searchterm

#headless = True: definine que não é necessário abrir o navegador para realizar o scraping
#ChromeDriverManager().install(): orienta para instalar a versão do chromedriver compatível com a versão atual do google chrome
options = Options()
options.headless = True
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
#driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(15)

#Se o site não for aberto no formato desejado, fica tentando até conseguir
while check_element_css_exists() == False:
    print("")
    print("Página web não está no formato desejado :-(")            
    driver.close()
    driver = webdriver.Chrome(options=options)
    driver.get(url)
else:
    print("")
    print("Página web no formato desejado :-)")
    print("Buscando vagas...")
    pass

time.sleep(5)
close_modal()
#Fecha a barra de aviso de utilização de cookies
driver.find_element_by_id("dm876A").click()
#Fecha a barra de aviso de mídia social
driver.find_element_by_xpath("//button[@class='jss17 jss29 jss31 jss32 jss34 jss35 jss54 gupy-button gupy-button--lg sc-gKclnd gbwZcc root gupy-button--link']").click()

# incializando o dicionário que irá guardar as informações extraídas
result = {"empresa":[], "cargo":[], "cidade_uf":[], "atributos":[], "data_publicacao":[], "url":[]}

close_modal()

#Verifica se chegou na última página
last_page = driver.find_element_by_css_selector("button[aria-label='Next Page']").get_attribute("aria-disabled")

j = 1
while last_page == 'false':
    close_modal()
    soup = bs(driver.page_source, "html.parser")
    # Calculando a quantidade de empresas na página para realizar o for loop
    n_empresas = len(soup.findAll("span", attrs={"class": "sc-hUpaCq"}))
    last_page = driver.find_element_by_css_selector("button[aria-label='Next Page']").get_attribute("aria-disabled")
    #last_page = True                  
    for i in range (0, n_empresas):
        print(f"Vagas encontradas: {j}", end='\r')
        #Nome da empresa
        result["empresa"].append(soup.findAll("span", attrs={"class": "sc-hUpaCq"})[i].text)
        
        #Nome do cargo
        result["cargo"].append(soup.findAll("h4", attrs={"class": "sc-ikJyIC kwLwsZ sc-jgrJph hEyVya"})[i].text)
        
        #Cidade e UF de origem da vaga
        result["cidade_uf"].append(soup.findAll("p", attrs={"class": "sc-gSQFLo rEpvD"})[i].text)        
        
        #Atributos (tipo da vaga, local, etc)
        result["atributos"].append(soup.findAll("ul", attrs={"class": "sc-lbhJGD htYCld"})[i].getText(separator=u';'))
        
        #Data de publicação
        result["data_publicacao"].append(soup.findAll("span", attrs={"class": "sc-nVkyK QYVUi"})[i].text)
        
        #url da vaga
        result["url"].append(soup.findAll("a", attrs={"rel":"noreferrer", "target":"_blank"})[i]['href'])
        j = j + 1

    close_modal()
    #verifica se chegou na última página
    driver.find_element_by_css_selector("button[aria-label='Next Page']").click()
    page_loaded = False
    #Aguarda até a página ser carregada
    while page_loaded == False:
        page_loaded = wait_page_load(driver, 10)    

#Encerrar o selenium após o carregamento das informações inciais
driver.close()

#Salva as informações inciais em um dataframe
df = pd.DataFrame.from_dict(result)

# Cria um id interno pra cada vaga
df.insert(0, 'id_vaga', df.index + 1)

#Guarda as url de cada vaga
url_list = df['url'].tolist()

print("")
print("Buscando atribuições e qualificações...")
print(f"Páginas a serem consultadas: {len(url_list)}")

desc = {"id_vaga":[], "atribuicoes_raw":[], "qualificacoes_raw":[], "atribuicoes_cleaned":[], "qualificacoes_cleaned":[]}
n = 1

#Realizando um loop em cada vaga pra pegar as atribuições e qualificações exigidasS 
session = HTMLSession()
for url in url_list:
    print(f"Consultando página {n}", end='\r')
    # get the html content
    response = session.get(url)
    soup = bs(response.html.html, "html.parser")
    
    #ID da vaga
    desc["id_vaga"].append(n)
    cleaner_html = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    
    atribuicoes = re.findall(r'responsibilities(.*?)<h2>', ' '.join(str(soup).split()))
    if len(atribuicoes) == 0:
        atribuicoes2 = atribuicoes
        #Atribuições
        desc["atribuicoes_raw"].append(atribuicoes2)
        desc["atribuicoes_cleaned"].append(atribuicoes2)
    else:
        atribuicoes2 = atribuicoes[0]
        atribuicoes_c1 = re.sub(cleaner_html, ' ', atribuicoes2)
        atribuicoes_c2=re.sub("[;:!*?·•]"," ",atribuicoes_c1)
        atribuicoes_cleaned = ' '.join(atribuicoes_c2.split())
        #Atribuições
        desc["atribuicoes_raw"].append(atribuicoes2)
        desc["atribuicoes_cleaned"].append(atribuicoes_cleaned)        
    
    qualificacoes = re.findall(r'skills(.*?)<h2>', ' '.join(str(soup).split()))
    if len(qualificacoes) == 0:
        qualificacoes2 = qualificacoes
        #Qualificações
        desc["qualificacoes_raw"].append(qualificacoes2)    
        desc["qualificacoes_cleaned"].append(qualificacoes2)           
    else:
        qualificacoes2 = qualificacoes[0]
        qualificacoes_c1 = re.sub(cleaner_html, ' ', qualificacoes2)
        qualificacoes_c2=re.sub("[;:!*?·•]"," ",qualificacoes_c1)
        qualificacoes_cleaned = ' '.join(qualificacoes_c2.split())
        #Qualificações
        desc["qualificacoes_raw"].append(qualificacoes2)
        desc["qualificacoes_cleaned"].append(qualificacoes_cleaned)
    
    n = n + 1
#encerra a sessão após retornar rodas as qualificações e atribuições
session.close()

df_desc = pd.DataFrame.from_dict(desc)
#Juntando os dataframes de vagas com atribuicoes e qualificacoes
df_merged = df.merge(df_desc, how='left', on='id_vaga')

#Expandindo os atributos dos cargos para colunas
df_merged[['tp_contratacao','remoto']] = df_merged.atributos.str.split(";",expand=True,)

df_merged['cidade_uf'] = df_merged.cidade_uf.str.replace('-','/')
df_merged.cidade_uf.fillna(value='Não Informado / Não Informado', inplace=True)

#Lista de condições pra criar a variável indicadora de trabalho remoto com 'sim' e 'não'
conditions1 = [
    (df_merged['remoto'].str.upper().str.contains('REMOTO|REMOTE', na=False))
    ]
#criando uma lista dos valores que queremos atribuir para cada condição acima
values1 = ['Sim']
#Aplicando as condições e valores
df_merged.loc[:,'trab_remoto'] = np.select(conditions1, values1, default = 'Não')

#Lista de condições para limpar ainda mais a variável 'cidade_uf'
conditions2 = [
    (df_merged['cidade_uf']==' ')
    ]                                            
#criando uma lista dos valores que queremos atribuir para cada condição acima
values2 = ['Não Informado / Não Informado']
#Aplicando as condições e valores
df_merged.loc[:,'cidade_uf_clean'] = np.select(conditions2, values2, default=df_merged['cidade_uf'])

#Separando cidade e uf
df_merged[['cidade','uf']] = df_merged.cidade_uf_clean.str.split("/",expand=True,)
df_merged.cidade.fillna(value='Não Informado', inplace=True)
df_merged.uf.fillna(value='Não Informado', inplace=True)

#Lista de condições para transformar a variável 'tp_contratacao' do inglês para o português
conditions3 = [
    (df_merged['tp_contratacao'].str.upper()=='ASSOCIATE'),
    (df_merged['tp_contratacao'].str.upper()=='EFFECTIVE'),
    (df_merged['tp_contratacao'].str.upper()=='INTERNSHIP'),
    (df_merged['tp_contratacao'].str.upper()=='LECTURER'),
    (df_merged['tp_contratacao'].str.upper()=='LEGAL ENTITY'),
    (df_merged['tp_contratacao'].str.upper()=='OUTSOURCE'),
    (df_merged['tp_contratacao'].str.upper()=='SUMMER JOB'),
    (df_merged['tp_contratacao'].str.upper()=='TALENT POOL'),
    (df_merged['tp_contratacao'].str.upper()=='TRAINEE')
    ]
#criando uma lista dos valores que queremos atribuir para cada condição acima
values3 = ['Associado', 'Efetivo', 'Estágio', 'Docente', 'Pessoa Jurídica', 'Terceirizado', 'Emprego de verão', 'Banco de talentos', 'Trainee']
#Aplicando as condições e valores e renomeando as colunas
df_merged.loc[:,'tp_contratacao_pt'] = np.select(conditions3, values3, default = df_merged['tp_contratacao'])
df_merged.rename(columns={"tp_contratacao": "tp_contratacao_old", "tp_contratacao_pt": "tp_contratacao"}, inplace=True)
#Tratando a variável 'data_publicacao' para apresentar apenas a data
df_merged["data_publicacao"] = df_merged["data_publicacao"].str.upper().str.replace("VAGA PUBLICADA EM:|JOB PUBLISHED ON:","")

#Registrando a data e hora em que os ajustes terminaram de serem realizados e carregados
df_merged['dh_carga'] = datetime.now()

#Cirando o dataframe apenas com as vagas para cargos de DATA SCIENTIST ou CIENTISTA DE DADOS e selecionando as colunas que irão se carregadas na base de dados final
df_ds = df_merged[df_merged['cargo'].str.upper().str.contains('DATA SCIENTIST|CIENTISTA DE DADOS|CIÊNTISTA DE DADOS')]
df_ds2csv = df_ds[['id_vaga', 'empresa', 'cargo', 'data_publicacao', 'url', 'atribuicoes_raw', 'atribuicoes_cleaned', 'qualificacoes_raw', 'qualificacoes_cleaned', 'tp_contratacao', 'trab_remoto', 'cidade', 'uf', 'dh_carga']]


####################################################################################################################################################
dt_carga = datetime.strptime(str(df_ds2csv['dh_carga'].max()), '%Y-%m-%d %H:%M:%S.%f').strftime("%d/%m/%Y")

#Retornando a base de dados históricos
BUCKET = 'vagas-ds-storage'
df_hist_base = get_s3_csv('gupy_base_historica.csv', BUCKET)

df_hist_base.drop(df_hist_base[df_hist_base['dt_carga'] == dt_carga].index, inplace = True)

df_hist_base = df_hist_base.append(df_ds2csv)

df_hist_base['dt_carga'] = pd.to_datetime(df_hist_base['dh_carga'], format='%Y-%m-%d %H:%M:%S').dt.strftime("%d/%m/%Y")
df_historico = df_hist_base.sort_values(['empresa', 'cargo', 'dt_carga', 'dh_carga']).drop_duplicates(subset=['empresa', 'cargo', 'dt_carga'],keep='last', ignore_index=True)
df_historico = df_historico.sort_values(['dt_carga', 'empresa'])

contagem_historica = df_historico.groupby('dt_carga').count()[['cargo']]
contagem_historica.rename(columns={"cargo": "qtd_vagas"}, inplace=True)
contagem_historica.reset_index(inplace=True)
#####################################################################################################################################################
#salvando as bases de dados para o S3
save2s3(df_merged, 'vagas-ds-storage', 'gupy_base_consulta_completa.csv')
save2s3(df_ds2csv, 'vagas-ds-storage', 'gupy_base_ds.csv')
save2s3(df, 'vagas-ds-storage', 'base_gupy_part1.csv')
save2s3(df_historico, 'vagas-ds-storage', 'gupy_base_historica.csv')
save2s3(contagem_historica, 'vagas-ds-storage', 'gupy_historico_vagas.csv')

#chamando os programas que geram o sistema de recomendação, wordcloud e mapa de vagas para serem executados
os.system('python3 recommender_system_publico.py')
os.system('python3 wordcloud_gupy_publico.py')
os.system('python3 mapa_vagas_gupy_publico.py')

end_time = datetime.now()

print("")
print(f'Tempo de execução: {end_time - start_time}')



