# Questionário Investigativo — Projeto Integrador Full Stack

**Disciplina:** Laboratório de Programação Full Stack  
**Aula:** 13  
**Projeto:** Sistema de Reservas de Laboratórios

> Este documento responde às 24 questões do questionário da atividade e identifica, em cada resposta, os componentes do projeto relacionados ao comportamento explicado. Os caminhos de ficheiros são indicados a partir da raiz do repositório.

## Parte 1 — Inicialização e arquitetura

### 1. Inicialização e comando do servidor

**Evidência relacionada:** [E01.png](../evidencias/E01.png).

O servidor é iniciado, na raiz do projeto e com o ambiente virtual ativo, pelo comando:

```powershell
python -m uvicorn backend.app.main:app --reload
```

O Uvicorn interpreta `backend.app.main` como o módulo Python a importar e `app` como o objeto ASGI definido nesse módulo. Em `backend/app/main.py`, o objeto é criado com `app = FastAPI(...)`. O parâmetro `--reload` reinicia o processo de desenvolvimento quando os ficheiros de código são alterados. Quando o servidor arranca corretamente, o terminal informa que está a servir a aplicação em `http://127.0.0.1:8000`.

### 2. Interface e documentação Swagger

**Evidência relacionada:** [E02.png](../evidencias/E02.png); [E03.png](../evidencias/E03.png).

A interface é aberta em `http://127.0.0.1:8000/` e a documentação interativa em `http://127.0.0.1:8000/docs`. Os dois endereços pertencem à mesma aplicação FastAPI. Em `backend/app/main.py`, a função `abrir_interface` atende a rota `/` e devolve `frontend/index.html`. A rota `/docs` é gerada pela FastAPI a partir das operações e schemas da API. A interface e a documentação, portanto, usam o mesmo host, porta e processo servidor.

### 3. Ciclo de vida e criação da tabela

**Evidência relacionada:** [E01.png](../evidencias/E01.png); [E07.png](../evidencias/E07.png).

Em `backend/app/main.py`, a função assíncrona `lifespan` chama `criar_tabela()` antes da instrução `yield`. A função `criar_tabela`, definida em `backend/app/database.py`, executa `CREATE TABLE IF NOT EXISTS reservas (...)`. O caminho normal do banco é definido por `CAMINHO_BANCO` como `dados/reservas.db`. O comando cria a tabela se ela ainda não existir, mas não apaga a base nem os registos. Assim, reiniciar o servidor não elimina as reservas existentes.

### 4. Fluxo de uma criação

**Evidência relacionada:** [E04.png](../evidencias/E04.png).

O formulário em `frontend/index.html` é ligado ao listener de `submit` em `frontend/app.js`. `dadosDoFormulario()` recolhe os valores e converte a quantidade para número. O listener serializa os dados como JSON e envia `POST /api/reservas` por `fetch`. FastAPI valida o corpo com `ReservaEntrada`, definido em `backend/app/schemas.py`, antes de chamar `criar_reserva` em `backend/app/main.py`. O endpoint delega a operação a `services.criar_reserva`, em `backend/app/services.py`. O serviço chama `existe_conflito`; se não houver conflito, executa um `INSERT` parametrizado através da conexão criada em `backend/app/database.py`. Depois procura novamente o registo para obter todos os campos e o ID. A rota devolve `201 Created` com o JSON da reserva. No frontend, a resposta é tratada por `lerResposta`; a mensagem é atualizada e `listar()` recarrega a tabela e o resumo.

## Parte 2 — Contrato da API

### 5. Contrato do endpoint de criação

**Evidência relacionada:** [E03.png](../evidencias/E03.png); [E04.png](../evidencias/E04.png).

A criação usa `POST /api/reservas`. O corpo é um objeto JSON com `laboratorio`, `data_reserva`, `turno`, `responsavel`, `quantidade_pessoas` e `finalidade`. Uma resposta bem-sucedida contém esses campos e também `id`, e tem o código `201 Created`. O contrato define como o cliente envia a operação, como o servidor interpreta os campos e como representa o resultado. O modelo de entrada está em `ReservaEntrada` e o de saída em `ReservaSaida`, no ficheiro `backend/app/schemas.py`; a rota está em `backend/app/main.py`.

Exemplo de pedido válido:

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

