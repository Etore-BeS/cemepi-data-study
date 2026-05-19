import json
import re

class TransformerSilverDadosIC:
    def __init__(self, input_ic_json, output_silver_ic):
        self.input_ic_json = input_ic_json
        self.output_silver_ic = output_silver_ic

    def json_pge_para_silver(self):
        # Lê os dados originais do IC e estrutura para a camada Silver.
        with open(self.input_ic_json, 'r', encoding='utf-8') as f:
            dados_ic = json.load(f)

        silver_ic_docs = []
        for doc in dados_ic:
            proc_bruto = str(doc.get("Processo", ""))
            proc_limpo = re.sub(r'\D', '', proc_bruto)
            
            processo_mascarado = proc_bruto
            if len(proc_limpo) == 20:
                processo_mascarado = f"{proc_limpo[:7]}-{proc_limpo[7:9]}.{proc_limpo[9:13]}.{proc_limpo[13]}.{proc_limpo[14:16]}.{proc_limpo[16:]}"
                
            silver_doc = {
                "processo_pk": processo_mascarado, 
                "_id": doc.get("_id"),
                "metadados": {
                    "pasta": doc.get("Pasta"),
                    "situacao": doc.get("Situação"),
                    "materia": doc.get("Matéria"),
                    "assuntos_ic": doc.get("Assuntos"),
                    "polo_pge": doc.get("Polo PGE"),
                    "originario": doc.get("É originário?"),
                    "tipo": doc.get("Tipo"),
                    "unidade": doc.get("Unidade")
                }
            }
            silver_ic_docs.append(silver_doc)

        with open(self.output_silver_ic, 'w', encoding='utf-8') as f:
            json.dump(silver_ic_docs, f, ensure_ascii=False, indent=4)
        return len(silver_ic_docs)
    