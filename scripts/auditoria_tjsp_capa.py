import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_auditoria_tjsp_capa import AuditoriaPGE

def run():
    auditor = AuditoriaPGE(
        input_json=PROJECT_ROOT / "data" / "PGE.GPDR.json",
        output_csv=PROJECT_ROOT / "data" / "coleta_tjsp_resultados.csv",
        pendentes_file=PROJECT_ROOT / "data" / "processos_pendentes.json"
    )
    
    print("[*] Iniciando Auditoria e Sanidade de Dados (Bronze)")
    dups = auditor.remover_duplicados_csv()
    print(f"[-] Duplicatas limpas fisicamente do CSV: {dups}")
    
    esperados, coletados, faltantes = auditor.auditar_e_gerar_pendencias()
    print(f"[-] Total Esperado: {esperados} | Coletados Únicos: {coletados} | Pendentes para coleta: {faltantes}")
    print("[*] Auditoria concluída. Arquivo de pendências atualizado.")

if __name__ == "__main__":
    run()
    