import pandas as pd
import json
import re
from datetime import datetime

class TransformerSilverNossosDados:
    def __init__(self, input_csv, output_json_bruto, output_silver):
        self.input_csv = input_csv
        self.output_json_bruto = output_json_bruto
        self.output_silver = output_silver

    def _limpar_string(self, valor):
        if pd.isna(valor) or valor == "NÃO HÁ REGISTRO":
            return "NÃO HÁ REGISTRO"
        return str(valor).strip()

    def csv_para_json_bruto(self):
        """Converte o CSV achatado para um JSON hierárquico primário."""
        df = pd.read_csv(self.input_csv)
        dados = []
        
        for _, row in df.iterrows():
            autores_nomes = self._limpar_string(row.get("Autores"))
            autores_advs = self._limpar_string(row.get("Advogados Autores"))
            reus_nomes = self._limpar_string(row.get("Réus"))
            reus_advs = self._limpar_string(row.get("Advogados Réus"))
            
            def extrair_partes(nomes_str, advs_str, tipo):
                if nomes_str == "NÃO HÁ REGISTRO": return []
                nomes = [n.strip() for n in nomes_str.split(",") if n.strip()]
                advs = [a.strip() for a in advs_str.split(",") if a.strip()] if advs_str != "NÃO HÁ REGISTRO" else []
                return [{"Tipo": tipo, "Nome": nome, "Advogados": advs} for nome in nomes]

            movs_str = self._limpar_string(row.get("Movimentações"))
            movimentacoes = []
            if movs_str != "NÃO HÁ REGISTRO":
                for bloco in movs_str.split(" | "):
                    if ": " in bloco:
                        data, mov = bloco.split(": ", 1)
                        movimentacoes.append({"Data": data.strip(), "Movimento": mov.strip()})

            processo_json = {
                "Processo": self._limpar_string(row.get("Processo")),
                "Classe": self._limpar_string(row.get("Classe")),
                "Assunto Principal": self._limpar_string(row.get("Assunto Principal")),
                "Data Distribuição / Status": self._limpar_string(row.get("Status/Data Dist.")),
                "Foro": self._limpar_string(row.get("Foro")),
                "Vara": self._limpar_string(row.get("Vara")),
                "Partes do Processo - Autores": extrair_partes(autores_nomes, autores_advs, "Requerente/Autor"),
                "Partes do Processo - Réus": extrair_partes(reus_nomes, reus_advs, "Requerido/Réu"),
                "Valor da ação": self._limpar_string(row.get("Valor Da Ação")),
                "Movimentações": movimentacoes
            }
            dados.append(processo_json)

        with open(self.output_json_bruto, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return len(dados)

    def json_bruto_para_silver(self):
        """Converte o JSON bruto para a infraestrutura Silver (Formato do Professor)."""
        with open(self.output_json_bruto, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        silver_docs = []
        for doc in dados:
            num_processo_limpo = re.sub(r'\D', '', doc.get("Processo", ""))
            
            valor_acao = doc.get("Valor da ação")
            valor_float = None
            if valor_acao and valor_acao != "NÃO HÁ REGISTRO":
                try:
                    v = re.sub(r'[^\d,.-]', '', str(valor_acao)).replace('.', '').replace(',', '.')
                    valor_float = float(v)
                except: pass

            def formatar_data(data_str):
                if not data_str or data_str == "NÃO HÁ REGISTRO": return None
                match = re.search(r'(\d{2}/\d{2}/\d{4})', data_str)
                if match:
                    try:
                        dt = datetime.strptime(match.group(1), "%d/%m/%Y")
                        return {"$date": dt.strftime("%Y-%m-%dT00:00:00.000Z")}
                    except: pass
                return None

            silver_doc = {
                "processo_pk": doc.get("Processo"), 
                "processo": {
                    "numero": num_processo_limpo,
                    "classe": {"descricao": doc.get("Classe")},
                    "assunto": {"descricao": doc.get("Assunto Principal")},
                    "valorAcao": valor_float
                },
                "tribunal": {"sigla": "TJSP", "nome": "Tribunal de Justiça de São Paulo", "segmento": "JUSTICA_ESTADUAL", "jtr": 826},
                "grau": {"sigla": "G1", "nome": "1° Grau", "numero": 1},
                "orgaoJulgador": {"nome": doc.get("Vara")},
                "datas": {},
                "partes": [],
                "movimentos": []
            }

            dt_dist = formatar_data(doc.get("Data Distribuição / Status"))
            if dt_dist: silver_doc["datas"]["ultimaDistribuicao"] = dt_dist

            for polo, key in [("ATIVO", "Partes do Processo - Autores"), ("PASSIVO", "Partes do Processo - Réus")]:
                for p in doc.get(key, []):
                    parte = {
                        "polo": polo, "tipoParte": p.get("Tipo", "").upper(),
                        "pessoa": {"nome": p.get("Nome", "")},
                        "representantes": [{"tipo": "ADVOGADO", "nome": adv} for adv in p.get("Advogados", [])]
                    }
                    silver_doc["partes"].append(parte)

            for m in doc.get("Movimentações", []):
                mov_mongo = {"descricao": m.get("Movimento")}
                dt_iso = formatar_data(m.get("Data"))
                if dt_iso: mov_mongo["dataHora"] = dt_iso
                silver_doc["movimentos"].append(mov_mongo)

            if silver_doc["movimentos"]:
                silver_doc["datas"]["ultimoMovimento"] = silver_doc["movimentos"][0]

            silver_docs.append(silver_doc)

        with open(self.output_silver, 'w', encoding='utf-8') as f:
            json.dump(silver_docs, f, ensure_ascii=False, indent=4)
        return len(silver_docs)
    