##################################################################################################################
## Este programa produz o mapa utilizado no app e salva como um pickle em um bucket do S3. A ideia é otimizar o ##
## carregamento do app sem perder a funcionalidade de hover do mapa                                             ##
##################################################################################################################

import plotly.express as px
from urllib.request import urlopen
import json
import pandas as pd
import io
import boto3
import pickle

#Função para salvar os resultados no S3
def save2s3(mapa, bucket, filename):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id='SUA_CHAVE_AQUI',
        aws_secret_access_key='SUA_CHAVE_AQUI'
    )
    serializedMyMap = pickle.dumps(mapa)
    response = s3_client.put_object(Bucket=bucket, Key=filename, Body=serializedMyMap, ACL ='public-read')
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        print("")
        print(f"Arquivo {filename} gravado com successo no S3. Status - {status}")
    else:
        print("")
        print(f"Arquivo {filename} não gravado no S3. Status - {status}")

#Carregando a base de dados
df = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/gupy_base_ds.csv')

#Carregando o geojson com os limites das Ufs brasileiras
with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brazil = json.load(response)
#Contando a qtde de vagas por UF
vagas_uf = df.groupby(['uf']).agg({'cargo': 'count'})
vagas_uf.reset_index(inplace=True)
vagas_uf['uf'] = vagas_uf['uf'].str.strip()

#criando um dicionário pra guardar os IDs das Ufs, guardando-os e transformando num dataframe
state_id_map = {"uf":[]}
for feature in Brazil ['features']:
    state_id_map['uf'].append(feature['properties']['name'])
all_uf = pd.DataFrame.from_dict(state_id_map)

#juntando a quantidade de vagas por UFs com os IDs das mesmas e renomeando o campo 'cargo'
dfmerged = all_uf.merge(vagas_uf, how='left', on='uf').fillna(0)
df2map = dfmerged.rename(columns={"cargo": "vagas"})

#gerando o mapa
title={
'text': "Distribuição espacial das vagas",
'y':0.9,
'x':0.5,
'xanchor': 'center',
'yanchor': 'top'}
fig = px.choropleth(
                    df2map,
                    locations = 'uf', #define the limits on the map/geography
                    geojson = Brazil, #shape information
                    featureidkey="properties.name",
                    color = "vagas", #defining the color of the scale through the database
                    hover_name = 'uf', #the information in the box
                    hover_data =["vagas"],
                    color_continuous_scale = "blues",
                    range_color = (0, 10)
                    )
fig.update_layout(coloraxis_showscale=False, title=title, title_font_size=22, width=1100, height=600)
mapa = fig.update_geos(fitbounds = "locations", visible = False)

#salvando o mapa no S3 como um pickle
save2s3(mapa, 'vagas-ds-storage', 'mapa_vagas_gupy.pkl')

    
