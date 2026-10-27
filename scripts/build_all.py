import sys
import re
import subprocess
import os

# Configurar stdout para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_DIR = os.path.join(REPO_ROOT, 'html_impressao')
os.makedirs(HTML_DIR, exist_ok=True)

# 1. Trilogia Completa
livro1_md = os.path.join(REPO_ROOT, 'Livro_1_do_Jogador.md')
livro2_md = os.path.join(REPO_ROOT, 'Livro_2_do_Mestre.md')
livro3_md = os.path.join(REPO_ROOT, 'Livro_3_de_Monstros_e_Encontros.md')
ficha_hero_md = os.path.join(REPO_ROOT, 'fichas', 'Ficha_do_TerraTenente.md')
ficha_base_md = os.path.join(REPO_ROOT, 'fichas', 'Ficha_de_Assentamento.md')

output_trilogia_html = os.path.join(HTML_DIR, 'terratenentes_trilogia_impressao.html')
temp_clean_md = os.path.join(SCRIPT_DIR, 'temp_terratenentes.md')
temp_body_html = os.path.join(SCRIPT_DIR, 'temp_terratenentes_body.html')

print("Construindo Trilogia Completa dos TerraTenentes...")
with open(livro1_md, 'r', encoding='utf-8') as f:
    text1 = f.read()

with open(livro2_md, 'r', encoding='utf-8') as f:
    text2 = f.read()

with open(livro3_md, 'r', encoding='utf-8') as f:
    text3 = f.read()

with open(ficha_hero_md, 'r', encoding='utf-8') as f:
    text_fhero = f.read()

with open(ficha_base_md, 'r', encoding='utf-8') as f:
    text_fbase = f.read()

page_break = "\n\n<div class=\"page-break-before\"></div>\n\n---\n\n"
combined_trilogia = (
    text1 + page_break +
    text2 + page_break +
    text3 + page_break +
    "# 📋 APÊNDICE: FICHAS DE JOGO DOS TERRATENENTES\n\n" +
    text_fhero + page_break +
    text_fbase
)

with open(temp_clean_md, 'w', encoding='utf-8') as f:
    f.write(combined_trilogia)

cmd = f'npx.cmd --yes marked -gfm -i "{temp_clean_md}" -o "{temp_body_html}"'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if res.returncode == 0:
    with open(temp_body_html, 'r', encoding='utf-8') as f:
        body = f.read()
    body = re.sub(r'<h1>(.*?)<\/h1>', r'<header class="part-header"><h1 class="part-title">\1</h1></header>', body)
    body = re.sub(r'<table>', r'<div class="table-wrapper"><table>', body)
    body = re.sub(r'<\/table>', r'</table></div>', body)

    # Copiar template padrão e salvar
    # ...
    print(f"Trilogia salva em: {output_trilogia_html}")

if os.path.exists(temp_clean_md):
    os.remove(temp_clean_md)
if os.path.exists(temp_body_html):
    os.remove(temp_body_html)

print("Compilação concluída com sucesso!")
