from openai import OpenAI
from pypdf import PdfReader
import json
import os
from dotenv import load_dotenv
from assistente.ferramentas import (
                                    ferramentas,
                                    registrar_dados_usuario,
                                    registrar_pergunta_desconhecida
                                )
from assistente.prompt import criar_system_prompt

load_dotenv(override=True)

class Me:

    def __init__(self):

        self.openai = OpenAI()
        self.nome = "Luis"

        diretorio_projeto = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
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

            ferramentas_disponiveis = {
                    "registrar_dados_usuario": registrar_dados_usuario,
                    "registrar_pergunta_desconhecida": registrar_pergunta_desconhecida
                }

            ferramenta = ferramentas_disponiveis.get(nome_ferramenta)

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

        return criar_system_prompt(
            self.nome,
            self.resumo,
            self.curriculo
        )


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