import json
import pandas as pd
import re
from pathlib import Path

class FaceAuditoriaTJSP:
    def __init__(self, input_json, output_csv, pendentes_file):
        self.input_json = input_json
        self.output_csv = output_csv
        self.pendentes_file = pendentes_file

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
            sufixo = str(int(sufixo))
            return f"{base_mascarada}/{sufixo}"
        return base_mascarada

    def auditar_limpar_csv(self):
        if not self.output_csv.exists():
            return 0, 0
        
        df = pd.read_csv(self.output_csv)
        
        filtro_falha = (df["Classe"] == "NÃO HÁ REGISTRO") & (df["Foro"] == "NÃO HÁ REGISTRO")
        falhas_removidas = filtro_falha.sum()
        df = df[~filtro_falha].copy()
        
        # 2. Padroniza a chave primária com máscara e barra, e remove duplicatas reais
        df["Processo"] = df["Processo"].apply(self._padronizar_processo)
        total_pos_falha = len(df)
        df.drop_duplicates(subset=["Processo"], keep="first", inplace=True)
        duplicatas_removidas = total_pos_falha - len(df)
        
        if falhas_removidas > 0 or duplicatas_removidas > 0:
            df.to_csv(self.output_csv, index=False)
            
        return falhas_removidas, duplicatas_removidas

    def auditar_e_gerar_pendencias(self):
        """Cruza a base JSON com o CSV limpo e gera o arquivo de pendentes."""
        with open(self.input_json, 'r', encoding='utf-8') as f:
            dados_base = json.load(f)
        
        processos_esperados = [p for p in dados_base if p.get('Processo')]
        
        if not self.output_csv.exists():
            set_coletados = set()
        else:
            df_coletado = pd.read_csv(self.output_csv, usecols=["Processo"])
            set_coletados = set(df_coletado["Processo"].astype(str).tolist())
        
        pendentes = []
        for p in processos_esperados:
            proc_padrao = self._padronizar_processo(p.get('Processo'))
            if proc_padrao and proc_padrao not in set_coletados:
                p['Processo'] = proc_padrao
                pendentes.append(p)

        with open(self.pendentes_file, 'w', encoding='utf-8') as f:
            json.dump(pendentes, f, ensure_ascii=False, indent=4)

        return len(processos_esperados), len(set_coletados), len(pendentes)

    def auditar_sandbox_repescagem(self, sandbox_csv_path, pendentes_json_path):
        # Audita especificamente a rodada de repescagem isolada.
        path_csv = Path(sandbox_csv_path)
        path_json = Path(pendentes_json_path)

        if not path_csv.exists():
            return 0, 0, 0
            
        df = pd.read_csv(path_csv)
        total_inical = len(df)
        
        # 1. Filtra as falhas
        filtro_falha = (df["Classe"] == "NÃO HÁ REGISTRO") & (df["Foro"] == "NÃO HÁ REGISTRO")
        df_sucesso = df[~filtro_falha].copy()
        
        # 2. Remove duplicatas e salva o CSV apenas com os Ricos
        if not df_sucesso.empty:
            df_sucesso["Processo"] = df_sucesso["Processo"].apply(self._padronizar_processo)
            df_sucesso.drop_duplicates(subset=["Processo"], keep="first", inplace=True)
            df_sucesso.to_csv(path_csv, index=False)
        else:
            # Se tudo falhou, cria um CSV vazio com o cabeçalho
            df_sucesso.to_csv(path_csv, index=False)
            
        sucessos = len(df_sucesso)
        falhas_expurgadas = total_inical - sucessos
        
        # 3. Atualiza a lista de pendentes final para a próxima tentativa
        set_sucessos = set(df_sucesso["Processo"].astype(str).tolist())
        
        with open(path_json, 'r', encoding='utf-8') as f:
            dados_pendentes = json.load(f)
            
        novos_pendentes = []
        for p in dados_pendentes:
            proc_padrao = self._padronizar_processo(p.get('Processo', p.get('processo_pk')))
            if proc_padrao and proc_padrao not in set_sucessos:
                novos_pendentes.append(p)
                
        with open(path_json, 'w', encoding='utf-8') as f:
            json.dump(novos_pendentes, f, ensure_ascii=False, indent=4)
            
        return sucessos, falhas_expurgadas, len(novos_pendentes)
    