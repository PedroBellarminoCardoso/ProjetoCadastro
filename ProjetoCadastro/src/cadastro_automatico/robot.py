
import os
import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from cadastro_automatico.funcionarios import ler_funcionarios


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports"


def fazer_login_com_playwright():
    """
    Usa Playwright exclusivamente para fazer login.
    Depois transfere os cookies para requests.Session().
    """
    load_dotenv(ROOT / ".env")

    base_url = os.getenv("ORANGEHRM_URL", "").strip().rstrip("/")
    username = os.getenv("ORANGEHRM_USERNAME", "").strip()
    password = os.getenv("ORANGEHRM_PASSWORD", "")

    if not base_url or not username or not password:
        raise ValueError(
            "Configure ORANGEHRM_URL, ORANGEHRM_USERNAME "
            "e ORANGEHRM_PASSWORD no arquivo .env."
        )

    session = requests.Session()
    session.headers.update({
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
    })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            url_login = f"{base_url}/web/index.php/auth/login"
            resposta = page.goto(
                url_login,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            print(f"Página aberta: {page.url}")
            print(f"Título: {page.title()}")

            if resposta and resposta.status >= 400:
                raise RuntimeError(
                    f"Erro ao abrir a página de login: HTTP {resposta.status}"
                )

            # Espera os campos reais da tela aparecerem.
            campo_usuario = page.locator('input[name="username"]')
            campo_senha = page.locator('input[name="password"]')

            campo_usuario.wait_for(state="visible", timeout=20000)
            campo_senha.wait_for(state="visible", timeout=10000)

            campo_usuario.fill(username)
            campo_senha.fill(password)
            page.get_by_role("button", name="Login").click()

            # Espera sair da rota de login.
            page.wait_for_function(
                "() => !window.location.pathname.includes('/auth/login')",
                timeout=30000,
            )

            print(f"URL após login: {page.url}")

            if "/auth/login" in page.url:
                raise RuntimeError(
                    "O login não foi concluído. Verifique as credenciais."
                )

            # Transfere os cookies do navegador para Requests.
            cookies = context.cookies()

            if not cookies:
                raise RuntimeError(
                    "O navegador não forneceu cookies para a sessão."
                )

            for cookie in cookies:
                session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                    secure=cookie.get("secure", False),
                )

            # Alguns sites usam um token CSRF em cookie.
            nomes_csrf = {
                "csrf-token",
                "csrftoken",
                "orangehrmcsrf",
                "csrf_token",
            }

            for cookie in cookies:
                if cookie["name"].lower() in nomes_csrf:
                    session.headers["X-CSRF-TOKEN"] = cookie["value"]
                    session.headers["X-CSRF-Token"] = cookie["value"]

            # Usa o mesmo referer do sistema autenticado.
            session.headers["Referer"] = page.url

            print(f"Cookies transferidos para Requests: {len(cookies)}")

        except PlaywrightTimeoutError as erro:
            print(f"URL no momento da falha: {page.url}")
            print(f"Título da página: {page.title()}")
            raise RuntimeError(
                "Não foi possível encontrar os campos de login ou concluir "
                "a autenticação. Confira a URL e a página aberta."
            ) from erro

        finally:
            browser.close()

    return base_url, session


def gerar_employee_id(ids_usados: set[str]) -> str:
    """Gera um ID numérico único dentro desta execução."""
    while True:
        novo_id = str(random.randint(1, 9999))

        if novo_id not in ids_usados:
            ids_usados.add(novo_id)
            return novo_id


def verificar_sessao(session: requests.Session, base_url: str):
    """
    Testa o acesso à API antes de tentar cadastrar funcionários.
    Não considera uma página HTML de login como autenticação válida.
    """
    url = f"{base_url}/web/index.php/api/v2/pim/employees"

    resposta = session.get(
        url,
        params={"limit": 1},
        timeout=30,
        allow_redirects=True,
    )

    if "/auth/login" in resposta.url:
        raise RuntimeError(
            "Requests foi redirecionado para o login. "
            "Os cookies transferidos não autenticaram a sessão."
        )

    if resposta.status_code in (401, 403):
        raise RuntimeError(
            f"Requests não está autenticado: HTTP {resposta.status_code}. "
            "Pode ser necessário transferir um token CSRF ou outro token."
        )

    if resposta.status_code >= 400:
        raise RuntimeError(
            f"Erro ao testar a API: HTTP {resposta.status_code}. "
            f"Resposta: {resposta.text[:400]}"
        )

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise RuntimeError(
            "O endpoint de teste não retornou JSON. "
            "Confira a URL e a autenticação."
        ) from erro

    if not isinstance(dados, dict):
        raise RuntimeError("A API retornou um formato inesperado.")

    print("A API respondeu em JSON; teste inicial concluído.")


