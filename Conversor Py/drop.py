import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

# --- 1. Mapeamento de Colunas Essenciais para o DW ---
# A chave é o nome da coluna no arquivo CSV.
# O valor é a descrição (para documentação e clareza).
COLUNAS_MAPA = {
    # MÉTRICAS (Fatos)
    'VAL_SH': 'Valor de Serviços Hospitalares (Métrica)',
    'VAL_SP': 'Valor de Serviços Profissionais (Métrica)',
    'VAL_TOT': 'Valor Total da AIH (Métrica Principal)',
    'VAL_UTI': 'Valor Gasto com UTI (Métrica)',
    'VAL_UCI': 'Valor Gasto com UCI (Métrica)',
    'VAL_VALATO': 'Valor da AIH no Ato Hospitalar (Métrica)',
    'DIAS_PERM': 'Dias de Permanência (Métrica)',
    'TEMP_PERM': 'Tempo de Permanência (Código de faixa de dias)',
    'MORTE': 'Indicador de Morte (Sim/Não - Métrica)',
    'SP_QT_PROC': 'Quantidade de Procedimentos Realizados (Métrica)',
    
    # DIMENSÕES - Tempo, Local, Estabelecimento e AIH
    'DT_INTER': 'Data de Internação (Dimensão Tempo)',
    'DT_SAIDA': 'Data de Saída (Dimensão Tempo / Cálculo de Permanência)',
    'CNES': 'Código CNES do Hospital/Estabelecimento (Dimensão Estabelecimento)',
    'COBRANCA': 'Tipo de Cobrança da AIH',
    'SEQ_AIH5': 'Sequencial da AIH (Identificador da AIH)',
    'SP_NAIH': 'Número da AIH (Identificador Único)',
    'SP_CNES': 'CNES do Prestador de Serviços (Dimensão Estabelecimento)',
    'SP_UF': 'UF do Prestador de Serviços (Dimensão Localização)',
    'SP_AA': 'Ano da AIH (Dimensão Tempo)',
    'SP_MM': 'Mês da AIH (Dimensão Tempo)',
    'SP_DTINTER': 'Data de Internação (Confirmação)',
    'SP_DTSAIDA': 'Data de Saída (Confirmação)',
    'SP_GESTOR': 'Código do Gestor (Federal, Estadual, Municipal)',
    'SP_U_AIH': 'Unidade da AIH (Principal/Secundária)',
    
    # DIMENSÕES - Diagnóstico e Procedimento
    'DIAG_PRINC': 'CID Principal (Dimensão CID)',
    'CID_ASSO': 'CID Secundário/Associado (Dimensão CID)',
    'CID_MORTE': 'CID Causa da Morte (Dimensão CID)',
    'CID_NOTIF': 'CID de Notificação (Dimensão CID)',
    'SP_PROCREA': 'Código do Procedimento Principal (Dimensão Procedimento)',
    
    # DIMENSÕES - Socio-demográficas
    'IDADE': 'Idade do Paciente (Dimensão Pessoas/Faixa Etária)',
    'INSTRU': 'Grau de Instrução do Paciente (Dimensão Pessoas)',
    'RACA_COR': 'Raça/Cor do Paciente (Dimensão Pessoas)',
    'ETNIA': 'Etnia do Paciente (Dimensão Pessoas)',
    'SP_M_HOSP': 'Código do Motivo da Saída/Permanência (Dimensão Motivo)'
}

COLUNAS_ESSENCIAIS = list(COLUNAS_MAPA.keys())

# --- 2. Mapeamento de Tipos de Dados e Limpeza ---

# Colunas que representam valores monetários e precisam ser limpas e convertidas
CURRENCY_COLUMNS = [
    'VAL_SH', 'VAL_SP', 'VAL_TOT', 'VAL_UTI', 'VAL_UCI', 'VAL_VALATO'
]

# Colunas que representam datas (formato 'AAAAMMDD' ou similar do DATASUS)
DATE_COLUMNS = [
    'DT_INTER', 'DT_SAIDA', 'SP_DTINTER', 'SP_DTSAIDA'
]

# Colunas que devem ser tratadas como números inteiros (Int64 suporta NaN)
INTEGER_COLUMNS = [
    'DIAS_PERM', 'MORTE', 'SP_QT_PROC', 'IDADE'
]

def clean_currency(series):
    """
    Limpa strings de valor, removendo caracteres não-dígitos e garantindo formato numérico.
    Assume que o valor é fixo-ponto (os 2 últimos dígitos são centavos).
    """
    # 1. Converte para string e trata NaNs
    s = series.astype(str).str.strip().replace({'nan': np.nan, 'NAN': np.nan})
    
    # Mantém o índice original para usar loc no final
    nan_mask = s.isna()
    
    # 2. Remove TODOS os caracteres não-dígitos, exceto se for NaN
    # Isso resolve o problema de pontos/vírgulas introduzidos na conversão DBF->CSV.
    s_clean = s.str.replace(r'[^\d]', '', regex=True).fillna('0')

    # 3. Insere o ponto decimal (logica DATASUS: últimos 2 dígitos = centavos)
    # Pega tudo exceto os 2 ultimos digitos + '.' + Pega os 2 ultimos digitos
    s_processed = (s_clean.str.slice(0, -2) + '.' + s_clean.str.slice(-2))
    
    # 4. Converte para float
    result = s_processed.astype(float)
    
    # 5. Restaura NaN para os valores que eram NaN originalmente
    result.loc[nan_mask] = np.nan
    
    return result

