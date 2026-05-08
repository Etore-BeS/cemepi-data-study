import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_json_tjsp_capa import TransformerSilverNossosDados

def run():
    transformer = TransformerSilverNossosDados(
        input_csv=PROJECT_ROOT / "data" / "coleta_tjsp_resultados.csv",
        output_json_bruto=PROJECT_ROOT / "data" / "tjsp_dados_brutos.json",
        output_silver=PROJECT_ROOT / "data" / "silver_dados_capa_tjsp.json"
    )
    
    print("[*] Transformando Bronze (CSV) -> JSON Bruto...")
    qtd_bruto = transformer.csv_para_json_bruto()
    print(f"[-] {qtd_bruto} registros gerados no JSON bruto.")
    
    print("[*] Refinando JSON Bruto -> Camada Silver (Infra Professor)...")
    qtd_silver = transformer.json_bruto_para_silver()
    print(f"[-] {qtd_silver} documentos modelados na Camada Silver.")

if __name__ == "__main__":
    run()
    