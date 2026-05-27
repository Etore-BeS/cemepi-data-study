import json

class FacePGEGPDRAggregator:
    def __init__(self, silver_nossos, silver_ic, output_gold, output_pendentes):
        self.silver_nossos = silver_nossos
        self.silver_ic = silver_ic
        self.output_gold = output_gold
        self.output_pendentes = output_pendentes

    def realizar_join_gold(self):
        dict_nossos = {}
        
        # Leitura em Fluxo (Streaming) da base TJSP
        with open(self.silver_nossos, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                item = json.loads(line) # Carrega apenas 1 processo na memória
                if item.get("processo_pk"):
                    dict_nossos[item["processo_pk"]] = item

        qtd_gold, qtd_ricos, qtd_pobres = 0, 0, 0

        # Escrita Streaming para a Camada Gold e Fila
        with open(self.output_gold, 'w', encoding='utf-8') as f_gold, \
             open(self.output_pendentes, 'w', encoding='utf-8') as f_pendentes:
             
            f_gold.write('[\n')
            f_pendentes.write('[\n')
            
            first_gold, first_pendente = True, True

            # Leitura em Fluxo da base PGE
            with open(self.silver_ic, 'r', encoding='utf-8') as f_ic:
                for line in f_ic:
                    if not line.strip(): continue
                    doc_ic = json.loads(line)
                    
                    pk = doc_ic.get("processo_pk")
                    doc_nosso = dict_nossos.get(pk)

                    if doc_nosso:
                        qtd_ricos += 1
                        gold_doc = {**doc_nosso}
                        if "_id" in doc_ic: gold_doc["_id"] = doc_ic["_id"]
                        if "metadados" in doc_ic: gold_doc["metadados"] = doc_ic["metadados"]
                        if "processo_pk" in gold_doc: del gold_doc["processo_pk"]
                    else:
                        qtd_pobres += 1
                        gold_doc = {
                            "_id": doc_ic.get("_id"),
                            "processo_pk": pk,
                            "metadados": doc_ic.get("metadados"),
                            "status_coleta": "PENDENTE_CAPA"
                        }
                        if not first_pendente: f_pendentes.write(',\n')
                        json.dump(doc_ic, f_pendentes, ensure_ascii=False, indent=4)
                        first_pendente = False

                    if not first_gold: f_gold.write(',\n')
                    json.dump(gold_doc, f_gold, ensure_ascii=False, indent=4)
                    first_gold = False
                    qtd_gold += 1

            f_gold.write('\n]')
            f_pendentes.write('\n]')
            
        return qtd_gold, qtd_ricos, qtd_pobres
    