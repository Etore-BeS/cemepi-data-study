import json
import re

class PGE_GPDRTransformerSilver:
    def __init__(self, input_ic_json, output_silver_ic):
        self.input_ic_json = input_ic_json
        self.output_silver_ic = output_silver_ic

    def json_pge_para_silver(self):
        with open(self.input_ic_json, 'r', encoding='utf-8') as f:
            dados_ic = json.load(f)

        qtd = 0
        # Padrão JSON Lines: Escreve linha por linha diretamente no disco
        with open(self.output_silver_ic, 'w', encoding='utf-8') as f_out:
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
                # Escreve o objeto convertido em string e pula a linha
                f_out.write(json.dumps(silver_doc, ensure_ascii=False) + '\n')
                qtd += 1

        return qtd
    