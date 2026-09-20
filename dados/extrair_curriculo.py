from pathlib import Path
from pypdf import PdfReader


diretorio = Path(__file__).parent

caminho_pdf = diretorio / "curriculo_luis_carlos.pdf"
caminho_txt = diretorio / "curriculo.txt"


leitor = PdfReader(caminho_pdf)

texto = ""

for pagina in leitor.pages:

    conteudo = pagina.extract_text()

    if conteudo:
        texto += conteudo + "\n"


caminho_txt.write_text(
    texto,
    encoding="utf-8"
)


print("Currículo extraído com sucesso.")