def cadastrar_funcionario(
    session: requests.Session,
    base_url: str,
    funcionario: dict,
    ids_usados: set[str],
) -> dict:
    """Cadastra um funcionário via HTTP, sem navegar pelo PIM."""
    nome = str(funcionario.get("firstName", "")).strip()
    nome_meio = str(funcionario.get("middleName", "")).strip()
    sobrenome = str(funcionario.get("lastName", "")).strip()
    employee_id = str(funcionario.get("employeeId", "")).strip()

    if not nome or not sobrenome:
        return {
            "Nome": nome,
            "Sobrenome": sobrenome,
            "Status": "ERRO",
            "Mensagem": "Nome e sobrenome são obrigatórios.",
        }

    if not employee_id:
        employee_id = gerar_employee_id(ids_usados)
    else:
        ids_usados.add(employee_id)

    payload = {
        "firstName": nome,
        "middleName": nome_meio,
        "lastName": sobrenome,
        "employeeId": employee_id,
    }

    url = f"{base_url}/web/index.php/api/v2/pim/employees"

    try:
        resposta = session.post(
            url,
            json=payload,
            timeout=30,
        )

        try:
            dados = resposta.json()
        except ValueError:
            dados = {}

        if resposta.status_code in (200, 201):
            # Uma resposta HTTP de sucesso deve conter dados válidos.
            if isinstance(dados, dict) and dados.get("data") is not None:
                return {
                    "Nome": nome,
                    "Sobrenome": sobrenome,
                    "Employee ID": employee_id,
                    "Status": "SUCESSO",
                    "Mensagem": str(dados.get("data")),
                }

        return {
            "Nome": nome,
            "Sobrenome": sobrenome,
            "Employee ID": employee_id,
            "Status": "ERRO",
            "Mensagem": (
                f"HTTP {resposta.status_code}: {resposta.text[:500]}"
            ),
        }

    except requests.RequestException as erro:
        return {
            "Nome": nome,
            "Sobrenome": sobrenome,
            "Employee ID": employee_id,
            "Status": "ERRO",
            "Mensagem": str(erro),
        }


def salvar_relatorio(resultados: list[dict], idt: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = REPORT_DIR / f"relatorio_{idt}_{timestamp}.xlsx"

    pd.DataFrame(resultados).to_excel(caminho, index=False)
    return caminho


def executar(idt: str):
    funcionarios = ler_funcionarios()

    if not funcionarios:
        print("Nenhum funcionário encontrado.")
        return

    base_url, session = fazer_login_com_playwright()
    resultados = []

    try:
        verificar_sessao(session, base_url)

        ids_usados = {
            str(f.get("employeeId", "")).strip()
            for f in funcionarios
            if str(f.get("employeeId", "")).strip()
        }

        for indice, funcionario in enumerate(funcionarios, start=1):
            nome = funcionario.get("firstName", "")
            sobrenome = funcionario.get("lastName", "")

            print(
                f"[{indice}/{len(funcionarios)}] "
                f"Enviando cadastro de {nome} {sobrenome} via Requests..."
            )

            resultado = cadastrar_funcionario(
                session,
                base_url,
                funcionario,
                ids_usados,
            )
            resultados.append(resultado)

            print(
                f"Resultado: {resultado['Status']} — "
                f"{resultado['Mensagem']}"
            )

    finally:
        session.close()

    caminho = salvar_relatorio(resultados, idt)
    print(f"\nRelatório salvo em: {caminho}")


class Robot:
    def start(self, arguments):
        executar(str(arguments.idt))