### 6. Criação válida e relação entre frontend e backend

**Evidência relacionada:** [E04.png](../evidencias/E04.png); [E11.png](../evidencias/E11.png).

A captura E04 registra a criação válida pelo Swagger, conforme o procedimento do Guia pessoal — Aula 13 no Windows: o pedido `POST /api/reservas` recebe `201` e devolve o JSON com o ID 1. A interface web usa o mesmo contrato: o listener de `#form-reserva` em `frontend/app.js` chama `dadosDoFormulario()`, serializa os campos com `JSON.stringify` e envia `POST` com `Content-Type: application/json`. A rota `criar_reserva`, em `backend/app/main.py`, recebe os dados validados como `ReservaEntrada`, chama o serviço e devolve a reserva. E11 também mostra uma gravação realizada pelo formulário; E04, porém, é a captura que documenta diretamente o JSON e o status da criação.

### 7. Uso do código `201`

**Evidência relacionada:** [E04.png](../evidencias/E04.png).

A criação devolve `201 Created` porque o pedido originou um novo recurso. A configuração está no decorador da rota em `backend/app/main.py`: `status_code=status.HTTP_201_CREATED`. O teste `test_fluxo_criar_consultar_atualizar_excluir`, em `tests/test_api.py`, verifica que o `POST` devolve `201`. O código `200` indicaria sucesso de forma mais genérica, enquanto `201` comunica especificamente que o recurso foi criado.

### 8. Validação de quantidade e resposta `422`

**Evidência relacionada:** [E05.png](../evidencias/E05.png).

O campo `quantidade_pessoas` em `ReservaEntrada`, `backend/app/schemas.py`, é declarado com `Field(ge=1, le=40)`. O valor zero fica abaixo do mínimo permitido. A captura E05 mostra o `POST` recusado com HTTP `422`; o Swagger apresenta o rótulo “Unprocessable Content” e o detalhe identifica `body.quantidade_pessoas`, o valor `0` e o limite mínimo 1. FastAPI/Pydantic rejeita o corpo antes da regra de negócio criar a reserva. O comportamento está coberto por `test_rejeitar_quantidade_invalida`, em `tests/test_api.py`.

### 9. Identificador inexistente e resposta `404`

**Evidência relacionada:** [E06.png](../evidencias/E06.png).

A função `buscar_reserva`, em `backend/app/services.py`, consulta o banco pelo identificador e devolve `None` quando não encontra uma linha. A rota `consultar_reserva`, em `backend/app/main.py`, verifica esse resultado e lança `HTTPException` com código `404` e detalhe “Reserva não encontrada”. A consulta SQL pertence ao serviço; a decisão de traduzir a ausência para um status HTTP pertence à camada de API. `test_recurso_inexistente`, em `tests/test_api.py`, cobre a consulta de um recurso inexistente.

## Parte 3 — Persistência e regras de negócio

### 10. Persistência após reinício

**Evidência relacionada:** [E07.png](../evidencias/E07.png).

Os registos são escritos no arquivo SQLite definido por `CAMINHO_BANCO` em `backend/app/database.py`, normalmente `dados/reservas.db`. `services.criar_reserva`, em `backend/app/services.py`, executa `INSERT INTO reservas`. O ciclo de vida chama `criar_tabela()` no arranque com `CREATE TABLE IF NOT EXISTS`, sem apagar os dados. Seguindo o passo do guia, a reserva foi criada, o Uvicorn foi encerrado com `Ctrl+C`, iniciado novamente e o ID foi consultado no Swagger. E07 mostra o resultado dessa última consulta: `GET /api/reservas/2` respondeu `200` e devolveu os dados da reserva. A imagem comprova a consulta bem-sucedida; não enquadra o terminal no momento em que o servidor foi parado e reiniciado.

### 11. Conflito de reserva e código `409`

**Evidência relacionada:** [E08a.png](../evidencias/E08a.png); [E08b.png](../evidencias/E08b.png).

