import sys
import re
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_DIR = os.path.join(REPO_ROOT, 'html_impressao')
PDF_DIR = os.path.join(REPO_ROOT, 'pdfs')

os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

SHARED_CSS = """
    @page {
      size: A4 portrait;
      margin: 8mm 8mm 9mm 8mm;
      @bottom-center {
        content: counter(page);
        font-family: 'Cinzel', 'Georgia', serif;
        font-size: 7.5pt;
        color: #666;
      }
    }

    *, *::before, *::after {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    :root {
      --primary-color: #2b4728;
      --secondary-color: #8c6d3b;
      --accent-color: #a73228;
      --dark-bg: #1c261b;
      --light-bg: #f9f8f5;
      --border-color: #d1c7b7;
      --text-color: #222220;
      --font-base: 8.5pt;
      --line-height-base: 1.28;
    }

    body {
      font-family: 'Crimson Pro', 'Georgia', serif;
      font-size: var(--font-base);
      line-height: var(--line-height-base);
      color: var(--text-color);
      background-color: #d5d1c8;
      margin: 0;
      padding: 0;
    }

    .toolbar {
      position: sticky;
      top: 0;
      z-index: 9999;
      background: #1e1e1e;
      color: #fff;
      padding: 10px 20px;
      display: flex;
      gap: 15px;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: 'Montserrat', sans-serif;
      font-size: 12px;
    }
    .toolbar button, .toolbar select {
      background: #2b4728;
      color: #fff;
      border: 1px solid #4a7545;
      padding: 6px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 600;
      font-size: 11px;
    }
    .toolbar button:hover { background: #3a5f36; }
    .toolbar .btn-print { background: #a73228; border-color: #c94035; }
    .toolbar .btn-print:hover { background: #bd3a2f; }

    @media print {
      .toolbar { display: none !important; }
      body { background-color: #fff; }
      .sheet {
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        width: 100% !important;
      }
    }

    .sheet {
      width: 210mm;
      min-height: 297mm;
      margin: 15mm auto;
      background: var(--light-bg);
      padding: 10mm 12mm;
      box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }

    .content-columns {
      column-count: 2;
      column-gap: 6mm;
      column-fill: auto;
      text-align: justify;
    }

    .one-column-mode .content-columns {
      column-count: 1 !important;
    }

    h1, h2, h3, h4, h5, h6 {
      font-family: 'Cinzel', 'Georgia', serif;
      font-weight: 700;
      line-height: 1.15;
      margin-top: 1.2em;
      margin-bottom: 0.4em;
      break-after: avoid;
    }

    .main-doc-header {
      column-span: all;
      text-align: center;
      padding: 12mm 0 8mm 0;
      margin-bottom: 6mm;
      border-bottom: 2px solid var(--secondary-color);
    }
    .main-title {
      font-size: 20pt;
      color: var(--primary-color);
      margin: 0;
      letter-spacing: 0.5px;
    }

    .part-header {
      column-span: all;
      background: var(--dark-bg);
      color: #f4eee1;
      padding: 5mm 8mm;
      margin: 8mm 0 4mm 0;
      border-left: 5px solid var(--accent-color);
      border-radius: 2px;
      page-break-before: auto;
    }
    .part-title {
      margin: 0;
      font-size: 13pt;
      color: #f4eee1;
      letter-spacing: 0.5px;
    }

    .section-title {
      font-size: 11pt;
      color: var(--primary-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1.5px;
      margin-top: 1.1em;
      break-after: avoid;
    }

    h2 { font-size: 10pt; color: var(--primary-color); }
    h3 { font-size: 9pt; color: #443e33; }
    h4 { font-size: 8.5pt; color: #555; }

    p { margin-top: 0; margin-bottom: 0.6em; text-indent: 1.2em; }
    p:first-of-type, .part-header + p, h1 + p, h2 + p, h3 + p { text-indent: 0; }

    blockquote {
      margin: 0.6em 0;
      padding: 4px 8px;
      background: #f0ebe1;
      border-left: 3px solid var(--secondary-color);
      font-style: italic;
      font-size: 0.95em;
    }
    blockquote p { text-indent: 0; margin-bottom: 0; }

    ul, ol {
      margin: 0.3em 0 0.6em 0;
      padding-left: 14px;
    }
    li { margin-bottom: 0.2em; }

    .table-wrapper, .table-wide-wrapper {
      margin: 0.6em 0;
      break-inside: avoid;
    }
    .table-wide-wrapper {
      column-span: all;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 7.8pt;
      line-height: 1.18;
      background: #fff;
      border: 1px solid var(--border-color);
    }
    th, td {
      padding: 3.5px 5px;
      border: 1px solid #ddd6c9;
      text-align: left;
    }
    th {
      background: #2b4728;
      color: #fff;
      font-family: 'Cinzel', serif;
      font-weight: 600;
      font-size: 7.8pt;
    }
    tr:nth-child(even) td { background: #f7f5f0; }

    hr {
      border: 0;
      height: 1px;
      background: var(--border-color);
      margin: 1em 0;
    }

    .page-break-before {
      break-before: page;
      page-break-before: always;
    }

    code {
      font-family: 'Consolas', monospace;
      font-size: 0.9em;
      background: #eee9df;
      padding: 1px 3px;
      border-radius: 2px;
    }
"""

