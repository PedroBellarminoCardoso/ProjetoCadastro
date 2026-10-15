
# Projeto de Automação de Cadastro

Projeto desenvolvido com o objetivo de praticar e aprofundar conhecimentos em automação web utilizando Python, Requests, Playwright, BeautifulSoup (BS4) e Pandas.

## Sobre o projeto

A aplicação automatiza o processo de cadastro de funcionários no sistema de demonstração [OrangeHRM](https://opensource-demo.orangehrmlive.com/web/index.php/auth/login), utilizando como fonte de dados uma planilha Excel.

O projeto combina a automação de navegador com requisições HTTP para tornar o processo de cadastro mais eficiente, reduzindo a necessidade de interações manuais com a interface do sistema.

## Tecnologias utilizadas

- **Python:** linguagem principal utilizada no desenvolvimento da automação.
- **Playwright:** utilizado para automatizar o navegador e realizar o login no sistema.
- **Requests:** utilizado para enviar requisições HTTP por meio de uma sessão autenticada.
- **BeautifulSoup (BS4):** utilizado para analisar o HTML e auxiliar na extração de informações das páginas.
- **Pandas:** utilizado para ler e processar os dados dos funcionários armazenados em uma planilha Excel.
- **Poetry:** utilizado para gerenciar as dependências e executar o projeto.

## Funcionamento

O processo de automação segue as seguintes etapas:

1. **Leitura dos dados:** o Pandas carrega os dados dos funcionários a partir de uma planilha Excel.
2. **Autenticação:** o Playwright acessa o OrangeHRM e realiza o login no sistema.
3. **Sessão autenticada:** o Requests utiliza uma sessão HTTP configurada para realizar requisições autenticadas.
4. **Processamento dos cadastros:** os dados dos funcionários são enviados ao sistema por meio de requisições HTTP.
5. **Execução automatizada:** o processo é executado a partir do terminal, utilizando o comando configurado no Poetry.

## Como executar

### Pré-requisitos

- Python na versão `>=3.12,<3.13`
- Poetry instalado
- Git instalado

### Instalação

Clone o repositório:

```bash
git clone https://github.com/PedroBellarminoCardoso/ProjetoCadastro.git
```

Acesse a pasta do projeto:

```bash
cd ProjetoCadastro
```

Instale as dependências:

```bash
poetry install
```

### Execução

Execute a automação pelo terminal:

```bash
poetry run main -idt
```

> **Observação:** o comando depende da configuração do ponto de entrada `main` no arquivo `pyproject.toml`.

## Objetivo de aprendizado

Este projeto tem finalidade educacional e busca desenvolver conhecimentos práticos em:

- Automação de processos web.
- Integração entre Playwright e Requests.
- Manipulação de sessões HTTP e autenticação.
- Leitura e processamento de planilhas Excel.
- Extração e análise de conteúdo HTML.
- Organização de projetos Python e gerenciamento de dependências com Poetry.

## Aviso

Este projeto utiliza o ambiente de demonstração do OrangeHRM e foi desenvolvido para fins de estudo e testes de automação.
