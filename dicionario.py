import pandas as pd
import os

def fix_encoding(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

pasta = "./Dados Simplificados/Hosp/"

dic_Diagnostico = pd.read_csv("CID-10-SUBCATEGORIAS.CSV", sep=';', encoding='utf-8')
dic_Diagnostico = dic_Diagnostico.applymap(fix_encoding)
motivo_saida_map = {
    11:"Alta curado", 
    12:"Alta melhorado", 
    14:"Alta a pedido", 
    15:"Alta com previsão de retorno p/acomp do paciente", 
    16:"Alta por evasão", 
    18:"Alta por outros motivos", 
    19:"Alta de paciente agudo em psiquiatria", 
    21:"Permanência por características próprias da doença", 
    22:"Permanência por intercorrência", 
    23:"Permanência por impossibilidade sócio-familiar", 
    24:"Permanência proc doação órg, tec, cél-doador vivo", 
    25:"Permanência proc doação órg, tec, cél-doador morto", 
    26:"Permanência por mudança de procedimento", 
    27:"Permanência por reoperação", 
    28:"Permanência por outros motivos", 
    29:"Transferência para internação domiciliar", 
    32:"Transferência para internação domiciliar", 
    31:"Transferência para outro estabelecimento", 
    41:"Óbito com DO fornecida pelo médico assistente", 
    42:"Óbito com DO fornecida pelo IML", 
    43:"Óbito com DO fornecida pelo SVO", 
    51:"Encerramento administrativo", 
    61:"Alta da mãe/puérpera e do recém-nascido", 
    17:"Alta da mãe/puérpera e do recém-nascido", 
    62:"Alta da mãe/puérpera e permanência recém-nascido", 
    13:"Alta da mãe/puérpera e permanência recém-nascido", 
    63:"Alta da mãe/puérpera e óbito do recém-nascido", 
    64:"Alta da mãe/puérpera com óbito fetal", 
    65:"Óbito da gestante e do concepto", 
    66:"Óbito da mãe/puérpera e alta do recém-nascido", 
    67:"Óbito da mãe/puérpera e permanência recém-nascido"
}
raca_cor = {
    1:"Branca", 
    2:"Preta", 
    3:"Parda", 
    4:"Amarela", 
    5:"Indígena", 
    99:"Sem Informação"
}
nivel_ensino = {
    1:"Analfabeto", 
    2:"1º grau", 
    3:"2º grau", 
    4:"3º grau", 
    0:"", 
    9:""
}

for arquivo in os.listdir(pasta):
    if arquivo.endswith(".csv"):

        caminho_arquivo = os.path.join(pasta, arquivo)
        print(f"Processando: {arquivo}")

        df = pd.read_csv(caminho_arquivo, encoding="latin1", sep=',')
        df = df.applymap(fix_encoding)

        df["COBRANCA"] = df["COBRANCA"].map(motivo_saida_map)
        df["RACA_COR"] = df["RACA_COR"].map(raca_cor)
        df["INSTRU"] = df["INSTRU"].map(nivel_ensino)
        df["DIAG_PRINC"] = df["DIAG_PRINC"].map(dic_Diagnostico.set_index("SUBCAT")["DESCRICAO"])

        df.to_csv(caminho_arquivo, index=False, encoding="utf-8")

        print(f"Arquivo atualizado: {arquivo}")

print("\nTodos os arquivos foram processados!")