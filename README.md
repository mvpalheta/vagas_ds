## Overview
Este repositório tem como finalidade compartilhar os códigos utilizados na construção [deste app](http://www.vagasds.com/). A aplicação realiza diariamente, às 00:00h, o scraping de vagas de cientista de dados/data scientist no site da [Gupy](https://www.gupy.io/), faz o tratamento dos mesmos, algumas transformações e disponibiliza estas vagas a fim de auxiliar na divulgação. Além disso, a aplicação conta com um sistema de recomendação de vagas similares além de possibilitar às pessoas interessadas receberem notificações de vagas em seus e-mails, de acordo com algumas preferências selecionadas.

Todo o projeto foi desenvolvido em Python, sendo que o frontend utiliza a biblioteca Streamilit. Para acessar a documentação, diversos exemplos, tutoriais e a comunidade da biblioteca basta [clicar aqui](https://streamlit.io/). Ainda, todo o projeto atualmente está rodando em uma instância EC2 da AWS sendo que as bases de dados estão disponíveis em um bucket S3 também da AWS. Por motivos de segurança, apenas as bases de dados que não contém e-mails são gravadas como públicas.

## A Gupy
A Gupy é uma startup de RH fundada em 2015 que presta, entre outros, serviços de recrutamento e seleção e vem crescendo bastante nos últimos anos. Atualmente grande empresas como Santander, Americanas, Ambev, Vivo, dentre outras utilizam sua plataforma para anunciar vagas. Sendo assim, esta plataforma se apresenta como ótimo espaço para quem busca uma vaga seja para recolocação, transição de carreira e/ou empresa ou mesmo acompanhar o mercado de trabalho desta área.

## Organização do repositório
Para uma melhor organização, o repositório está dividido em 4 pastas descritas abaixo:

**backend_codes:** Esta pasta contém todos os códigos que rodam no backend e atualmente estão em uma instância EC2 da AWS. A seguir, uma breve descrição do que cada código faz:
			
- **Scrap_vagas_publico.py:** realiza o scraping de vagas no site da gupy, tratamento dos dados e salva a base de dados em um bucket do S3;
- **recommender_system_publico.py:** calcula a matriz de similaridades entre as vagas extraídas do site da Gupy e salva esta matriz em um bucket do S3;
- **mapa_vagas_gupy_publico.py:** produz o mapa utilizado no app e salva como um pickle em um bucket do S3. A ideia é otimizar o carregamento do app sem perder a funcionalidade de hover do mapa;
- **wordcloud_gupy_publico.py:** produz as wordclouds utilizadas no app e salva as imagens em um bucket do S3. A ideia é otimizar o carregamento do app;
- **lista_feed_publico.py:** verifica as incrições, cancelamentos do dia, produz a lista de envio de e-mails e salva em um bucket do S3;
- **envio_email_vagasds_publico.py:** checa a lista de envio de e-mails e envia conforme as preferências de cada usuário cadastrado.

**main_page_app:** Esta pasta guarda todos os códigos necessários para gerar o [app principal](link para o app) do projeto juntamente com todas as suas funcionalidades.

**skills_responsibilities_page_app:** Contém os códigos que geram a aplicação com as qualificações e responsabilidades de cada vaga selecionada na lista de vagas do app principal.

**unsubscribe_page_app:** Guarda os códigos necessários ao app de cancelamento das notificações por e-mail.

Ainda existem diversos melhorias a serem implementadas futuramente, mas esta já é uma versão funcional. Espero que tanto a aplicação quanto os códigos disponibilizados aqui sejam úteis para alguém. Estou à disposição para esclarecer dúvidas, receber críticas construtivas e/ou sugestões. **Abraços.**
