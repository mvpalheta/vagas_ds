from resources import *

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title='Vagas cientista de dados')

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
m = st.markdown("""
<style>
div.stButton > button:first-child {
    padding-top: 0px;
    padding-bottom: 0px;
    --border-color: #ffffff;
    --background-color: rgba(255, 255, 0, 00);
    margin-top: -100px;
    margin-bottom: -100px;
    --height: 0px;
    font-size: 16px;
    color: blue;
    text-decoration:underline;
    
}
</style>""", unsafe_allow_html=True)

st.markdown(""" <style >
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown(""" <style type="text/css"> 
div.css-sg054d {
  display:none;
}
</style>""", unsafe_allow_html=True)


df_all = load_data()
id_list = df_all["id_vaga"].tolist()
cosine_sim = load_cosine_sim()

try:
    options = id_list

    query_params = st.experimental_get_query_params()
    query_option = query_params['idvaga'][0] #throws an exception when visiting http://host:port
    with st.sidebar.expander(''):
        option_selected = st.selectbox(' ',
                                                options,
                                                index=options.index(query_option))
    if option_selected:
        st.experimental_set_query_params(idvaga=option_selected)

# run when query params don't exist. e.g on first launch
except: # catch exception and set query param to predefined value
    options = id_list
    st.experimental_set_query_params(idvaga=options[0]) #default para o primeiro valor da lista

    query_params = st.experimental_get_query_params()
    query_option = query_params['idvaga'][0]
    with st.sidebar.expander(''):
        option_selected = st.selectbox(' ',
                                                options,
                                                index=options.index(query_option))
    if option_selected:
        st.experimental_set_query_params(idvaga=option_selected)

def main():
    empresa = df_all[(df_all['id_vaga']==option_selected)][['empresa']].to_string(header=False, index=False)
    cargo = df_all[(df_all['id_vaga']==option_selected)][['cargo']].to_string(header=False, index=False)
    trab_remoto = df_all[(df_all['id_vaga']==option_selected)][['trab_remoto']].to_string(header=False, index=False)
    url = df_all[(df_all['id_vaga']==option_selected)][['url']].to_string(header=False, index=False)

    data_recomend = get_recommendations(df_all, option_selected, cosine_sim)

    st.markdown('##### **Talvez estas vagas também sejam interessantes para você**')    
    recommend_list = {}
    cols = st.columns(5)
    for i in [0, 1, 2, 3, 4]:
        recommend_list["cargo"+str(i)] = data_recomend.iloc[[i]][['cargo']].to_string(header=False, index=False)
        recommend_list["empresa"+str(i)] = data_recomend.iloc[[i]][['empresa']].to_string(header=False, index=False)
        recommend_list["tp_contratacao"+str(i)] = data_recomend.iloc[[i]][['tp_contratacao']].to_string(header=False, index=False)
        recommend_list["trab_remoto"+str(i)] = data_recomend.iloc[[i]][['trab_remoto']].to_string(header=False, index=False)
        recommend_list["url_skills"+str(i)] = data_recomend.iloc[[i]][['skills_link']].to_string(header=False, index=False)
        with cols[i]:
            st.markdown('<p style="background-color:#ecfbff;color:black;font-size:24px;border: 1px solid #ecfbff;border-radius:8px;padding: 2px;font-size:16px;"><font style="font-size:16px;"><b>'
            +recommend_list["cargo"+str(i)] + '</b></font>'
            '<br>'+recommend_list["empresa"+str(i)]+
            '<br>'+recommend_list["tp_contratacao"+str(i)]+
            '<br>Trabalho remoto: '+recommend_list["trab_remoto"+str(i)]+
            '<br>'+recommend_list["url_skills"+str(i)]+'</p>', unsafe_allow_html=True) 

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### " + empresa + " - " + cargo + '<font style="font-size:18px;"><br>Trabalho remoto: ' + trab_remoto + '</b></font>', unsafe_allow_html=True)
    with col2:
        st.markdown("<p align='center', style='font-size:20px;'>" + url + "</p>", unsafe_allow_html=True)

    st.markdown("##### Atribuições:")
    atribuicoes = df_all[(df_all['id_vaga']==option_selected)][['atribuicoes_raw']].to_string(header=False, index=False)
    st.markdown(atribuicoes, unsafe_allow_html=True,)

    st.markdown("##### Qualificações:")
    qualificacoes = df_all[(df_all['id_vaga']==option_selected)][['qualificacoes_raw']].to_string(header=False, index=False)
    st.markdown(qualificacoes, unsafe_allow_html=True,)

if __name__ == "__main__":
    main()