def processar_csv(caminho_entrada_csv, caminho_saida_csv):
    """
    Carrega o CSV, mantém apenas as colunas essenciais, corrige os tipos de dados
    (data, valor) e salva um novo CSV limpo.
    """
    try:
        # 1. Carregar o arquivo CSV no Pandas
        df = pd.read_csv(caminho_entrada_csv, sep=',', encoding='latin-1', low_memory=False)
        
        colunas_disponiveis = set(df.columns)
        colunas_a_manter = [col for col in COLUNAS_ESSENCIAIS if col in colunas_disponiveis]
        colunas_removidas = [col for col in COLUNAS_ESSENCIAIS if col not in colunas_disponiveis]
        
        if not colunas_a_manter:
            raise ValueError(f"Nenhuma das colunas essenciais foi encontrada no arquivo. Colunas procuradas: {COLUNAS_ESSENCIAIS}")

        # Realiza o 'drop' (seleção) mantendo apenas as colunas essenciais
        df_limpo = df[colunas_a_manter].copy() # Usar .copy() para evitar SettingWithCopyWarning

        # 2. Conversão e Limpeza de Tipos (Data Casting)
        print("\n--- Iniciando Conversão de Tipos e Limpeza ---")

        # A. Limpeza e Conversão de Valores Monetários (Ex: 123456 -> 1234.56)
        for col in [c for c in CURRENCY_COLUMNS if c in df_limpo.columns]:
            df_limpo[col] = clean_currency(df_limpo[col])
            print(f"💰 {col} limpa e convertida para Float.")

        # B. Conversão de Datas (Ex: 20240115 -> 2024-01-15)
        for col in [c for c in DATE_COLUMNS if c in df_limpo.columns]:
            # Formato esperado: AAAAMMDD
            df_limpo[col] = pd.to_datetime(df_limpo[col], format='%Y%m%d', errors='coerce')
            print(f"📅 {col} convertida para Data.")

        # C. Conversão de Inteiros (Usando Int64 para preservar NaN)
        for col in [c for c in INTEGER_COLUMNS if c in df_limpo.columns]:
            # Usa to_numeric com errors='coerce' para transformar valores inválidos em NaN
            df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce').astype('Int64')
            print(f"🔢 {col} convertida para Inteiro (Int64).")


        # 3. Salvar o arquivo transformado
        df_limpo.to_csv(caminho_saida_csv, index=False, encoding='utf-8')

        print("\n--- Colunas Mantidas e Descrições ---")
        for col in colunas_a_manter:
            print(f"✅ {col}: {COLUNAS_MAPA.get(col, 'DESCRIÇÃO INDISPONÍVEL')}")

        if colunas_removidas:
            print("\n--- ATENÇÃO: Colunas Esperadas Não Encontradas ---")
            print(f"Colunas ausentes no arquivo: {colunas_removidas}")

        return True

    except Exception as e:
        print(f"❌ Erro ao processar {os.path.basename(caminho_entrada_csv)}: {e}")
        return False

# --- Funções da Interface (GUI) ---

def selecionar_arquivos_csv():
    """Abre uma caixa de diálogo para selecionar múltiplos arquivos CSV."""
    root = tk.Tk()
    root.withdraw()
    
    arquivos = filedialog.askopenfilenames(
        title="Selecione os Arquivos CSV das Internações (AIH)",
        filetypes=[("Arquivos CSV", "*.csv")]
    )
    return arquivos

def selecionar_pasta_destino():
    """Abre uma caixa de diálogo para selecionar a pasta onde os CSVs limpos serão salvos."""
    root = tk.Tk()
    root.withdraw()
    
    pasta = filedialog.askdirectory(
        title="Selecione a Pasta para Salvar os Arquivos CSV Limpos e Tipados"
    )
    return pasta

# --- Gerenciamento do Fluxo de Trabalho (Main) ---

def iniciar_aplicativo():
    """Gerencia o fluxo de trabalho da interface e do processamento."""
    
    # 1. Selecionar os arquivos CSV de origem
    arquivos_origem = selecionar_arquivos_csv()
    
    if not arquivos_origem:
        messagebox.showinfo("Cancelado", "Nenhum arquivo CSV selecionado. Aplicação cancelada.")
        return

    # 2. Selecionar a pasta de destino
    pasta_destino = selecionar_pasta_destino()
    
    if not pasta_destino:
        messagebox.showinfo("Cancelado", "Nenhuma pasta de destino selecionada. Aplicação cancelada.")
        return

    sucessos = 0
    falhas = 0
    
    # 3. Processar cada arquivo
    for caminho_entrada_csv in arquivos_origem:
        
        nome_arquivo = os.path.basename(caminho_entrada_csv)
        # Cria o nome do arquivo de saída (ex: "Limpo_RDSP2401.csv")
        nome_csv_saida = f"Limpo_Tipado_{nome_arquivo}"
        caminho_csv_saida = os.path.join(pasta_destino, nome_csv_saida)
        
        print(f"\nIniciando processamento e tipagem de: {nome_arquivo}")

        if processar_csv(caminho_entrada_csv, caminho_csv_saida):
            sucessos += 1
        else:
            falhas += 1

    # 4. Exibir o resultado final
    messagebox.showinfo(
        "Processamento Concluído! 🥳",
        f"Limpeza de colunas e tipagem de dados finalizada.\n\n"
        f"✅ Arquivos processados com sucesso: {sucessos}\n"
        f"❌ Falhas: {falhas}"
    )

if __name__ == "__main__":
    iniciar_aplicativo()