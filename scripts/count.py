import os
import sys

def contar_processos_com_progresso(caminho_arquivo: str):
    if not os.path.exists(caminho_arquivo):
        print(f"[ERRO] O arquivo não foi encontrado no caminho: {caminho_arquivo}")
        return
        
    tamanho_total = os.path.getsize(caminho_arquivo)
    bytes_lidos = 0
    total_processos = 0
    linhas_lidas = 0
    
    print(f"[*] Analisando arquivo ({tamanho_total / (1024*1024):.2f} MB)...")
    print("=" * 60)
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Calcula os bytes lidos para a barra de progresso
                bytes_lidos += len(linha.encode('utf-8'))
                linhas_lidas += 1
                
                # Heurística: No formato gerado pelo seu aggregator (indent=4),
                # a chave "_id" aparece exatamente uma vez por processo.
                if '"_id":' in linha:
                    total_processos += 1
                
                # Atualiza a barra a cada 5000 linhas lidas (para não travar o I/O do terminal)
                if linhas_lidas % 5000 == 0:
                    percentual = (bytes_lidos / tamanho_total) * 100
                    barra_preenchida = int(percentual / 2)  # Barra de 50 caracteres visuais
                    barra = '█' * barra_preenchida + '-' * (50 - barra_preenchida)
                    
                    # O '\r' faz o cursor voltar ao início da linha e sobrescrever a barra anterior
                    sys.stdout.write(f'\r[{barra}] {percentual:.1f}% | Processos contados: {total_processos}')
                    sys.stdout.flush()
                    
        # Garante que a barra feche em 100% no final da leitura
        sys.stdout.write(f'\r[{"█" * 50}] 100.0% | Processos contados: {total_processos}\n')
        sys.stdout.flush()
        
        print("=" * 60)
        print(f"[✅] SUCESSO! O número exato a colocar no artigo é: {total_processos}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema inesperado: {e}")

if __name__ == "__main__":
    # Substitua pelo caminho correto de onde o seu arquivo está salvo
    CAMINHO_DO_ARQUIVO = "data/PGE_GPDR_e_Dados_Capa.json" 
    
    contar_processos_com_progresso(CAMINHO_DO_ARQUIVO)
    