import json
import os
import time
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.scrapers.scraper_tjsp_capa_request import FaceTJSPScraper

INPUT_FILE = "data/PGE.GPDR.json"
OUTPUT_FILE = "data/coleta_tjsp_resultados.csv"

def carregar_ja_coletados():
    if not os.path.exists(OUTPUT_FILE):
        return set()
    try:
        df_existente = pd.read_csv(OUTPUT_FILE, usecols=["Processo"])
        return set(df_existente["Processo"].astype(str).tolist())
    except ValueError:
        print("[AVISO] Arquivo CSV com formato antigo detectado. Sugerimos apagá-lo.")
        return set()

def executar_coleta():
    scraper = FaceTJSPScraper()
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        dados_base = json.load(f)
    
    ja_feitos = carregar_ja_coletados()
    
    a_processar = [p for p in dados_base if p.get('Processo') and p['Processo'] not in ja_feitos]

    print(f"Total na base: {len(dados_base)} | Já coletados: {len(ja_feitos)} | Restantes: {len(a_processar)}")

    for item in a_processar:
        num = item['Processo']
        
        url = f"https://esaj.tjsp.jus.br/cpopg/search.do?cbPesquisa=NUMPROC&dadosConsulta.valorConsulta={num}"
        
        try:
            html = scraper.get_html(url)
            
            link_exato = scraper.resolve_multiple_results(html, num)
            if link_exato:
                url = link_exato  
                html = scraper.get_html(url)  
            
            resultado = scraper.parse_process(html)
            
            if resultado:
                numero_extraido = resultado.get("numero")
                
                # Formatação das listas
                movs = resultado.get("movimentações", [])
                if isinstance(movs, list) and len(movs) > 0:
                    movs_formatadas = " | ".join([f"{m['data']}: {m['tipo']}" for m in movs])
                else:
                    movs_formatadas = "NÃO HÁ REGISTRO"

                tipo_sent = resultado.get("tipo_sentença")
                data_sent = resultado.get("data_sentença")
                tipo_sent_formatado = ", ".join(tipo_sent) if tipo_sent and tipo_sent[0] is not None else "NÃO HÁ REGISTRO"
                data_sent_formatada = ", ".join(data_sent) if data_sent and data_sent[0] is not None else "NÃO HÁ REGISTRO"

                linha_dict = {
                    "Processo": num if numero_extraido == "NÃO HÁ REGISTRO" else numero_extraido,
                    "Classe": resultado.get("classe"),
                    "Assunto Principal": resultado.get("assunto"),
                    "Status/Data Dist.": resultado.get("distribuicao"),
                    "Foro": resultado.get("foro"),
                    "Vara": resultado.get("vara"),
                    "Autores": resultado.get("autores"),
                    "Advogados Autores": resultado.get("advogados_autores"),
                    "Réus": resultado.get("reus"),
                    "Advogados Réus": resultado.get("advogados_reus"),
                    "Valor Da Ação": resultado.get("valor"),
                    "Outros Assuntos": resultado.get("outros_assuntos"),
                    "Tipo de Sentença": tipo_sent_formatado, 
                    "Data Sentença": data_sent_formatada,
                    "Movimentações": movs_formatadas,
                    "URL_Consulta": url
                }
                
                df_linha = pd.DataFrame([linha_dict])
                df_linha.to_csv(OUTPUT_FILE, mode='a', index=False, header=not os.path.exists(OUTPUT_FILE))
                print(f"[OK] Processo coletado: {num}")
            else:
                print(f"[FALHA] HTML vazio ou erro de parsing: {num}")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"[ERRO] Processo {num}: {e}")
            continue

if __name__ == "__main__":
    executar_coleta()
