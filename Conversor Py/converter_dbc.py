import pandas as pd
from dbfread import DBF
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Funções da Interface (GUI) ---

def selecionar_arquivos_dbf():
    """Abre uma caixa de diálogo para selecionar múltiplos arquivos .DBF."""
    root = tk.Tk()
    root.withdraw()
    
    arquivos = filedialog.askopenfilenames(
        title="Selecione os Arquivos .DBF (descompactados pelo TABWIN)",
        filetypes=[("Arquivos DBF", "*.DBF")]
    )
    return arquivos

def selecionar_pasta_destino():
    """Abre uma caixa de diálogo para selecionar a pasta onde os CSVs serão salvos."""
    root = tk.Tk()
    root.withdraw()
    
    pasta = filedialog.askdirectory(
        title="Selecione a Pasta para Salvar os Arquivos .CSV"
    )
    return pasta

# --- Função de Conversão Principal ---

def converter_dbf_para_csv(caminho_arquivo_dbf, caminho_saida_csv):
    """
    Lê um arquivo .DBF usando dbfread e o salva como .CSV usando Pandas.

    :param caminho_arquivo_dbf: Caminho completo para o arquivo .dbf de entrada.
    :param caminho_saida_csv: Caminho completo para o arquivo .csv de saída.
    :return: True se a conversão for bem-sucedida, False caso contrário.
    """
    try:
        # 1. Leitura do arquivo .DBF
        # Usa dbfread para ler o arquivo (table_name.name garante que o nome da tabela seja o nome do arquivo)
        # O encoding 'latin-1' (ou 'cp1252') é comum para arquivos DBF brasileiros.
        tabela = DBF(caminho_arquivo_dbf, encoding='latin-1', load=True)
        
        # 2. Conversão para DataFrame
        df = pd.DataFrame(iter(tabela))
        
        # 3. Exportação para .CSV
        # index=False evita salvar o índice do DataFrame como uma coluna no CSV
        df.to_csv(caminho_saida_csv, index=False, encoding='utf-8')

        return True

    except Exception as e:
        print(f"❌ Erro ao converter {caminho_arquivo_dbf}: {e}")
        return False

# --- Gerenciamento do Fluxo de Trabalho ---

def iniciar_conversao():
    """Gerencia o fluxo de trabalho da interface e da conversão."""
    
    # 1. Selecionar os arquivos DBF de origem
    arquivos_origem = selecionar_arquivos_dbf()
    
    if not arquivos_origem:
        messagebox.showinfo("Cancelado", "Nenhum arquivo DBF selecionado. Conversão cancelada.")
        return

    # 2. Selecionar a pasta de destino
    pasta_destino = selecionar_pasta_destino()
    
    if not pasta_destino:
        messagebox.showinfo("Cancelado", "Nenhuma pasta de destino selecionada. Conversão cancelada.")
        return

    sucessos = 0
    falhas = 0
    
    # 3. Processar cada arquivo
    for caminho_arquivo_dbf in arquivos_origem:
        
        # Cria o nome do arquivo CSV
        nome_arquivo_dbf = os.path.basename(caminho_arquivo_dbf)
        nome_csv = nome_arquivo_dbf.replace('.DBF', '.CSV').replace('.dbf', '.csv')
        caminho_csv_saida = os.path.join(pasta_destino, nome_csv)
        
        print(f"Processando: {nome_arquivo_dbf} -> {caminho_csv_saida}")

        if converter_dbf_para_csv(caminho_arquivo_dbf, caminho_csv_saida):
            sucessos += 1
        else:
            falhas += 1

    # 4. Exibir o resultado final
    messagebox.showinfo(
        "Concluído! 🎉",
        f"Processo de conversão finalizado.\n\n"
        f"✅ Sucessos: {sucessos}\n"
        f"❌ Falhas: {falhas}"
    )

# --- Execução Principal ---

if __name__ == "__main__":
    messagebox.showinfo(
        "Atenção!", 
        "Lembre-se: Use o TABWIN primeiro para descompactar os arquivos .DBC para .DBF. "
        "Este script converterá o .DBF para .CSV."
    )
    iniciar_conversao()