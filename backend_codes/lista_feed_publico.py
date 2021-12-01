##############################################################################################################################
## Este programa verifica as incrições, cancelamentos do dia, produz a lista de envio de e-mails e salva em um bucket do S3 ##
##############################################################################################################################

import pandas as pd
import io
import boto3

#Instanciando um client S3 com boto
s3_client = boto3.client(
    "s3",
    aws_access_key_id='SUA_CHAVE_AQUI',
    aws_secret_access_key='SUA_CHAVE_AQUI'
)

BUCKET = 'vagas-ds-storage'
PREFIX1 = 'inscricoes_dia/'
PREFIX2 = 'cancelamentos_dia/'

#Função para listar os arquivos de uma pasta em um bucket do S3
def ListFiles(client, bucket, prefix):
    """List files in specific S3 URL"""
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for content in response.get('Contents', []):
        yield content.get('Key')

#Função para retornar um arquivo de uma pasta        
def get_s3_csv(csv_file, bucket):
    response = s3_client.get_object(Bucket=bucket, Key=csv_file)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
            print(f"Successful S3 get_object response. Status - {status}")
            df = pd.read_csv(response.get("Body"))
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")
    return df

#Retornando a lista de inscrições
df_base = get_s3_csv('lista_feed/lista_inscricoes.csv', BUCKET)

#Listando as inscrições ocorridas no dia e limpando a lista     
inscricoes_file_list = list(ListFiles(s3_client, BUCKET, PREFIX1))
inscricoes_file_list.remove('inscricoes_dia/')

#Se houve alguma inscrição no dia, então adicioná-las à lista de inscrições. Caso contrário, exibir uma mensagem alertando que não houveram inscrições no dia e seguir com 
#o código
if len(inscricoes_file_list) > 0:
    for file in inscricoes_file_list:
        print (file)
        df_temp = get_s3_csv(file, BUCKET)
        df_base = df_base.append(df_temp)
else:
    print('Não existem inscrições hoje')
    pass

#Caso a pessoa que se inscreveu no dia, já constava na lista de incrições, então será mantida a inscrição do dia, com status de ativa e com as novas preferências de vagas
df_inscricoes = df_base.sort_values('dh_inscricao').drop_duplicates('email',keep='last', ignore_index=True)

#Listando os cancelamentos ocorridos no dia e limpando a lista  
cancel_file_list = list(ListFiles(s3_client, BUCKET, PREFIX2))
cancel_file_list.remove('cancelamentos_dia/')

#Criando um dataframe para guardar os cancelamentos do dia
df_cancel = pd.DataFrame.from_dict({"email":[], "dh_cancelamento":[]})

#Se houve algum cancelamento no dia, compará-las com a lista de inscritos. Caso a pessoa já conste na lista de inscrições e se o cancelamento ocorreu após
#a incrição, então marcar a inscrição com o status de inativa (zero). Caso não haja cancelamentos, exibir uma mensagem alertando que não houveram cancelamentos no dia 
if len(cancel_file_list) > 0:
    for file in cancel_file_list:
        df_temp = get_s3_csv(file, BUCKET)
        df_cancel = df_cancel.append(df_temp, ignore_index=True)
    df_cadastro = df_inscricoes.merge(df_cancel, how='left', on='email')
    df_cadastro.loc[df_cadastro.dh_cancelamento > df_cadastro.dh_inscricao, "ind_envio_email"] = 0
    df_cadastro.drop(columns=['dh_cancelamento'], inplace=True)
else:
    print('Não existem cancelamentos hoje')
    df_cadastro = df_inscricoes

#Gerar o df só com as pessoas com o status ativo para envio de e-mail (valor 1)
df_envio_email = df_cadastro[df_cadastro['ind_envio_email'] == 1]

#Função para salvar os arquivos de incrições e de envio de e-mails no S3
def save2s3(df, bucket, filename):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    response = s3_client.put_object(Bucket=bucket, Key=filename, Body=csv_buffer.getvalue())
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print("")
        print(f"Arquivo {filename} gravado com successo no S3. Status - {status}")
    else:
        print("")
        print(f"Arquivo {filename} não gravado no S3. Status - {status}")
    return status

#Salvando os arquivos de incrições e de envio de e-mails no S3 e deletando as inscrições e cancelamentos do dia, caso as gravações ocorram com sucesso
filename1 = 'lista_feed/lista_inscricoes.csv'
filename2 = 'lista_feed/lista_envio_feed.csv'
status_envio_1 = save2s3(df_cadastro, 'vagas-ds-storage', filename1)
status_envio_2 = save2s3(df_envio_email, 'vagas-ds-storage', filename2)
print(status_envio_1)
print(status_envio_2)

if status_envio_1 == 200 and status_envio_2 == 200 and len(inscricoes_file_list) > 0:
    for object in inscricoes_file_list:
        print('Deleting', object)
        s3_client.delete_object(Bucket=BUCKET, Key=object)
elif len(inscricoes_file_list) == 0:
    print("")
    print(f"Não existem novas inscrições hoje")  
else:
    print("")
    print(f"Arquivos não deletados. Status Lista Inscrições - {status_envio1}")
    print(f"Arquivos não deletados. Status Lista Envio e-mail - {status_envio2}")

if status_envio_1 == 200 and status_envio_2 == 200 and len(cancel_file_list) > 0:
    for object in cancel_file_list:
        print('Deleting', object)
        s3_client.delete_object(Bucket=BUCKET, Key=object)        
elif len(cancel_file_list) == 0:
    print("")
    print(f"Não existem novos cancelamentos hoje")  
else:
    print("")
    print(f"Arquivos não deletados. Status Lista Inscrições - {status_envio1}")
    print(f"Arquivos não deletados. Status Lista Envio e-mail - {status_envio2}")

print(df_cadastro)
print(' ')
print(df_envio_email)



