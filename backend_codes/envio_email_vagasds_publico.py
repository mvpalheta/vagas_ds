###########################################################################################################
## Este programa checa a lista de envio de e-mails e envia conforme as preferências de vagas cadastradas ##
###########################################################################################################

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import io
import boto3
import ast
import csv

#Instanciando um client S3 com boto
s3_client = boto3.client(
    "s3",
    aws_access_key_id='SUA_CHAVE_AQUI',
    aws_secret_access_key='SUA_CHAVE_AQUI'
)

BUCKET = 'vagas-ds-storage'

#Função para criar um campo com o link para a vaga
def make_skill_link(id_vaga):
    text = 'Mais...'
    return f'<a target="_blank" href=https://vagas-ds-skills-resp.herokuapp.com/?idvaga={id_vaga}>'

#Função para carregar a base de dados
def load_data():
    df = pd.read_csv('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/gupy_base_ds.csv')
    df['id_vaga'] = df['id_vaga'].values.astype(str)
    df.sort_values(by=['empresa'], inplace=True)
    df['link_vaga'] = df['id_vaga'].apply(make_skill_link)
    return df

#Carregando a base de dados
df = load_data()

#Carregando a lista de e-mails para onde enviar as vagas
response = s3_client.get_object(Bucket=BUCKET, Key='lista_feed/lista_envio_feed.csv')
lines = response['Body'].read().decode("utf-8")
lines = lines.splitlines()
reader = csv.reader(lines)
next(reader)  # Skip header row

#E-mail de senha do rementente
sender_email = "SEU_EMAIL"
password = "SUA_SENHA_DO_PROVEDOR_DE_EMAIL"

#Loop para enviar os a-mails para cada pessoa inscrita no feed de vagas
for nome, email, remoto, tp_contratacao, dh_inscricao, ind_envio_email in reader:
    prim_nome = nome.split()[0] #Retornando o primeiro nome da pessoa para deixar um e-mail mais personalizado e amigável
    remoto2 = ast.literal_eval(remoto) #Retornando a indicação de trabalho remoto que cada pessoa selecionou na inscrição
    tp_contratacao2 = ast.literal_eval(tp_contratacao) #Retornando o tippo de contratação que cada pessoa selecionou na inscrição
    df_filtered = df[df["trab_remoto"].isin(remoto2) & df["tp_contratacao"].isin(tp_contratacao2)] #Filtrando a base de dados de acordo com as preferências de cada pessoa
    qtd_vagas = len(df_filtered) #Contando a quantidade de vagas disponíveis de acordo com as preferências
    #Instanciando duas listas vazias que irão guardar o corpo do e-mail tanto na versão HTML quanto apenas texto simples
    #Importante ressaltar que, como nem todos os clientes de e-mail exibem conteúdo HTML por padrão, e algumas pessoas optam por receber apenas e-mails em 
    #texto simples por razões de segurança, é importante incluir uma alternativa em texto simples para mensagens HTML
    lista_url_metadados = ''
    lista_texto = ''
    
    #Loop para montar o corpo do texto para cada e-mail a ser enviado
    for i in df_filtered.index:
        #Para cada vaga que corresponda às preferências da pessoa será criado um parágrafo no e-mail contendo o nome do cargo com o link para a vaga, o nome da empresa
        #cidade e UF de origem e se aceita ou não trabalho remoto (para as pessoas que se increveram para receber apenas vagas de trabalho remoto, esse campo aparecerá apenas como 'sim')
        cargo = df_filtered.loc[i, "cargo"] 
        link_vaga = df_filtered.loc[i, "link_vaga"]
        empresa = df_filtered.loc[i, "empresa"]
        cidade = df_filtered.loc[i, "cidade"]
        uf = df_filtered.loc[i, "uf"]
        trab_remoto = df_filtered.loc[i, "trab_remoto"]
        id_vaga = df_filtered.loc[i, "id_vaga"] #essa variável é utilizada apenas para a alternativa em texto simples
        
        #montando o corpo do texto para HTML
        url_vaga = "<p style='font-size:16px;'><b>" + link_vaga + cargo + "</a></b><br> "
        metadados_vaga = str(empresa) + " - " + str(cidade) + " - "  + str(uf) + " - "  + "Aceita remoto: " + trab_remoto + "</p>"
        url_metadados = url_vaga + metadados_vaga
        lista_url_metadados = lista_url_metadados + url_metadados
        
        #Montando o corpo do texto para texto simples
        url_text ="https://vagas-ds-skills-resp.herokuapp.com/?idvaga=" + id_vaga
        metadados_vaga_text = str(empresa) + " - " + str(cidade) + " - "  + str(uf) + " - "  + "Aceita remoto: " + trab_remoto
        url_metadados2 = cargo + " - " + metadados_vaga_text + " - " + url_text + "\n"
        lista_texto = lista_texto + url_metadados2
        
# Criando as versões em texto simples e HTML completo para as mensagens
    text = """\
    Olá, {nome}, tudo blz? Olha só que legal, hoje existem {qtd_vagas} vagas de cientista de dados compatíveis com suas preferências. Confira abaixo:
    
    {lista_texto}\n
    Para conferir outras vagas siga o link ao lado: https://vagas-ds.herokuapp.com/ \n
    Você está recebendo esta mensagem porque se inscreveu em nosso espaço. Se desejar parar de receber este alerta, basta clicar neste link: https://vagas-ds-unsubscribe.herokuapp.com/?usuario={email}
    """.format(nome=prim_nome, qtd_vagas=qtd_vagas, lista_texto=lista_texto, email=email)
    
    html = """\
    <html>
      <body>
        <h2>Olá, {nome}, tudo blz? Olha só que legal, hoje existem <font color="red">{qtd_vagas} vagas</font> de cientista de dados compatíveis com suas preferências. Confira abaixo:</h2>

           {lista_url_metadados}
        <br>
        <p>Para conferir outras vagas <a target="_blank" href="https://vagas-ds.herokuapp.com/">clique aqui.</a></p>
        <p>Você está recebendo esta mensagem porque se inscreveu em nosso espaço. Se desejar parar de receber este alerta, <a target="_blank" href="https://vagas-ds-unsubscribe.herokuapp.com/?usuario={email}">basta clicar aqui.</a></p>

      </body>
    </html>
    """.format(nome=prim_nome,qtd_vagas=qtd_vagas, lista_url_metadados=lista_url_metadados, email=email)
    
    #Configurações para o envio das vagas
    message = MIMEMultipart("alternative")
    message["Subject"] = "Alerta de vagas do Vagasds"
    message["From"] = 'noreply-vagasds@gmail.com'
    message["To"] = email

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Adicionando o corpo do texto, tanto em HTML quanto texto simples, à mensagem MIMEMultipart
    # Como o cliente de e-mail tentará renderizar primeiro o último anexo multipart, certifique-se de adicionar a mensagem HTML após a versão em texto simples.
    message.attach(part1)        
    message.attach(part2)



    #Criando uma conexão segura com o provedor de envio de e-mail e enviando a mensagem
    context = ssl.create_default_context()
    #O Gmail requer que você se conecte à porta 465 se estiver usando SMTP_SSL () e à porta 587 ao usar .starttls (), Caso seu provedor de e-mail seja outro, verifique qual a porta necessária
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, email, message.as_string()
        )
    del message['To']