def compile_markdown_to_body(md_text, script_dir):
    temp_clean = os.path.join(script_dir, 'temp_build_pdf.md')
    temp_body = os.path.join(script_dir, 'temp_build_pdf_body.html')
    with open(temp_clean, 'w', encoding='utf-8') as f:
        f.write(md_text)
    cmd = f'npx.cmd --yes marked -gfm -i "{temp_clean}" -o "{temp_body}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print("Erro ao processar markdown:", res.stderr)
        sys.exit(1)
    with open(temp_body, 'r', encoding='utf-8') as f:
        body = f.read()
    if os.path.exists(temp_clean): os.remove(temp_clean)
    if os.path.exists(temp_body): os.remove(temp_body)
    return body

def process_body(body):
    def mark_tables(match):
        t = match.group(0)
        first_row = re.search(r'<tr>(.*?)</tr>', t, re.DOTALL)
        if first_row:
            cols = len(re.findall(r'<t[hd]', first_row.group(1)))
            if cols >= 5:
                return f'<div class="table-wide-wrapper"><table class="table-wide" data-cols="{cols}">' + t[7:] + '</div>'
        return f'<div class="table-wrapper">{t}</div>'
    
    body = re.sub(r'<table>.*?</table>', mark_tables, body, flags=re.DOTALL)

    def format_h1(match):
        t = match.group(1).strip()
        if 'LIVRO' in t.upper() or 'OS TERRATENENTES' in t.upper() or 'FRAGMENTOS DO PINDORAMA' in t.upper():
            return f'<header class="main-doc-header"><h1 class="main-title">{t}</h1></header>'
        elif any(k in t.upper() for k in ['CAPÍTULO', 'APÊNDICE', 'FICHA', 'ATO', 'HERÓIS', 'INTRODUÇÃO', 'PARTE']):
            return f'<header class="part-header"><h1 class="part-title">{t}</h1></header>'
        else:
            return f'<h1 class="section-title">{t}</h1>'
            
    body = re.sub(r'<h1>(.*?)</h1>', format_h1, body)
    return body

def create_html(title, body):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="toolbar">
    <span><strong>{title}</strong></span>
    <button onclick="toggleColumns()" id="colBtn">Modo: 2 Colunas (Clique p/ 1)</button>
    <select onchange="setFontSize(this.value)">
      <option value="8pt">Densidade: Compacta (8pt)</option>
      <option value="8.5pt" selected>Densidade: Normal (8.5pt)</option>
      <option value="9pt">Densidade: Confortável (9pt)</option>
    </select>
    <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Salvar em PDF</button>
  </div>
  <div class="sheet" id="bookContainer">
    <div class="content-columns">
      {body}
    </div>
  </div>
  <script>
    function toggleColumns() {{
      const container = document.getElementById('bookContainer');
      const btn = document.getElementById('colBtn');
      container.classList.toggle('one-column-mode');
      btn.textContent = container.classList.contains('one-column-mode') ? 'Modo: 1 Coluna (Clique p/ 2)' : 'Modo: 2 Colunas (Clique p/ 1)';
    }}
    function setFontSize(val) {{
      document.documentElement.style.setProperty('--font-base', val);
    }}
  </script>
