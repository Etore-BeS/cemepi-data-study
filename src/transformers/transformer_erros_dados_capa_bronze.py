import json
import pandas as pd
import re
from pathlib import Path

class TransformerErrosDadosCapaBronze:
    def __init__(self, csv_repescagem, csv_master, csv_duplicados, json_leitura, json_saida):
        self.csv_repescagem = Path(csv_repescagem)
        self.csv_master = Path(csv_master)
        self.csv_duplicados = Path(csv_duplicados)
        self.json_leitura = Path(json_leitura)
        self.json_saida = Path(json_saida)

    def _padronizar_processo(self, proc_str):
        proc_str = str(proc_str).strip()
        if not proc_str or proc_str == 'nan': return ""
        
        if '/' in proc_str:
            partes = proc_str.split('/')
            base_limpa = re.sub(r'\D', '', partes[0])
            sufixo = re.sub(r'\D', '', partes[1])
        else:
            limpo = re.sub(r'\D', '', proc_str)
            if len(limpo) > 20:
                base_limpa = limpo[:20]
                sufixo = limpo[20:]
            else:
                base_limpa = limpo
                sufixo = ""
                
        base_mascarada = f"{base_limpa[:7]}-{base_limpa[7:9]}.{base_limpa[9:13]}.{base_limpa[13]}.{base_limpa[14:16]}.{base_limpa[16:]}" if len(base_limpa) == 20 else base_limpa
        
        if sufixo:
            return f"{base_mascarada}/{str(int(sufixo))}"
        return base_mascarada

    def processar_merge_e_fila(self):
        # Executa a pipeline completa: Expurgos, Fila de Pendentes e Anti-Join de Duplicatas. Retorna um dicionário com as métricas para o orquestrador.
        
        if not self.csv_repescagem.exists():
            raise FileNotFoundError("Arquivo de repescagem não encontrado.")

        arquivo_alvo_auditoria = self.json_saida if self.json_saida.exists() else self.json_leitura

        # 1. Leitura e Separação
        df_coleta_bruta = pd.read_csv(self.csv_repescagem, dtype=str)
        df_coleta_bruta["Processo_Padrao"] = df_coleta_bruta["Processo"].apply(self._padronizar_processo)

        filtro_falha = (df_coleta_bruta["Classe"] == "NÃO HÁ REGISTRO") & (df_coleta_bruta["Foro"] == "NÃO HÁ REGISTRO")
        df_falhas = df_coleta_bruta[filtro_falha].copy()
        df_sucesso = df_coleta_bruta[~filtro_falha].copy()

        df_falhas.drop_duplicates(subset=["Processo_Padrao"], keep="first", inplace=True)
        df_sucesso.drop_duplicates(subset=["Processo_Padrao"], keep="first", inplace=True)
        
        qtd_falhas = len(df_falhas)
        qtd_sucessos = len(df_sucesso)

        # 2. Redução da Fila (Falhas viram Pendentes)
        with open(arquivo_alvo_auditoria, 'r', encoding='utf-8') as f:
            fila_atual = json.load(f)

        set_processos_falhos = set(df_falhas["Processo_Padrao"].tolist())
        nova_fila = []
        
        for proc_json in fila_atual:
            chave = str(proc_json.get('Processo', proc_json.get('processo_pk', '')))
            if self._padronizar_processo(chave) in set_processos_falhos:
                nova_fila.append(proc_json)

        with open(self.json_saida, 'w', encoding='utf-8') as f:
            json.dump(nova_fila, f, ensure_ascii=False, indent=4)

        restantes = len(nova_fila)
        qtd_injetar, qtd_duplicados = 0, 0

        # Se houveram sucessos, aplica o Anti-Join
        if qtd_sucessos > 0:
            if self.csv_master.exists():
                df_master_keys = pd.read_csv(self.csv_master, usecols=["Processo"], dtype=str)
                set_master = set(df_master_keys["Processo"].apply(self._padronizar_processo).tolist())
                del df_master_keys 
                
                mask_duplicados = df_sucesso["Processo_Padrao"].isin(set_master)
                df_duplicados = df_sucesso[mask_duplicados].copy()
                df_injetar = df_sucesso[~mask_duplicados].copy()
            else:
                df_injetar = df_sucesso.copy()
                df_duplicados = pd.DataFrame()
                
            qtd_duplicados = len(df_duplicados)
            qtd_injetar = len(df_injetar)

            if 'Processo_Padrao' in df_injetar.columns: del df_injetar['Processo_Padrao']
            if 'Processo_Padrao' in df_duplicados.columns: del df_duplicados['Processo_Padrao']

            if qtd_injetar > 0:
                precisa_cab_master = not self.csv_master.exists()
                df_injetar.to_csv(self.csv_master, mode='a', index=False, header=precisa_cab_master, encoding='utf-8')
                
            if qtd_duplicados > 0:
                precisa_cab_dup = not self.csv_duplicados.exists()
                df_duplicados.to_csv(self.csv_duplicados, mode='a', index=False, header=precisa_cab_dup, encoding='utf-8')

        return {
            "injetados": qtd_injetar,
            "duplicados": qtd_duplicados,
            "falhas_expurgadas": qtd_falhas,
            "restantes_fila": restantes
        }
    