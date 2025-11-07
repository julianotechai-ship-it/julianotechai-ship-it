import json
import datetime
import os

def carregar_templates():
    try:
        with open('prompt_templates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def salvar_log(msg):
    agora = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    # Caminho absoluto para garantir que funcione no Windows
    caminho = f"C:/Users/Notebook/RecomeçoIA/src/logs/log_{agora}.txt"

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(msg)

def gerar_conteudo():
    templates = carregar_templates()
    texto = "Gerando conteúdo de teste do Recomeço..."
    print(texto)
    salvar_log(texto)

if __name__ == '__main__':
    print("✅ RecomeçoIA iniciado!")
    gerar_conteudo()