</body>
</html>"""

def get_browser():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def convert_html_to_pdf(browser, html_path, pdf_path):
    file_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={os.path.abspath(pdf_path)}",
        file_url
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return os.path.exists(pdf_path)

def main():
    browser = get_browser()
    if not browser:
        print("Erro: Nenhum executável do Edge ou Chrome encontrado para exportação de PDFs.")
        sys.exit(1)
    print(f"Utilizando motor de renderização: {browser}")

    pb = "\n\n<div class=\"page-break-before\"></div>\n\n---\n\n"

    # Definição dos Módulos a Compilar
    modules = [
        {
            "id": "00_trilogia",
            "title": "Os TerraTenentes: Trilogia Completa — Aldeias, Quilombos e Fortes",
            "html_name": "terratenentes_trilogia_impressao.html",
            "pdf_name": "00_Os_TerraTenentes_Trilogia_Completa.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'Livro_1_do_Jogador.md'),
                os.path.join(REPO_ROOT, 'Livro_2_do_Mestre.md'),
                os.path.join(REPO_ROOT, 'Livro_3_de_Monstros_e_Encontros.md'),
                os.path.join(REPO_ROOT, 'fichas', 'Ficha_do_TerraTenente.md'),
                os.path.join(REPO_ROOT, 'fichas', 'Ficha_de_Assentamento.md')
            ]
        },
        {
            "id": "01_livro1",
            "title": "Os TerraTenentes: Livro 1 do Jogador — Heróis & Fronteira",
            "html_name": "livro_1_jogador_impressao.html",
            "pdf_name": "01_Livro_1_do_Jogador.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'Livro_1_do_Jogador.md')
            ]
        },
        {
            "id": "02_livro2",
            "title": "Os TerraTenentes: Livro 2 do Mestre — Gestão, Bastiões & Cercos",
            "html_name": "livro_2_mestre_impressao.html",
            "pdf_name": "02_Livro_2_do_Mestre.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'Livro_2_do_Mestre.md')
            ]
        },
        {
            "id": "03_livro3",
            "title": "Os TerraTenentes: Livro 3 de Monstros & Encontros — Bestiário Folclórico",
            "html_name": "livro_3_monstros_impressao.html",
            "pdf_name": "03_Livro_3_de_Monstros_e_Encontros.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'Livro_3_de_Monstros_e_Encontros.md')
            ]
        },
        {
            "id": "04_starter",
            "title": "Os TerraTenentes: Starter Kit Oficial — O Cerco da Garganta do Boitatá",
            "html_name": "starter_kit_impressao.html",
            "pdf_name": "04_Starter_Kit_O_Cerco_da_Garganta_do_Boitata.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'Aventura_O_Cerco_da_Garganta_do_Boitata.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Ficha_Povoado_Mata_do_Remanso.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Tiao_Batedor_Guayana.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Dandara_Guerreira_do_Quilombo.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Nha_Benta_Rezadeira_Curandeira.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Bento_Vaqueiro_do_Sertao.md'),
                os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata', 'fichas_pre_geradas', 'Jaciara_Barqueira_Iariense.md')
            ]
        },
        {
            "id": "05_fichas",
            "title": "Os TerraTenentes: Fichas Oficiais em Branco (Herói & Assentamento)",
            "html_name": "fichas_oficiais_impressao.html",
            "pdf_name": "05_Fichas_Oficiais_em_Branco.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'fichas', 'Ficha_do_TerraTenente.md'),
                os.path.join(REPO_ROOT, 'fichas', 'Ficha_de_Assentamento.md')
            ]
        },
        {
            "id": "06_cenario",
            "title": "Fragmentos do Pindorama: Guia do Mundo & Catálogo das 6 Raças",
            "html_name": "cenario_pindorama_impressao.html",
            "pdf_name": "06_Fragmentos_do_Pindorama_Guia_de_Cenario.pdf",
            "sources": [
                os.path.join(REPO_ROOT, 'Cenário Principal', 'Fragmentos do Pindorama.md')
            ]
        }
    ]

    print(f"\nIniciando exportação de {len(modules)} publicações para HTML e PDF...")

    for mod in modules:
        print(f"\n--- Processando: {mod['title']} ---")
        contents = []
        for src in mod['sources']:
            if not os.path.exists(src):
                print(f"AVISO: Arquivo não encontrado: {src}")
                continue
            with open(src, 'r', encoding='utf-8') as f:
                contents.append(f.read())
        
        combined_md = pb.join(contents)
        raw_body = compile_markdown_to_body(combined_md, SCRIPT_DIR)
        final_body = process_body(raw_body)
        full_html = create_html(mod['title'], final_body)

        html_path = os.path.join(HTML_DIR, mod['html_name'])
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"  [HTML OK] -> {html_path}")

        pdf_path = os.path.join(PDF_DIR, mod['pdf_name'])
        ok = convert_html_to_pdf(browser, html_path, pdf_path)
        if ok:
            sz = os.path.getsize(pdf_path)
            if sz > 1024 * 1024:
                sz_str = f"{sz / (1024 * 1024):.2f} MB"
            else:
                sz_str = f"{sz / 1024:.1f} KB"
            print(f"  [PDF  OK] -> {pdf_path} ({sz_str})")
        else:
            print(f"  [PDF FALHOU] -> {pdf_path}")

    print("\n=======================================================")
    print(f"Todos os PDFs foram exportados com sucesso para: '{PDF_DIR}'")
    print("=======================================================")

if __name__ == '__main__':
    main()
