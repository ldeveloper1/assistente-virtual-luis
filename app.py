import streamlit as st
from assistente.agente import Me

me = Me()


st.markdown(
    "<h1 style='color: #0B3C5D;'>Assistente Virtual</h1>", 
    unsafe_allow_html=True
)


st.write(
    "Olá! Meu nome é Luis.\n\n "
    "Este é o meu assistente virtual baseado em IA, programado para responder "
    "a dúvidas sobre a minha **trajetória profissional, projetos e habilidades**. "
    "Fique à vontade para perguntar qualquer coisa sobre minha carreira!"
)

st.write(
    "Se você é desenvolvedor ou tem curiosidade em tecnologia, pode "
    "analisar a arquitetura e o código-fonte deste agente diretamente no "
    "[GitHub](https://github.com/ldeveloper1/assistente-virtual-luis/blob/main/app.py)."
)

if "mensagens" not in st.session_state:

    st.session_state.mensagens = []


for mensagem in st.session_state.mensagens:

    with st.chat_message(mensagem["role"]):

        st.write(mensagem["content"])


mensagem_usuario = st.chat_input(
    "Faça uma pergunta sobre minha carreira..."
)


if mensagem_usuario:

    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": mensagem_usuario
        }
    )

    with st.chat_message("user"):

        st.write(mensagem_usuario)


    historico = [
        {
            "role": mensagem["role"],
            "content": mensagem["content"]
        }

        for mensagem in st.session_state.mensagens[:-1]
    ]


    resposta = me.chat(
        mensagem_usuario,
        historico
    )


    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "content": resposta
        }
    )


    with st.chat_message("assistant"):

        st.write(resposta)