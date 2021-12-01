from resources import *
from eda import *
from datetime import datetime
import pickle
from urllib.request import urlopen

st.set_page_config(layout="wide", page_title='Vagas cientista de dados')

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 230px;
        padding-top: 60px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 230px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        padding-top: 0px;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown(""" <style type="text/css"> 
div.streamlit-expanderHeader {
  display:none;
}
</style>""", unsafe_allow_html=True)


def main():
    df = load_data('gupy_base_ds.csv')[['empresa', 'cargo', 'tp_contratacao', 'trab_remoto', 'cidade', 'uf', 'url', 'id_vaga']]
    df_all = load_data('gupy_base_ds.csv')
    df_tp_contratacao = load_data('gupy_base_consulta_completa.csv')[['tp_contratacao']]
########################################################### SIDEBAR ##############################################################    

    st.sidebar.selectbox('Selecione a página para navegar:', ['Home', 'Análise exploratória', 'Lista de vagas'], key='page_nav')
    st.sidebar.download_button(
    label="Baixar dados como CSV",
    data=convert_df(df[['empresa', 'cargo', 'tp_contratacao', 'trab_remoto', 'cidade', 'uf', 'url']]),
    file_name='vagas_gupy.csv',
    mime='text/csv',
    help = 'Baixar a lista de vagas para um arquivo CSV')
    if "notif_btn2" not in st.session_state:
        st.session_state.notif_btn2 = False
    notif_btn = st.sidebar.button(label="Receber/alterar notificações no e-mail")
    if notif_btn:
        st.session_state.notif_btn2 = True
    dh_carga = df_all['dh_carga'].max()
    dt_carga = datetime.strptime(dh_carga, '%Y-%m-%d %H:%M:%S.%f').strftime("%d/%m/%Y")
    st.sidebar.write("Última atualização: "+dt_carga)
    st.sidebar.write('Críticas e/ou sugestões: mvpalheta@gmail.com')
     
########################################## Formulário para receber notificações de vagas ##########################################
    if st.session_state.notif_btn2==True:
        def send_form_success():
            st.session_state.page_nav = "confirma_envio_form"
            st.session_state.notif_btn2 = False
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(' ')
            with col2:
                with st.expander('', expanded=True):
                    st.success('Cadastro realizado com sucesso!!!')
                    st.button(label="OK", on_click=reset_btn2)                    
            with col3:
                    st.write(' ')

        def reset_btn2():
            st.session_state.notif_btn2 = False

        feed = {"nome":[], "email":[], "remoto":[], "tp_contratacao":[], "dh_inscricao":[], "ind_envio_email":[]}
        st.subheader('Receber/alterar notificações de vagas')
        st.write("Preencha os campos abaixo para receber notificações de vagas no seu e-mail. Caso você já receba nossas notificações, \
            o envio do formulário irá atualizar sua preferências.")
        nome = st.text_input("Seu nome", key="nome")
        e_mail2 = st.text_input("Seu e-mail", key="email2")
        if (e_mail2 != '' and '@' not in e_mail2) or ',' in e_mail2:
            st.error("E-mail incorreto")

        remoto_val2 = st.multiselect("Trabalho remoto?", sorted(list(dict.fromkeys(df["trab_remoto"].tolist()))))

        contratacao_val2 = st.multiselect("Tipo contratação", sorted(list(dict.fromkeys(df_tp_contratacao["tp_contratacao"].tolist()))), key="mult_ntf")

        def enviar_form():
            if nome.replace(' ', '') == '':
                st.error("Por favor, preencha seu nome")            
            elif (e_mail2 != '' and '@' not in e_mail2) or e_mail2 == '' or ',' in e_mail2:
                st.error("E-mail incorreto")
            elif len(remoto_val2) == 0:
                st.error("Selecione ao menos uma opção de trabalho remoto")
            elif len(contratacao_val2) == 0:
                st.error("Selecione ao menos uma opção de tipo de contratação")                
            else:
                feed["nome"].append(nome)
                feed["email"].append(e_mail2)
                feed["remoto"].append(remoto_val2)
                feed["tp_contratacao"].append(contratacao_val2)
                feed["dh_inscricao"].append(datetime.now())
                feed["ind_envio_email"].append(1)
                df_feed = pd.DataFrame.from_dict(feed)
                filename = 'inscricoes_dia/querofeed_' + e_mail2 + '.csv'
                status = save2s3(df_feed, 'vagas-ds-storage', filename)
                if status == 200:
                    send_form_success()
                else:
                    st.error('Ocorreu algum problema no envio. Por favor, tente novamente.')      
        col1, col2 = st.columns([1,10])
        with col1:
                st.button('Enviar', on_click=enviar_form)
        with col2:
                st.button("Fechar", on_click=reset_btn2)          
