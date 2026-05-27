import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.aggregators.aggregator_tjsp_capa_PGE_GPDR import FacePGEGPDRAggregator

def run():
    aggregator = FacePGEGPDRAggregator(
        silver_nossos=PROJECT_ROOT / "data" / "silver_dados_capa_tjsp.json",
        silver_ic=PROJECT_ROOT / "data" / "silver_dados_PGE_GPDR.json",
        output_gold=PROJECT_ROOT / "data" / "gold_tjsp_enriquecido.json",
        output_pendentes=PROJECT_ROOT / "data" / "processos_pendentes_final.json"
    )
    
    print("[*] Inicializando processo de Enriquecimento (Left Join)...")
    qtd_gold, qtd_ricos, qtd_pobres = aggregator.realizar_join_gold()
    
    print(f"[*] SUCESSO ABSOLUTO! {qtd_gold} documentos gerados na Camada GOLD.")
    print(f"    -> Documentos 'Ricos' (Com Capa): {qtd_ricos}")
    print(f"    -> Documentos 'Pobres' (Aguardando Capa): {qtd_pobres}")
    print(f"[!] Fila de retentativa gerada com {qtd_pobres} processos em: processos_pendentes_final.json")

if __name__ == "__main__":
    run()
    