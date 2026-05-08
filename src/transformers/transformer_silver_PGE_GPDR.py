import json

class TransformerSilverDadosIC:
    def __init__(self, input_ic_json, output_silver_ic):
        self.input_ic_json = input_ic_json
        self.output_silver_ic = output_silver_ic

    def json_pge_para_silver(self):
        """Lê os dados originais do IC e estrutura para a camada Silver."""
        with open(self.input_ic_json, 'r', encoding='utf-8') as f:
            dados_ic = json.load(f)

        silver_ic_docs = []
        for doc in dados_ic:
            silver_doc = {
                "processo_pk": doc.get("Processo"), 
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
    