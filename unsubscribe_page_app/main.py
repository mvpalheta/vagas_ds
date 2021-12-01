from resources import *
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title='Vagas cientista de dados')

st.markdown(""" <style type="text/css"> 
div.streamlit-expanderHeader {
  display:none;
}
</style>""", unsafe_allow_html=True)

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown(""" <style type="text/css"> 
div.css-sg054d {
  display:none;
}
</style>""", unsafe_allow_html=True)

#Esse trecho try/except envia o e-mail da pessoa como parâmetro na URL da página, para que o mesmo seja capturado e salvado no S3 quando a pessoa
#confirmar o cancelamento
try:
    query_params = st.experimental_get_query_params()
    query_option = query_params['usuario'][0] #lança uma exceção ao visitar http://host:port
    with st.sidebar.expander(''):
        text_added = st.text_input(' ', value=query_option)
    if text_added != '':
        st.experimental_set_query_params(usuario=text_added)

# run when query params don't exist. e.g on first launch
except: # catch exception and set query param to predefined value
    st.experimental_set_query_params(usuario='None') #default para o primeiro valor da lista

    query_params = st.experimental_get_query_params()
    query_option = query_params['usuario'][0]
    with st.sidebar.expander(''):
        text_added = st.text_input(' ', value=query_option)
    if text_added != '':
        st.experimental_set_query_params(usuario=text_added)

def main():
    st.sidebar.selectbox('bla', ['none'], key='page_nav')
    if st.session_state.page_nav == 'none':
        def send_form_success():
            st.session_state.page_nav = "confirma_envio_form"
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(' ')
            with col2:
                st.success('Cancelamento realizado com sucesso!!!')                  
            with col3:
                    st.write(' ')

        unsub = {"email":[], "dh_cancelamento":[]}
        
        def cancelar():
            unsub["email"].append(query_option)
            unsub["dh_cancelamento"].append(datetime.now())
            df_cancel = pd.DataFrame.from_dict(unsub)

            filename = 'cancelamentos_dia/cancel_' + query_option + '.csv'
            status = save2s3(df_cancel, 'vagas-ds-storage', filename)
            if status == 200:
                send_form_success()
            else:
                st.error('Ocorreu algum problema no envio. Por favor, tente novamente.')     
        st.markdown('<center>Clique no botão abaixo para confirmar o cancelamento de sua inscrição em nosso feed de vagas.</center>', unsafe_allow_html=True)
        st.write("")
        col1, col2, col3 = st.columns([1.6,1,1])
        with col1:
            st.write("")
        with col2:
            st.button('Confirmar', on_click=cancelar)
        with col3:
            st.write("")

    if st.session_state.page_nav == "confirma_envio_form":
        st.write("")

if __name__ == "__main__":
    main()
