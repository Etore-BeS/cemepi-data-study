import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.transformers.transformer_erros_dados_capa_bronze import TransformerErrosDadosCapaBronze

def run():
    # Definição Estrita de Caminhos
    csv_repescagem = PROJECT_ROOT / "data" / "coleta_tjsp_resultados.csv"
    csv_master_bkp = PROJECT_ROOT / "data" / "coleta_tjsp_resultados_BKP.csv"
    csv_duplicados = PROJECT_ROOT / "data" / "duplicado_dados_capa.csv" 
    
    json_pendentes_leitura = PROJECT_ROOT / "data" / "processos_pendentes_final.json"
    json_pendentes_saida = PROJECT_ROOT / "data" / "processos_pendentes_restantes.json"

    print("="*60)
    print("🛠️ INICIANDO MERGE NA CAMADA BRONZE E REDUÇÃO DE FILA")
    print("="*60)

    # Instancia o Transformer
    transformer = TransformerErrosDadosCapaBronze(
        csv_repescagem=csv_repescagem,
        csv_master=csv_master_bkp,
        csv_duplicados=csv_duplicados,
        json_leitura=json_pendentes_leitura,
        json_saida=json_pendentes_saida
    )

    try:
        print("[*] Lendo arquivos, identificando falhas e reduzindo fila de pendentes...")
        print("[*] Executando Anti-Join de duplicatas contra o arquivo Mestre...")
        
        metricas = transformer.processar_merge_e_fila()
        
        print("\n" + "="*60)
        print(f"[🏁] RODADA DA BRONZE CONCLUÍDA COM SUCESSO!")
        print(f"    -> Inéditos adicionados à base mestra: {metricas['injetados']}")
        print(f"    -> Duplicatas isoladas em 'duplicado_dados_capa.csv': {metricas['duplicados']}")
        print(f"    -> Falhas expurgadas e transferidas para a NOVA Fila: {metricas['falhas_expurgadas']}")
        print(f"    -> Pendentes Restantes ('processos_pendentes_restantes.json'): {metricas['restantes_fila']}")
        print(f"    -> O arquivo 'coleta_tjsp_resultados.csv' foi mantido intacto para sua auditoria.")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"[!] {e} Rode o scraper primeiro para gerar novos dados.")
    except Exception as e:
        print(f"[❌] ERRO FATAL no pipeline de repescagem: {e}")

if __name__ == "__main__":
    run()
