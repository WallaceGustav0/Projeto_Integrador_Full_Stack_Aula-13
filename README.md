# Projeto Integrador Full Stack — Aula 13

Aplicação didática para gestão de reservas de laboratórios, desenvolvida com **FastAPI**, **SQLite**, **HTML**, **CSS** e **JavaScript**. O projeto demonstra o percurso completo de uma operação: da interação na interface até à validação, regra de negócio, persistência e resposta HTTP.

O [questionário investigativo respondido](documentos/Questionario_Investigativo_Resolvido.md) acompanha o projeto e explica cada uma das 24 questões com referências aos ficheiros e funções correspondentes.

## Funcionalidades

- Criar, consultar, editar e excluir reservas.
- Filtrar reservas por laboratório e turno.
- Consultar o total de reservas e a distribuição por turno.
- Validar os dados enviados à API.
- Impedir duas reservas para o mesmo laboratório, data e turno.
- Persistir os dados localmente em SQLite.
- Executar testes automatizados para a API e para as regras de negócio.

## Tecnologias

| Área | Tecnologia |
|---|---|
| Backend e API REST | Python, FastAPI, Pydantic e Uvicorn |
| Persistência | SQLite |
| Interface | HTML, CSS e JavaScript (Fetch API) |
| Testes e cobertura | pytest, TestClient e pytest-cov |

## Estrutura do projeto

```text
.
├── backend/
│   └── app/
│       ├── database.py       # conexão SQLite e criação da tabela
│       ├── main.py           # ciclo de vida da aplicação e rotas HTTP
│       ├── schemas.py        # modelos e validação dos dados
│       └── services.py       # operações CRUD e regras de negócio
├── documentos/
│   ├── 02_Roteiro_de_Evidencias.md
│   └── Questionario_Investigativo_Resolvido.md
├── evidencias/                # capturas numeradas da atividade
├── frontend/
│   ├── app.js                # eventos, pedidos HTTP e atualização da interface
│   ├── index.html            # formulário, filtros e tabela
│   └── style.css             # estilos responsivos
├── tests/
│   ├── conftest.py           # fixtures e banco de teste isolado
│   ├── test_api.py           # testes dos endpoints e do contrato HTTP
│   └── test_services.py      # testes diretos dos serviços
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Como funciona

A aplicação segue uma arquitetura monolítica em camadas. A interface web e a API são servidas pela mesma aplicação FastAPI. A separação por pastas e módulos deixa claras as responsabilidades sem introduzir a complexidade operacional de vários serviços independentes.

O fluxo de criação de uma reserva é:

```text
Formulário HTML
  → listener submit em frontend/app.js
  → Fetch API envia POST /api/reservas com JSON
  → FastAPI valida ReservaEntrada (backend/app/schemas.py)
  → endpoint criar_reserva (backend/app/main.py)
  → serviço verifica conflito e aplica a regra de negócio
  → SQLite grava com INSERT parametrizado
  → API responde 201 Created com os dados e o identificador
  → interface atualiza mensagem, lista e resumo
