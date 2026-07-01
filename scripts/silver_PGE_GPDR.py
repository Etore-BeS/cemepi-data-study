import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_silver_PGE_GPDR import PGE_GPDRTransformerSilver

def run():
    transformer = PGE_GPDRTransformerSilver(
        input_ic_json=PROJECT_ROOT / "data" / "PGE.GPDR.json",
        output_silver_ic=PROJECT_ROOT / "data" / "silver_dados_PGE_GPDR.json"
    )
    
    print("[*] Adaptando dados do outro IC (Bronze) -> Camada Silver...")
    qtd = transformer.json_pge_para_silver()
    print(f"[-] {qtd} documentos do IC padronizados na Camada Silver.")

if __name__ == "__main__":
    run()
    