import json

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