```

As rotas HTTP ficam em `backend/app/main.py`; os modelos e as regras de validação, em `schemas.py`; as operações de negócio, em `services.py`; e a conexão/tabela SQLite, em `database.py`. No frontend, `app.js` coordena os pedidos `fetch` e atualiza a página.

## Requisitos

- Windows 10 ou Windows 11.
- Python 3.10 ou superior, disponível pelo comando `py`.
- PowerShell.
- Um navegador atualizado, como Microsoft Edge ou Google Chrome.

## Instalação e execução no Windows

Descarregue ou clone este repositório e abra uma janela do PowerShell na pasta que contém `README.md`. Para mudar de pasta, use `cd` seguido do caminho local, por exemplo:

```powershell
cd "C:\caminho\para\projeto-integrador-full-stack-aula13"
```

Confirme que o Python está instalado e crie um ambiente virtual para manter as dependências deste projeto separadas das restantes instalações Python:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências listadas em `requirements.txt`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se a ativação for bloqueada pela política de execução do PowerShell, permita scripts apenas para a janela atual e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

O prefixo `(.venv)` no início da linha do PowerShell indica que o ambiente está ativo. Para iniciar a aplicação:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Mantenha o terminal aberto enquanto utiliza o sistema. Abra estes endereços no navegador:

- **Aplicação:** `http://127.0.0.1:8000/`
- **Documentação interativa da API (Swagger):** `http://127.0.0.1:8000/docs`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/openapi.json`

Para parar o servidor, volte ao PowerShell onde o Uvicorn está a correr e prima `Ctrl+C`.

## API REST

| Método | Caminho | Descrição | Respostas relevantes |
|---|---|---|---|
| `GET` | `/api/reservas` | Lista reservas; aceita filtros `laboratorio` e `turno` | `200` |
| `GET` | `/api/reservas/resumo` | Devolve total e contagem por turno | `200` |
| `GET` | `/api/reservas/{reserva_id}` | Consulta uma reserva pelo identificador | `200`, `404` |
| `POST` | `/api/reservas` | Cria uma reserva | `201`, `409`, `422` |
| `PUT` | `/api/reservas/{reserva_id}` | Atualiza uma reserva existente | `200`, `404`, `409`, `422` |
| `DELETE` | `/api/reservas/{reserva_id}` | Exclui uma reserva | `204`, `404` |

Exemplo de corpo JSON para criar uma reserva:

```json
{
  "laboratorio": "Laboratório 101",
  "data_reserva": "2026-11-10",
  "turno": "manha",
  "responsavel": "Grupo de Integração",
  "quantidade_pessoas": 20,
  "finalidade": "Aula prática de integração"
}
```

A data usa o formato `AAAA-MM-DD`. Os turnos aceites são `manha`, `tarde` e `noite`. A quantidade de pessoas tem de estar entre 1 e 40. O modelo Pydantic valida ainda os comprimentos dos campos de texto e remove espaços externos de laboratório, responsável e finalidade.

O código `201 Created` indica criação bem-sucedida; `409 Conflict` indica que já existe uma reserva com a mesma combinação de laboratório, data e turno; `422 Unprocessable Entity` indica falha de validação; `404 Not Found` identifica uma reserva inexistente; e `204 No Content` confirma a exclusão sem devolver corpo.

## Persistência e dados

A base SQLite é criada automaticamente durante o arranque da aplicação. O caminho é `dados/reservas.db`, e a tabela é criada com `CREATE TABLE IF NOT EXISTS`, de modo que um reinício do servidor não apaga os registos existentes. O diretório e o ficheiro surgem na primeira execução.

O ficheiro da base de dados é ignorado pelo Git para evitar publicar dados de execução. Utilize apenas dados de demonstração no repositório. Os testes automatizados usam uma base temporária isolada e não alteram a base normal.

## Testes

Com o ambiente virtual ativo e a partir da raiz do repositório, execute:

```powershell
python -m pytest -v
```

Para executar a suíte e ver a cobertura de código:

```powershell
python -m pytest --cov=backend.app --cov-report=term-missing
```

Na execução Windows incluída no projeto, os sete testes passaram. O relatório apresentou **94%** de cobertura, com **136 instruções** e **8 não cobertas**.

A fixture em `tests/conftest.py` usa `tmp_path` e `monkeypatch` para redirecionar a conexão ao SQLite temporário de cada teste. `TestClient` chama a aplicação ASGI diretamente, pelo que os testes não exigem que um servidor Uvicorn esteja em execução.

## Evidências registradas

As capturas reais estão guardadas em `evidencias/`. A tabela resume o que aparece nelas e a relação com as questões; o [roteiro detalhado](documentos/02_Roteiro_de_Evidencias.md) explica as ações, as funções do código e os testes relacionados.

| Código | Captura(s) | Resultado registrado | Questões |
|---|---|---|---|
| E01 | [E01.png](evidencias/E01.png) | Uvicorn iniciado em `127.0.0.1:8000` | 1 |
| E02 | [E02.png](evidencias/E02.png) | Interface aberta no navegador; lista inicial vazia | 2 |
| E03 | [E03.png](evidencias/E03.png) | Swagger lista as operações da API | 2 e 5 |
| E04 | [E04.png](evidencias/E04.png) | Criação via Swagger: `201`, reserva ID 1 e JSON | 6 e 7 |
| E05 | [E05.png](evidencias/E05.png) | Quantidade zero recusada com `422` | 8 |
| E06 | [E06.png](evidencias/E06.png) | Consulta do ID `999999` responde `404` | 9 |
| E07 | [E07.png](evidencias/E07.png) | Consulta do ID 2 responde `200` após a sequência de reinício do guia | 10 |
| E08 | [E08a.png](evidencias/E08a.png), [E08b.png](evidencias/E08b.png) | Primeira reserva `201`; duplicada `409` | 11 |
| E09 | [E09a.png](evidencias/E09a.png), [E09b.png](evidencias/E09b.png) | `PUT` do ID 2 responde `200` e mostra o responsável atualizado | 12 |
| E10 | [E10a.png](evidencias/E10a.png), [E10b.png](evidencias/E10b.png) | `DELETE` responde `204`; consulta do mesmo ID responde `404` | 13 |
| E11 | [E11.png](evidencias/E11.png) | Filtro `turno=noite`; resumo final: total 3, noite 2 | 14 e 15 |
| E12 | [E12a.png](evidencias/E12a.png), [E12b.png](evidencias/E12b.png), [E12c.png](evidencias/E12c.png) | Sete testes aprovados; cobertura 94%; falha controlada ao esperar `200` em vez de `201` | 16 a 22 |

## Questionário

As respostas às 24 perguntas, com links para as capturas relacionadas, estão em [Questionário Investigativo Resolvido](documentos/Questionario_Investigativo_Resolvido.md).

O documento [02 — Roteiro de evidências](documentos/02_Roteiro_de_Evidencias.md) relaciona os arquivos da pasta `evidencias/` aos itens da atividade, descreve o que aparece em cada captura e indica as funções e os testes relacionados.

## Créditos e contexto

Projeto académico da disciplina **Laboratório de Programação Full Stack**, elaborado a partir do material da Aula 13. O foco é compreender como interface, API, validação, regras de negócio, persistência e testes cooperam numa aplicação Full Stack.
