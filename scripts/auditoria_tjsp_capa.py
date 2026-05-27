import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_auditoria_tjsp_capa import FaceAuditoriaTJSP

def run():
    auditor = FaceAuditoriaTJSP(
        input_json=PROJECT_ROOT / "data" / "PGE.GPDR.json",
        output_csv=PROJECT_ROOT / "data" / "coleta_tjsp_resultados.csv",
        pendentes_file=PROJECT_ROOT / "data" / "processos_pendentes.json"
    )
    
    print("[*] Iniciando Auditoria e Sanidade de Dados (Bronze)")
    falhas, dups = auditor.auditar_limpar_csv()
    print(f"[-] Processos corrompidos ('NÃO HÁ REGISTRO') expurgados do CSV: {falhas}")
    print(f"[-] Duplicatas reais limpas fisicamente do CSV: {dups}")
    
    esperados, coletados, faltantes = auditor.auditar_e_gerar_pendencias()
    print(f"[-] Total Esperado: {esperados} | Coletados Únicos: {coletados} | Pendentes para coleta: {faltantes}")
    print("[*] Auditoria concluída. Arquivo de pendências atualizado.")

if __name__ == "__main__":
    run()
    