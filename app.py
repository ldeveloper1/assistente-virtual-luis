from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from pypdf import PdfReader
import streamlit as st


load_dotenv(override=True)


def enviar(texto):
    print(texto, flush=True)


def registrar_dados_usuario(
    email,
    nome="Nome não informado",
    observacoes="Não informado"
):
    enviar(
        f"Registrando {nome} com email {email} "
        f"e observações {observacoes}"
    )
    return {"registrado": "ok"}


def registrar_pergunta_desconhecida(pergunta):
    enviar(f"Registrando pergunta: {pergunta}")
    return {"registrado": "ok"}


ferramenta_dados_usuario = {
    "name": "registrar_dados_usuario",
    "description": (
        "Use esta ferramenta para registrar que um visitante "
        "está interessado em entrar em contato e forneceu "
        "um endereço de email."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "O endereço de email do visitante."
            },
            "nome": {
                "type": "string",
                "description": "O nome do visitante, se informado."
            },
            "observacoes": {
                "type": "string",
                "description": (
                    "Qualquer informação adicional relevante "
                    "sobre a conversa."
                )
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}


ferramenta_pergunta_desconhecida = {
    "name": "registrar_pergunta_desconhecida",
    "description": (
        "Use sempre esta ferramenta para registrar qualquer "
        "pergunta que não pôde ser respondida porque você "
        "não sabia a resposta."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "pergunta": {
                "type": "string",
                "description": (
                    "A pergunta que não pôde ser respondida."
                )
            }
        },
        "required": ["pergunta"],
        "additionalProperties": False
    }
}


ferramentas = [
    {
        "type": "function",
        "function": ferramenta_dados_usuario
    },
    {
        "type": "function",
        "function": ferramenta_pergunta_desconhecida
    }
]


class Me:

    def __init__(self):

        self.openai = OpenAI()
        self.nome = "Luis"

        diretorio_projeto = os.path.dirname(
            os.path.abspath(__file__)
        )

        caminho_pdf = os.path.join(
            diretorio_projeto,
            "dados",
            "curriculo_luis_carlos.pdf"
        )

        leitor = PdfReader(caminho_pdf)

        self.curriculo = ""

        for pagina in leitor.pages:

            try:

                texto = pagina.extract_text()

                if texto:
                    self.curriculo += texto

            except Exception as e:

                print(
                    f"Aviso: não foi possível extrair "
                    f"texto da página: {e}",
                    flush=True
                )

                continue

        caminho_resumo = os.path.join(
            diretorio_projeto,
            "dados",
            "resumo.txt"
        )

        with open(
            caminho_resumo,
            "r",
            encoding="utf-8"
        ) as arquivo:

            self.resumo = arquivo.read()


    def executar_chamada_ferramenta(self, chamadas):

        resultados = []

        for chamada in chamadas:

            nome_ferramenta = chamada.function.name

            argumentos = json.loads(
                chamada.function.arguments
            )

            print(
                f"Ferramenta chamada: {nome_ferramenta}",
                flush=True
            )

            ferramenta = globals().get(nome_ferramenta)

            resultado = (
                ferramenta(**argumentos)
                if ferramenta
                else {}
            )

            resultados.append(
                {
                    "role": "tool",
                    "content": json.dumps(resultado),
                    "tool_call_id": chamada.id
                }
            )

        return resultados


    def system_prompt(self):

        system_prompt = f"""
            Você está representando {self.nome}.

            Você responde perguntas no site de {self.nome}, especificamente
            perguntas relacionadas à carreira, trajetória profissional,
            habilidades, experiências e projetos de {self.nome}.

            Responda às perguntas usando apenas informações explicitamente
            fornecidas no Resumo e no Currículo.

            Se uma pergunta não estiver relacionada ao contexto profissional
            de {self.nome}, não a responda.

            Se uma pergunta pedir para você aplicar as habilidades de {self.nome}
            a um novo negócio, problema ou situação que não esteja explicitamente
            descrita no Resumo ou no Currículo, não resolva o problema.

            Se você não souber a resposta, use a ferramenta
            registrar_pergunta_desconhecida.

            Não invente informações nem deduza experiências que não estejam
            explicitamente fornecidas.

            Seja profissional e envolvente, como se estivesse conversando
            com alguém interessado no contexto profissional de {self.nome}.

            Para perguntas sobre como você lidaria com uma situação ou cenário
            específico, sugira discutir o assunto por email e peça o endereço
            de email do usuário.

            Se o usuário demonstrar explicitamente interesse em entrar em contato,
            peça seu endereço de email e registre-o usando a ferramenta
            registrar_dados_usuario.
"""

        system_prompt += f"""

## Resumo:

{self.resumo}

## Currículo:

{self.curriculo}
"""

        system_prompt += f"""

Com base nesse contexto, converse com o usuário, mantendo sempre
o papel de {self.nome}.
"""

        return system_prompt


    def chat(self, mensagem, historico):

        mensagens = [
            {
                "role": "system",
                "content": self.system_prompt()
            }
        ] + historico + [
            {
                "role": "user",
                "content": mensagem
            }
        ]

        concluido = False

        while not concluido:

            resposta = self.openai.chat.completions.create(
                model="gpt-5-nano",
                messages=mensagens,
                tools=ferramentas
            )

            if resposta.choices[0].finish_reason == "tool_calls":

                mensagem_assistente = resposta.choices[0].message

                chamadas = mensagem_assistente.tool_calls

                resultados = self.executar_chamada_ferramenta(
                    chamadas
                )

                mensagens.append(
                    mensagem_assistente
                )

                mensagens.extend(
                    resultados
                )

            else:

                concluido = True

        return resposta.choices[0].message.content


if __name__ == "__main__":

    me = Me()

    st.title("Assistente Virtual - Luis")

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