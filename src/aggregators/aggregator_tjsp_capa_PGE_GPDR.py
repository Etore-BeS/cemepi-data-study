import json

class AggregatorGold:
    def __init__(self, silver_nossos, silver_ic, output_gold):
        self.silver_nossos = silver_nossos
        self.silver_ic = silver_ic
        self.output_gold = output_gold

    def realizar_join_gold(self):
        """Une as duas bases Silver usando processo_pk e expurga a chave temporária."""
        with open(self.silver_nossos, 'r', encoding='utf-8') as f:
            dados_nossos = json.load(f)
            
        with open(self.silver_ic, 'r', encoding='utf-8') as f:
            dados_ic = json.load(f)

        dict_ic = {item["processo_pk"]: item for item in dados_ic if item.get("processo_pk")}

        gold_docs = []
        for doc_nosso in dados_nossos:
            pk = doc_nosso.get("processo_pk")
            doc_ic = dict_ic.get(pk, {})

            gold_doc = {**doc_nosso}
            
            if "_id" in doc_ic: gold_doc["_id"] = doc_ic["_id"]
            if "metadados" in doc_ic: gold_doc["metadados"] = doc_ic["metadados"]
            
            if "processo_pk" in gold_doc:
                del gold_doc["processo_pk"]

            gold_docs.append(gold_doc)

        with open(self.output_gold, 'w', encoding='utf-8') as f:
            json.dump(gold_docs, f, ensure_ascii=False, indent=4)
            
        return len(gold_docs)
    