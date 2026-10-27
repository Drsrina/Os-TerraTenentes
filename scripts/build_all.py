import sys
import re
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_DIR = os.path.join(REPO_ROOT, 'html_impressao')
os.makedirs(HTML_DIR, exist_ok=True)

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
    temp_clean = os.path.join(script_dir, 'temp_build.md')
    temp_body = os.path.join(script_dir, 'temp_build_body.html')
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
        if 'LIVRO' in t.upper() or 'OS TERRATENENTES' in t.upper():
            return f'<header class="main-doc-header"><h1 class="main-title">{t}</h1></header>'
        elif any(k in t.upper() for k in ['CAPÍTULO', 'APÊNDICE', 'FICHA', 'ATO', 'HERÓIS', 'INTRODUÇÃO']):
            return f'<header class="part-header"><h1 class="part-title">{t}</h1></header>'
        else:
            return f'<h1 class="section-title">{t}</h1>'
            
    body = re.sub(r'<h1>(.*?)</h1>', format_h1, body)
    return body

def build_trilogia():
    print("=== Compilando Trilogia Completa dos TerraTenentes ===")
    l1 = os.path.join(REPO_ROOT, 'Livro_1_do_Jogador.md')
    l2 = os.path.join(REPO_ROOT, 'Livro_2_do_Mestre.md')
    l3 = os.path.join(REPO_ROOT, 'Livro_3_de_Monstros_e_Encontros.md')
    fh = os.path.join(REPO_ROOT, 'fichas', 'Ficha_do_TerraTenente.md')
    fb = os.path.join(REPO_ROOT, 'fichas', 'Ficha_de_Assentamento.md')

    with open(l1, 'r', encoding='utf-8') as f: t1 = f.read()
    with open(l2, 'r', encoding='utf-8') as f: t2 = f.read()
    with open(l3, 'r', encoding='utf-8') as f: t3 = f.read()
    with open(fh, 'r', encoding='utf-8') as f: th = f.read()
    with open(fb, 'r', encoding='utf-8') as f: tb = f.read()

    pb = "\n\n<div class=\"page-break-before\"></div>\n\n---\n\n"
    combined = (
        t1 + pb +
        t2 + pb +
        t3 + pb +
        "# 📋 APÊNDICE: FICHAS DE JOGO DOS TERRATENENTES\n\n" +
        th + pb +
        tb
    )

    body = compile_markdown_to_body(combined, SCRIPT_DIR)
    body = process_body(body)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Os TerraTenentes: Trilogia Completa — Aldeias, Quilombos e Fortes</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="toolbar">
    <span><strong>Os TerraTenentes</strong> (Trilogia Completa)</span>
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
    out = os.path.join(HTML_DIR, 'terratenentes_trilogia_impressao.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"-> Salvo: {out}")

def build_starter_kit():
    print("=== Compilando Starter Kit: O Cerco da Garganta do Boitatá ===")
    adv_dir = os.path.join(REPO_ROOT, 'aventuras', 'o_cerco_da_garganta_do_boitata')
    adv_md = os.path.join(adv_dir, 'Aventura_O_Cerco_da_Garganta_do_Boitata.md')
    f_remanso = os.path.join(adv_dir, 'fichas_pre_geradas', 'Ficha_Povoado_Mata_do_Remanso.md')
    f_tiao = os.path.join(adv_dir, 'fichas_pre_geradas', 'Tiao_Batedor_Guayana.md')
    f_dandara = os.path.join(adv_dir, 'fichas_pre_geradas', 'Dandara_Guerreira_do_Quilombo.md')
    f_benta = os.path.join(adv_dir, 'fichas_pre_geradas', 'Nha_Benta_Rezadeira_Curandeira.md')
    f_bento = os.path.join(adv_dir, 'fichas_pre_geradas', 'Bento_Vaqueiro_do_Sertao.md')

    with open(adv_md, 'r', encoding='utf-8') as f: t_adv = f.read()
    with open(f_remanso, 'r', encoding='utf-8') as f: t_rem = f.read()
    with open(f_tiao, 'r', encoding='utf-8') as f: t_tia = f.read()
    with open(f_dandara, 'r', encoding='utf-8') as f: t_dan = f.read()
    with open(f_benta, 'r', encoding='utf-8') as f: t_ben = f.read()
    with open(f_bento, 'r', encoding='utf-8') as f: t_bto = f.read()

    pb = "\n\n<div class=\"page-break-before\"></div>\n\n---\n\n"
    combined = (
        t_adv + pb +
        "# 📋 APÊNDICE: FICHA DE DOMÍNIO DE MATA DO REMANSO\n\n" +
        t_rem + pb +
        "# 👤 APÊNDICE: OS 4 HERÓIS PRÉ-GERADOS\n\n" +
        t_tia + pb +
        t_dan + pb +
        t_ben + pb +
        t_bto
    )

    body = compile_markdown_to_body(combined, SCRIPT_DIR)
    body = process_body(body)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Os TerraTenentes: Starter Kit Oficial — O Cerco da Garganta do Boitatá</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="toolbar">
    <span><strong>Starter Kit Oficial</strong>: O Cerco da Garganta do Boitatá</span>
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
    out = os.path.join(HTML_DIR, 'starter_kit_impressao.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"-> Salvo: {out}")

if __name__ == '__main__':
    build_trilogia()
    build_starter_kit()
    print("Todas as compilações foram finalizadas com sucesso!")
