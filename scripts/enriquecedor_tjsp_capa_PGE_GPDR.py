import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.aggregators.aggregator_tjsp_capa_PGE_GPDR import AggregatorGold

def run():
    aggregator = AggregatorGold(
        silver_nossos=PROJECT_ROOT / "data" / "silver_dados_capa_tjsp.json",
        silver_ic=PROJECT_ROOT / "data" / "silver_dados_PGE_GPDR.json",
        output_gold=PROJECT_ROOT / "data" / "gold_tjsp_enriquecido.json"
    )
    
    print("[*] Inicializando processo de Enriquecimento (Join)...")
    qtd = aggregator.realizar_join_gold()
    print(f"[*] SUCESSO ABSOLUTO! {qtd} documentos gerados na Camada GOLD e prontos para o MongoDB.")

if __name__ == "__main__":
    run()
    