########################################################### HOME ##############################################################
    elif st.session_state.page_nav == 'Home':
        st.subheader('Bem vindo ao espaço de divulgação de vagas de cientista de dados disponíveis no site da Gupy!!!')
        st.markdown("<p align='center', style='color:#27add9;font-size:30px;'> <b>Atualmente encontram-se disponíveis</b> </p>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("")
        with col2:
            st.metric(label="Qtd. Vagas", value=str(df.shape[0]))            
        with col3:
            st.metric(label="Qtd. empresas", value=str(len(pd.unique(df['empresa']))))
        with col4:
            st.metric(label="Qtd. Cidades", value=str(len(pd.unique(df['cidade']))))
        with col5:
            st.metric(label="Qtd. de UFs", value=str(len(pd.unique(df['uf']))))        
        st.markdown('<p>Esta página tem por objetivo coletar e divulgar vagas de cientista de dados a partir do site da Gupy. A Gupy \
                    é uma startup de RH fundada em 2015 que presta serviços de recrutamento e seleção e vem crescendo bastante nos últimos \
                    anos. Atualmente grande empresas como Santander, Americanas, Ambev, Vivo, dentre outras utilizam sua plataforma para \
                    anunciar vagas. Sendo assim, esta plataforma se apresenta como ótimo espaço para quem busca uma vaga \
                    seja para recolocação, transição de carreira e/ou empresa ou mesmo acompanhar o mercado de trabalho desta \
                    área.</p> \
                    <p>Além de coletar e divulgar a lista de vagas de cientista de dados disponíveis atualmente na plataforma da Gupy, \
                    este espaço também apresenta alguns resultados exploratórios sobre os dados coletados além de um sistema de recomendação \
                    de vagas semelhantes. Além disto, ainda é possível realizar o download dos dados utilizados aqui.</p> \
                    Sinta-se a vontade para navegar e enviar sugestões. <font style="font-size:20px;"><b>Enjoy</b></font>!!!', unsafe_allow_html=True)

#################################################### ANALISE EXPLORATORIA ######################################################
    elif st.session_state.page_nav == 'Análise exploratória':
        st.header('Análise exploratória das vagas')
        st.subheader('Esta página apresenta alguns resultados exploratórios acerca dos dados')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("")
        with col2:
            st.metric(label="Qtd. Vagas", value=str(df.shape[0]))            
        with col3:
            st.metric(label="Qtd. empresas", value=str(len(pd.unique(df['empresa']))))
        with col4:
            st.metric(label="Qtd. Cidades", value=str(len(pd.unique(df['cidade']))))
        with col5:
            st.metric(label="Qtd. de UFs", value=str(len(pd.unique(df['uf']))))
        
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            fig1 = graph_top10(df, 'empresa', 'cargo', 'count', title="Top 10 empresas com mais vagas disponíveis", 
                xlabel="Nº de vagas", ylabel='Empresa')
            st.pyplot(fig1)
        with col2:
            all_obs = df.shape[0]
            remoto = df[df.trab_remoto=='Sim'].shape[0]
            n_remoto = all_obs - remoto

            x = ["Remoto", "Não remoto"]
            height = [remoto, n_remoto]

            plt.figure(figsize=(8,4.5))
            plt.bar(x, height, color="#27add9")
            plt.text(0-.1,height[0]+(max(height)*0.015), str(round(100*height[0]/sum(height),2))+"%", fontsize=13)
            plt.text(1-.1,height[1]+(max(height)*0.015), str(round((100*height[1]/sum(height)),2))+"%", fontsize=13)
            plt.ylim(0, (height[0]+(height[0]*0.1)))
            plt.title('% de trabalho remoto e não remoto', fontsize=12)
            fig2 = plt
            st.pyplot(fig2)

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            df_remoto = df[df['trab_remoto'] != 'Não']
            fig3 = graph_top10(df_remoto, 'empresa', 'cargo', 'count', title="Top 10 empresas com mais vagas remotas", 
                                xlabel="Nº de vagas", ylabel='Empresa')
            st.pyplot(fig3)
        with col2:
            fig4 = graph_top10(df, 'tp_contratacao', 'cargo', 'count', top=None, title="Tipos de contratações com vagas disponíveis", 
                                xlabel="Nº de vagas", ylabel='Tipo de contratação', figsize=(12,7))
            st.pyplot(fig4)

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            fig5 = graph_top10(df, 'uf', 'cargo', 'count', title="Top 10 UFs com mais vagas disponíveis", 
                                xlabel="Nº de vagas", ylabel='UF')
            st.pyplot(fig5)
        with col2:
            fig6 = graph_top10(df, 'cidade', 'cargo', 'count', title="Top 10 cidades com mais vagas disponíveis", 
                                xlabel="Nº de vagas", ylabel='Cidade')
            st.pyplot(fig6)

        st.plotly_chart(pickle.load(urlopen("https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/mapa_vagas_gupy.pkl")))

        col1, col2 = st.columns(2)
        with col1:
            st.image(image_from_s3('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/wordcloud_atribuicoes.png'), width=550)

        with col2:
            st.image(image_from_s3('https://vagas-ds-storage.s3.sa-east-1.amazonaws.com/wordcloud_qualificacoes.png'), width=550)

            

#################################################### LISTA DE VAGAS ############################################################
    elif st.session_state.page_nav == "Lista de vagas":
        st.title("Lista de vagas disponíveis atualmente")
        col1, col2 = st.columns(2)
        with col1:
            empresas1 = st.multiselect("Filtrar por empresas:", sorted(list(dict.fromkeys(df["empresa"].tolist()))))
            df_filtered1 = df[df['empresa'].isin(empresas1)]
        
        if len(empresas1) == 0:
            with col2:
                remoto1 = st.multiselect("Trabalho remoto?", sorted(list(dict.fromkeys(df["trab_remoto"].tolist()))))
                df_filtered2 = df[df['trab_remoto'].isin(remoto1)]
        else:
            with col2:
                remoto1 = st.multiselect("Trabalho remoto?", sorted(list(dict.fromkeys(df_filtered1["trab_remoto"].tolist()))))
                df_filtered3 = df_filtered1[df_filtered1['trab_remoto'].isin(remoto1)]

        ########################################################################################################################
        columns_list = ['empresa', 'cargo', 'tp_contratacao', 'trab_remoto', 'cidade', 'uf', 'id_vaga']
        rename_columns = {'empresa': 'Empresa', 'cargo': 'Cargo', 'tp_contratacao': 'Contrato', 'trab_remoto': 'Remoto', 'cidade': 'Cidade', 'uf': 'UF', 'id_vaga': 'Mais'}
        if len(empresas1) == 0 and len(remoto1) == 0:
            col1, col2 = st.columns([1,6])
            with col1:
                st.markdown("Nº de vagas: "+str(df.shape[0]))
            with col2:
                st.markdown("Qtd. empresas: "+str(len(pd.unique(df['empresa']))))                
            st.write(df[columns_list].rename(columns=rename_columns).to_html(escape=False, index=False), unsafe_allow_html=True, width=1200, height=800)
        
        elif len(empresas1) > 0 and len(remoto1) == 0:
            col1, col2 = st.columns([1,6])
            with col1:
                st.markdown("Nº de vagas: "+str(df_filtered1.shape[0]))
            with col2:
                st.markdown("Qtd. empresas: "+str(len(pd.unique(df_filtered1['empresa']))))
            st.write(df_filtered1[columns_list].rename(columns=rename_columns).to_html(escape=False, index=False), unsafe_allow_html=True, width=1200, height=500)

        elif len(empresas1) == 0 and len(remoto1) > 0:
            col1, col2 = st.columns([1,6])
            with col1:
                st.markdown("Nº de vagas: "+str(df_filtered2.shape[0]))
            with col2:
                st.markdown("Qtd. empresas: "+str(len(pd.unique(df_filtered2['empresa']))))
            st.write(df_filtered2[columns_list].rename(columns=rename_columns).to_html(escape=False, index=False), unsafe_allow_html=True, width=1200, height=500)

        elif len(empresas1) > 0 and len(remoto1) > 0:
            col1, col2 = st.columns([1,6])
            with col1:
                st.markdown("Nº de vagas: "+str(df_filtered3.shape[0]))
            with col2:
                st.markdown("Qtd. empresas: "+str(len(pd.unique(df_filtered3['empresa']))))            
            st.write(df_filtered3[columns_list].rename(columns=rename_columns).to_html(escape=False, index=False), unsafe_allow_html=True, width=1200, height=500)

    ######################################## Página de confirmação de envio dos dados para notificação ####################################
    elif st.session_state.page_nav == "confirma_envio_form":
        st.write("")
        


if __name__ == "__main__":
    main()