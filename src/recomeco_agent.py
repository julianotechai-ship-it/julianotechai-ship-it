import json
import datetime
import os

def carregar_templates():
    caminho = "prompt_templates.json"
    if not os.path.exists(caminho):
        print("⚠️  Arquivo prompt_templates.json não encontrado.")
        return {}

    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def gerar_conteudo():
    templates = carregar_templates()

    texto = ""
    if "post_simples" in templates:
        texto = f"✅ Gerando post simples:\n{templates['post_simples']}"
    else:
        texto = "⚠️ Nenhum template encontrado!"

    print(texto)
    salvar_log(texto)

def salvar_log(msg):
    # garante que a pasta logs existe
    pasta_logs = "logs"
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)

    agora = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    caminho = os.path.join(pasta_logs, f"log_{agora}.txt")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(msg)

    print(f"✅ Log salvo em {caminho}")

if __name__ == '__main__':
    print("✅ RecomeçoIA iniciado!")
    gerar_conteudo()
