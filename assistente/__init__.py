def __init__(self):

    self.openai = OpenAI()
    self.nome = "Luis"

    diretorio_projeto = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    self.curriculo = os.getenv("CURRICULO")

    if not self.curriculo:

        caminho_curriculo = os.path.join(
            diretorio_projeto,
            "dados",
            "curriculo.txt"
        )

        with open(
            caminho_curriculo,
            "r",
            encoding="utf-8"
        ) as arquivo:

            self.curriculo = arquivo.read()

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