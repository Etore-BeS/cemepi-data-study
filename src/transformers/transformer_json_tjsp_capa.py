import pandas as pd
import json
import re
from datetime import datetime

class FaceTransformerSilverTJSP:
    def __init__(self, input_csv, output_silver):
        self.input_csv = input_csv
        self.output_silver = output_silver

    def _limpar_string(self, valor):
        if pd.isna(valor) or str(valor).strip() == "NÃO HÁ REGISTRO":
            return "NÃO HÁ REGISTRO"
        return str(valor).strip()

    def transformar_csv_para_silver(self):
        df = pd.read_csv(self.input_csv)
        qtd = 0
        
        # Padrão JSON Lines: Escreve direto no arquivo
        with open(self.output_silver, 'w', encoding='utf-8') as f_out:
            for _, row in df.iterrows():
                processo_raw = self._limpar_string(row.get("Processo"))
                if processo_raw == "NÃO HÁ REGISTRO" or not processo_raw:
                    continue 
                    
                num_processo_limpo = re.sub(r'\D', '', processo_raw)
                
                valor_acao = self._limpar_string(row.get("Valor Da Ação"))
                valor_float = None
                if valor_acao != "NÃO HÁ REGISTRO":
                    try:
                        v = re.sub(r'[^\d,.-]', '', valor_acao).replace('.', '').replace(',', '.')
                        valor_float = float(v)
                    except ValueError: pass

                def formatar_data(data_str):
                    if not data_str or data_str == "NÃO HÁ REGISTRO": return None
                    match = re.search(r'(\d{2}/\d{2}/\d{4})', str(data_str))
                    if match:
                        try:
                            dt = datetime.strptime(match.group(1), "%d/%m/%Y")
                            return {"$date": dt.strftime("%Y-%m-%dT00:00:00.000Z")}
                        except ValueError: pass
                    return None

                silver_doc = {
                    "processo_pk": processo_raw, 
                    "processo": {
                        "numero": num_processo_limpo,
                        "classe": {"descricao": self._limpar_string(row.get("Classe"))},
                        "assunto": {"descricao": self._limpar_string(row.get("Assunto Principal"))},
                        "valorAcao": valor_float
                    },
                    "tribunal": {"sigla": "TJSP", "nome": "Tribunal de Justiça de São Paulo", "segmento": "JUSTICA_ESTADUAL", "jtr": 826},
                    "grau": {"sigla": "G1", "nome": "1° Grau", "numero": 1},
                    "orgaoJulgador": {"nome": self._limpar_string(row.get("Vara"))},
                    "datas": {},
                    "partes": [],
                    "movimentos": []
                }

                dt_dist = formatar_data(row.get("Status/Data Dist."))
                if dt_dist: silver_doc["datas"]["ultimaDistribuicao"] = dt_dist

                autores_nomes = self._limpar_string(row.get("Autores"))
                autores_advs = self._limpar_string(row.get("Advogados Autores"))
                reus_nomes = self._limpar_string(row.get("Réus"))
                reus_advs = self._limpar_string(row.get("Advogados Réus"))

                def extrair_partes(nomes_str, advs_str, polo, tipo):
                    if nomes_str == "NÃO HÁ REGISTRO": return
                    nomes = [n.strip() for n in str(nomes_str).split(",") if n.strip()]
                    advs = [a.strip() for a in str(advs_str).split(",") if a.strip()] if advs_str != "NÃO HÁ REGISTRO" else []
                    for nome in nomes:
                        parte = {
                            "polo": polo, "tipoParte": tipo.upper(), "pessoa": {"nome": nome},
                            "representantes": [{"tipo": "ADVOGADO", "nome": adv} for adv in advs]
                        }
                        silver_doc["partes"].append(parte)

                extrair_partes(autores_nomes, autores_advs, "ATIVO", "Requerente/Autor")
                extrair_partes(reus_nomes, reus_advs, "PASSIVO", "Requerido/Réu")

                movs_str = self._limpar_string(row.get("Movimentações"))
                if movs_str != "NÃO HÁ REGISTRO":
                    for bloco in str(movs_str).split(" | "):
                        if ": " in bloco:
                            data_str, mov_desc = bloco.split(": ", 1)
                            mov_mongo = {"descricao": mov_desc.strip()}
                            dt_iso = formatar_data(data_str.strip())
                            if dt_iso: mov_mongo["dataHora"] = dt_iso
                            silver_doc["movimentos"].append(mov_mongo)

                if silver_doc["movimentos"]:
                    silver_doc["datas"]["ultimoMovimento"] = silver_doc["movimentos"][0]

                # Escreve direto no disco linha por linha
                f_out.write(json.dumps(silver_doc, ensure_ascii=False) + '\n')
                qtd += 1

        return qtd
    