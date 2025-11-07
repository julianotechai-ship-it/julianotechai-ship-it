import os
from datetime import datetime

def salvar_log(texto):
    pasta_logs = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(pasta_logs, exist_ok=True)

    nome = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    caminho = os.path.join(pasta_logs, nome)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"✅ Log salvo em: {caminho}")


def gerar_post_simples():
    print("✅ Gerando post simples:")
    texto_post = "Texto curto e inspirador sobre recomeço e transformação pessoal."

    pasta_posts = os.path.join(os.path.dirname(__file__), "posts", "simples")
    os.makedirs(pasta_posts, exist_ok=True)

    nome_arquivo = f"post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    caminho = os.path.join(pasta_posts, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto_post)

    print(f"✅ Post salvo em: {caminho}")
    return texto_post


def main():
    print("✅ RecomeçoIA iniciado!")
    texto = gerar_post_simples()
    salvar_log("Gerando post simples:\n" + texto)


if __name__ == "__main__":
    main()
