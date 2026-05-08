import json
import pandas as pd
from collections import Counter
from pathlib import Path

class AuditoriaPGE:
    def __init__(self, input_json, output_csv, pendentes_file):
        self.input_json = input_json
        self.output_csv = output_csv
        self.pendentes_file = pendentes_file

    def remover_duplicados_csv(self):
        """Lê o CSV, remove linhas duplicadas baseadas no número do processo e sobrescreve."""
        if not self.output_csv.exists():
            return 0
        df = pd.read_csv(self.output_csv)
        total_original = len(df)
        df.drop_duplicates(subset=["Processo"], keep="first", inplace=True)
        total_limpo = len(df)
        duplicatas_removidas = total_original - total_limpo
        
        if duplicatas_removidas > 0:
            df.to_csv(self.output_csv, index=False)
        return duplicatas_removidas

    def auditar_e_gerar_pendencias(self):
        """Cruza a base JSON com o CSV e gera o arquivo de processos faltantes."""
        with open(self.input_json, 'r', encoding='utf-8') as f:
            dados_base = json.load(f)
        
        processos_esperados = [p for p in dados_base if p.get('Processo')]
        
        if not self.output_csv.exists():
            processos_coletados = []
        else:
            df_coletado = pd.read_csv(self.output_csv, usecols=["Processo"])
            processos_coletados = df_coletado["Processo"].astype(str).tolist()

        set_coletados = set(processos_coletados)
        pendentes = [p for p in processos_esperados if p['Processo'] not in set_coletados]

        with open(self.pendentes_file, 'w', encoding='utf-8') as f:
            json.dump(pendentes, f, ensure_ascii=False, indent=4)

        return len(processos_esperados), len(set_coletados), len(pendentes)
    