A regra considera conflito quando já existe uma reserva com o mesmo laboratório, data e turno. `services.existe_conflito`, em `backend/app/services.py`, executa uma consulta com esses três valores. Se houver correspondência, `services.criar_reserva` lança `ValueError` com uma mensagem iniciada por “Conflito”. A rota `criar_reserva`, em `backend/app/main.py`, intercepta essa exceção e converte-a em `HTTPException` com código `409 Conflict`. `test_rejeitar_conflito`, em `tests/test_api.py`, valida o comportamento HTTP; `test_servico_impede_conflito`, em `tests/test_services.py`, verifica diretamente a regra do serviço.

### 12. Atualização com `PUT`

**Evidência relacionada:** [E09a.png](../evidencias/E09a.png); [E09b.png](../evidencias/E09b.png).

Na interface, `window.editar` coloca os valores da reserva no formulário e o ID no campo oculto `#reserva-id`, em `frontend/app.js`. Quando o utilizador grava, o listener escolhe `PUT /api/reservas/{id}` em vez de `POST`. A rota `atualizar_reserva`, em `backend/app/main.py`, recebe um `ReservaEntrada` e chama `services.atualizar_reserva`. O serviço verifica se a reserva existe, evita conflitos com outros IDs, executa SQL `UPDATE` e volta a procurar o registo. A resposta de sucesso é `200` com a reserva atualizada. O teste CRUD em `tests/test_api.py` confirma a mudança do responsável.

### 13. Exclusão, `204` e consulta subsequente

**Evidência relacionada:** [E10a.png](../evidencias/E10a.png); [E10b.png](../evidencias/E10b.png).

A rota `excluir_reserva`, em `backend/app/main.py`, delega a exclusão a `services.excluir_reserva`. Se nenhuma linha for eliminada, a API devolve `404`; se a exclusão ocorrer, devolve `204 No Content`. Uma resposta `204` não inclui corpo, pois comunica que a operação foi concluída sem enviar uma representação adicional. No frontend, `lerResposta`, em `frontend/app.js`, verifica primeiro se o status é 204 e devolve `null` sem chamar `resposta.json()`. Uma consulta subsequente ao ID eliminado resulta em `404`. O fluxo é verificado pelo teste CRUD de `tests/test_api.py`.

### 14. Filtro por turno

**Evidência relacionada:** [E11.png](../evidencias/E11.png).

O frontend constrói os parâmetros com `URLSearchParams` dentro de `listar()`, em `frontend/app.js`. Um pedido para o turno da noite pode ser `GET /api/reservas?turno=noite`. A rota `listar_reservas`, em `backend/app/main.py`, recebe o parâmetro e encaminha o valor ao serviço. Em `services.listar_reservas`, `backend/app/services.py`, a condição `AND turno = ?` é adicionada à consulta apenas quando há filtro, e o valor é enviado como parâmetro SQL. O filtro de laboratório segue o mesmo princípio com `LIKE ?`. A lista devolvida contém apenas os registos que correspondem aos filtros selecionados.

### 15. Resumo total e distribuição por turno

**Evidência relacionada:** [E11.png](../evidencias/E11.png).

O endpoint `obter_resumo`, em `backend/app/main.py`, chama `services.obter_resumo`, em `backend/app/services.py`. O serviço conta o total e as reservas por turno; `listar()`, em `frontend/app.js`, consulta `/api/reservas/resumo` e apresenta o resultado. Seguindo o guia, deve-se anotar o resumo antes de criar a reserva noturna e conferi-lo depois: o total e a contagem de noite devem aumentar em um. E11 mostra o estado final (`Total: 3 | manhã: 1 | tarde: 0 | noite: 2`), a mensagem “Sucesso: reserva 4 salva” e o filtro noturno. A imagem enviada não mostra o valor anterior; portanto, ela confirma o estado posterior e o filtro, mas não permite calcular visualmente a variação exata antes/depois. `test_filtrar_e_resumir`, em `tests/test_api.py`, verifica o cálculo em dados de teste.

## Parte 4 — Testes automatizados

### 16. Execução da suíte e descoberta dos testes

**Evidência relacionada:** [E12a.png](../evidencias/E12a.png); [E12b.png](../evidencias/E12b.png).

Na captura E12a, `python -m pytest -v` termina com **7 passed, 1 warning in 0.26s**. O aviso exibido é de depreciação relacionado ao `Starlette TestClient`; não houve falha. O arquivo `pytest.ini` define `testpaths = tests`; por convenção, o pytest procura arquivos `test_*.py` e funções cujos nomes começam por `test_`. A execução com cobertura é apresentada separadamente em E12b e discutida na questão 21.

