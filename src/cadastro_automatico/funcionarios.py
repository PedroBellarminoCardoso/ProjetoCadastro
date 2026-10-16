from pathlib import Path

import pandas as pd #Bibloteca para ler a planilha do Excel


ROOT = Path(__file__).resolve().parents[2]
ARQUIVO_EXCEL = ROOT / "data" / "Funcionarios.xlsx" #Vai na pasta data e pega a planilha Funcionarios


def ler_funcionarios() -> list[dict]: #Função para ler os Funcionarios
    if not ARQUIVO_EXCEL.exists():
        raise FileNotFoundError(
            f"Planilha não encontrada: {ARQUIVO_EXCEL}" #Caso não ache exibe a mensagem de erro
        )

    df = pd.read_excel(ARQUIVO_EXCEL) #df le o pandas com o arquivo excel
    df.columns = df.columns.astype(str).str.strip()

    print("Colunas encontradas no Excel:", df.columns.tolist())

    mapeamento = {
        "Nome": "firstName",
        "Nome do meio": "middleName",
        "Sobrenome": "lastName",
        "gerar numero de 1 a 9.999": "employeeId",
    }

    df.rename(columns=mapeamento, inplace=True)

    if "firstName" not in df.columns or "lastName" not in df.columns:
        raise ValueError(
            "Não foi possível identificar as colunas de nome e sobrenome. "
            f"Colunas após o mapeamento: {df.columns.tolist()}"
        )

    funcionarios = []

    for _, linha in df.iterrows():
        nome = linha.get("firstName", "")
        sobrenome = linha.get("lastName", "")
        nome_meio = linha.get("middleName", "")
        employee_id = linha.get("employeeId", "")

        nome = "" if pd.isna(nome) else str(nome).strip()
        sobrenome = "" if pd.isna(sobrenome) else str(sobrenome).strip()
        nome_meio = "" if pd.isna(nome_meio) else str(nome_meio).strip()

        if pd.isna(employee_id) or str(employee_id).strip() == "":
            employee_id = ""
        else:
            employee_id = str(employee_id).strip()
            if employee_id.endswith(".0"):
                employee_id = employee_id[:-2]

        if nome and sobrenome:
            funcionarios.append({
                "firstName": nome,
                "middleName": nome_meio,
                "lastName": sobrenome,
                "employeeId": employee_id,
            })

    print(f"Total de funcionários carregados: {len(funcionarios)}")

    return funcionarios