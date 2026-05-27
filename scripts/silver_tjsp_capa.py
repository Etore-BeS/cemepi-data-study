import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_json_tjsp_capa import FaceTransformerSilverTJSP

def run():
    arquivo_csv = PROJECT_ROOT / "data" / "coleta_tjsp_resultados.csv"
    arquivo_silver = PROJECT_ROOT / "data" / "silver_dados_capa_tjsp.json"

    transformer = FaceTransformerSilverTJSP(
        input_csv=arquivo_csv,
        output_silver=arquivo_silver
    )
    
    print("="*60)
    print("💎 INICIANDO PIPELINE DE TRANSFORMAÇÃO SILVER (CAPA TJSP)")
    print("="*60)
    print("[*] Lendo CSV e aplicando Schema-on-Read (Padrão MongoDB)...")
    
    try:
        qtd_silver = transformer.transformar_csv_para_silver()
        print(f"[✅] SUCESSO! {qtd_silver} documentos modelados diretamente na Camada Silver.")
    except Exception as e:
        print(f"[❌] ERRO FATAL na conversão Silver: {e}")

if __name__ == "__main__":
    run()
    