Comandos no PowerShell, a partir da raiz do projeto e com `.venv` ativo:

```powershell
python -m pytest -v
python -m pytest --cov=backend.app --cov-report=term-missing
```

### 17. Arrange, Act e Assert no teste de CRUD

**Evidência relacionada:** [E12a.png](../evidencias/E12a.png).

Em `tests/test_api.py`, a função `test_fluxo_criar_consultar_atualizar_excluir` pode ser lida pelas três etapas:

- **Arrange:** as fixtures `client` e `reserva_valida` preparam a aplicação e os dados iniciais. São definidas em `tests/conftest.py`.
- **Act:** `client.post`, `client.get`, `client.put` e `client.delete` executam as operações CRUD pela interface HTTP simulada.
- **Assert:** as instruções `assert` verificam os códigos de resposta, os campos devolvidos e o resultado final da exclusão.

O ID criado no primeiro pedido é reutilizado nas consultas, atualização e exclusão seguintes, de modo que o teste valida a sequência completa.

### 18. Por que `TestClient` não precisa do Uvicorn

**Evidência relacionada:** [E12a.png](../evidencias/E12a.png).

`TestClient`, importado de `fastapi.testclient`, comunica diretamente com a aplicação ASGI em memória. Assim, `client.post(...)` encaminha o pedido pela aplicação FastAPI, incluindo roteamento, validação, endpoint e serviço, e devolve uma resposta ao teste sem abrir um servidor de rede. A fixture usa `with TestClient(app) as cliente`, que também executa o ciclo de vida da aplicação. Uvicorn é necessário para servir a aplicação a um navegador real, mas não para os testes automatizados com TestClient.

### 19. Banco temporário e isolamento dos testes

**Evidência relacionada:** [E12a.png](../evidencias/E12a.png); [E12b.png](../evidencias/E12b.png).

A fixture `client` em `tests/conftest.py` recebe `tmp_path`, que fornece um diretório temporário, e `monkeypatch`, que substitui `database.CAMINHO_BANCO` pelo caminho de teste. Em seguida abre `TestClient` com um context manager. Assim, os testes usam uma base temporária, enquanto a aplicação normal continua a usar `dados/reservas.db`. E12a e E12b mostram a execução dos testes, mas não mostram a fixture nem comparam o arquivo de produção antes e depois; o isolamento é confirmado pela leitura de `tests/conftest.py` (linhas 7–13).

### 20. Falha controlada de uma asserção e restauração

**Evidência relacionada:** [E12c.png](../evidencias/E12c.png).

Para provocar uma falha controlada, a asserção de criação em `tests/test_api.py` foi alterada temporariamente de `201` para `200`. E12c mostra o teste falhando: o valor obtido foi `201`, diferente do esperado `200` (`assert 201 == 200`). Conforme o guia, depois da captura a asserção deve ser restaurada para `201`, o arquivo de backup removido e a suíte completa executada novamente. A versão do projeto entregue contém a expectativa correta `201` e a validação deste pacote passou com sete testes. E12a foi capturada antes da mudança temporária; portanto, ela não registra visualmente a execução final após a restauração.

### 21. Percentagem de cobertura e oportunidades de teste

**Evidência relacionada:** [E12b.png](../evidencias/E12b.png).

A captura E12b, executada no Windows com Python 3.14, mostra cobertura total de **94%**: 136 instruções e 8 não cobertas. `backend/app/main.py` aparece com 51 instruções, 4 não cobertas e 92%; as linhas listadas são 34, 70–71 e 73. `backend/app/services.py` aparece com 55 instruções, 4 não cobertas e 93%; as linhas listadas são 16–17, 71 e 73. O resumo indica sete testes aprovados e 22 avisos, incluindo um `ResourceWarning` de conexão SQLite não encerrada. Os avisos não reprovam a suíte. Duas oportunidades concretas de ampliar a cobertura são testar o filtro de laboratório (`GET /api/reservas?laboratorio=101`) e tentar atualizar uma reserva para uma combinação já ocupada, esperando `409`.

Duas oportunidades concretas de ampliação, incluindo linhas não executadas, são:

1. As linhas 16–17 de `services.py`: chamar `GET /api/reservas?laboratorio=101` depois de criar uma reserva correspondente (ou testar diretamente `services.listar_reservas(laboratorio="101")`). Isso exercita a montagem do filtro `LIKE` e a passagem do respetivo parâmetro.
2. As linhas 70–71 de `main.py`: criar duas reservas com chaves distintas e tentar atualizar a primeira para a combinação de laboratório, data e turno da segunda. O teste deve esperar `409`, exercitando a conversão da exceção do serviço em resposta HTTP durante `PUT`.

Também é possível testar `GET /` para cobrir a linha 34, que entrega o HTML, e `PUT` de um identificador inexistente para cobrir as linhas de tratamento 404. A linha 73 de `services.py` pode ser coberta pelo teste de conflito durante a atualização. Cobertura mede que linhas foram executadas; não substitui a avaliação da qualidade das asserções.

### 22. Teste da API em comparação com teste do serviço

**Evidência relacionada:** [E12a.png](../evidencias/E12a.png).

`test_rejeitar_conflito`, em `tests/test_api.py`, usa `client.post` e percorre as camadas da API até ao serviço. Verifica o contrato visível ao cliente: resposta HTTP `409` e mensagem de conflito. `test_servico_impede_conflito`, em `tests/test_services.py`, chama diretamente o serviço e verifica a exceção `ValueError`. Este teste isola a regra de negócio, mas não passa pelo endpoint e, por isso, não valida o código HTTP. Os dois testes complementam-se: um protege a regra e o outro a sua tradução para o protocolo HTTP.

## Parte 5 — Síntese do fluxo

### 23. Cadeia completa de uma criação

**Evidência relacionada:** [E04.png](../evidencias/E04.png); [E09a.png](../evidencias/E09a.png); [E09b.png](../evidencias/E09b.png); [E11.png](../evidencias/E11.png).

A cadeia do projeto é:

```text
Evento submit de #form-reserva
→ listener de submit em frontend/app.js
→ fetch POST /api/reservas
→ endpoint criar_reserva em backend/app/main.py
→ validação do modelo ReservaEntrada em backend/app/schemas.py
→ services.criar_reserva e services.existe_conflito
→ INSERT INTO reservas com database.conectar()
→ resposta HTTP 201 com os dados e o ID
→ lerResposta(), mensagem de sucesso e listar() no frontend
```

### 24. Exemplo de defeito, camada, deteção e prevenção

**Evidência relacionada:** [E04.png](../evidencias/E04.png); [E12c.png](../evidencias/E12c.png).

Um defeito possível seria alterar a rota de criação para devolver `200` em vez de `201`. O erro estaria na camada de API, no endpoint `criar_reserva`, em `backend/app/main.py`. E04 registra a criação válida com `201`; E12c demonstra que o teste detecta a divergência quando a expectativa é alterada para `200`. A prevenção está na asserção `criada.status_code == 201` de `test_fluxo_criar_consultar_atualizar_excluir`, em `tests/test_api.py`.

Outro risco de evolução está na função `listar`, em `frontend/app.js`, que usa `innerHTML` para inserir campos da reserva na tabela. Caso a aplicação passe a aceitar dados não confiáveis, deve-se construir os elementos DOM de forma segura ou inserir texto com `textContent`, além de criar testes adequados para impedir a interpretação de conteúdo fornecido pelo utilizador como HTML.

## Referência rápida de ficheiros

| Ficheiro | Responsabilidade principal |
|---|---|
| `backend/app/main.py` | Ciclo de vida, interface inicial, rotas e códigos HTTP |
| `backend/app/schemas.py` | Modelos Pydantic, enums e validação |
| `backend/app/services.py` | CRUD, filtros, conflitos e resumo |
| `backend/app/database.py` | Caminho, conexão SQLite e criação da tabela |
| `frontend/index.html` | Formulário, filtros, resumo e tabela |
| `frontend/app.js` | Eventos, `fetch`, tratamento de resposta e renderização |
| `frontend/style.css` | Estilos e adaptação a ecrãs menores |
| `tests/conftest.py` | Fixtures e banco temporário isolado |
| `tests/test_api.py` | Testes dos contratos e endpoints HTTP |
| `tests/test_services.py` | Testes das regras de negócio isoladas |
