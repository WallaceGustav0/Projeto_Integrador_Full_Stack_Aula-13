# 02 — Roteiro de evidências

**Projeto:** Sistema de Reservas de Laboratórios — Aula 13  
**Disciplina:** Laboratório de Programação Full Stack

Este roteiro identifica as capturas fornecidas na pasta `evidencias/`, relaciona cada uma ao item da atividade e explica qual parte do projeto confirma o comportamento. Os comentários abaixo descrevem apenas o que é legível nas imagens e no código que acompanha o repositório.

A ordem das ações é: iniciar o servidor, usar a aplicação e o Swagger, executar as operações na sequência, e por fim rodar os testes no PowerShell. Os nomes aqui são os que aparecem nos arquivos enviados; quando o guia permitia dividir uma captura, mantive os sufixos realmente usados, como `E09a` e `E09b`.

## Mapa das capturas

| Código | Arquivo(s) | O que a atividade pede | Questões |
|---|---|---|---|
| E01 | [E01.png](../evidencias/E01.png) | Terminal com o Uvicorn iniciado | 1 |
| E02 | [E02.png](../evidencias/E02.png) | Interface e endereço do navegador | 2 |
| E03 | [E03.png](../evidencias/E03.png) | Swagger com as rotas disponíveis | 2 e 5 |
| E04 | [E04.png](../evidencias/E04.png) | Criação válida, resposta `201` e JSON | 6 e 7 |
| E05 | [E05.png](../evidencias/E05.png) | Validação rejeitada com `422` | 8 |
| E06 | [E06.png](../evidencias/E06.png) | Consulta de ID inexistente com `404` | 9 |
| E07 | [E07.png](../evidencias/E07.png) | Consulta de uma reserva existente após a sequência de reinício | 10 |
| E08 | [E08a.png](../evidencias/E08a.png), [E08b.png](../evidencias/E08b.png) | Primeira tentativa criada e repetição recusada com `409` | 11 |
| E09 | [E09a.png](../evidencias/E09a.png), [E09b.png](../evidencias/E09b.png) | Alteração de uma reserva por `PUT` | 12 |
| E10 | [E10a.png](../evidencias/E10a.png), [E10b.png](../evidencias/E10b.png) | Exclusão `204` e consulta seguinte `404` | 13 |
| E11 | [E11.png](../evidencias/E11.png) | Filtro de turno e resumo da aplicação | 14 e 15 |
| E12 | [E12a.png](../evidencias/E12a.png), [E12b.png](../evidencias/E12b.png), [E12c.png](../evidencias/E12c.png) | Suíte pytest, cobertura e falha controlada do teste | 16 a 22 |

## Descrição e relação entre execução e código

### E01 — Inicialização do servidor

**Ação registrada:** instalação das dependências com `python -m pip install -r requirements.txt` e início do servidor com `python -m uvicorn backend.app.main:app --reload`.

**Resultado que aparece:** o terminal mostra o ambiente virtual ativo, instalação concluída, Uvicorn disponível em `http://127.0.0.1:8000`, conclusão do arranque e pedidos recebidos pela aplicação.

**Relação com o código:** o objeto FastAPI `app` é criado em `backend/app/main.py`. O contexto `lifespan`, nas linhas 14–17, chama `criar_tabela()` antes de a aplicação começar a receber pedidos.

**Teste relacionado:** não há um teste automatizado que inicie um processo Uvicorn separado. Os testes usam `TestClient` em memória. Um teste de integração adicional poderia iniciar o servidor e consultar `/` ou `/docs`; a captura atual regista o arranque manual.

**Legendas:** `E01 — Dependências instaladas e servidor Uvicorn iniciado na porta 8000 (questão 1).`

### E02 — Interface no navegador

**Ação registrada:** abertura da página inicial em `http://127.0.0.1:8000/`.

**Resultado que aparece:** a página “Reservas de Laboratórios”, o formulário de nova reserva, os filtros, a tabela vazia e o resumo inicial com total zero. A barra do navegador mostra o endereço local.

**Relação com o código:** a rota `/`, função `abrir_interface` em `backend/app/main.py` (linhas 32–34), devolve `frontend/index.html`. A estrutura do formulário está em `frontend/index.html`; estilos e comportamento estão em `frontend/style.css` e `frontend/app.js`.

**Teste relacionado:** a suíte enviada não tem um teste específico de `GET /`. Poderia ser acrescentado um teste com `client.get("/")` que confirme status `200` e tipo de conteúdo HTML.

**Legendas:** `E02 — Página inicial carregada no navegador a partir do servidor local (questão 2).`

### E03 — Documentação interativa da API

**Ação registrada:** abertura de `http://127.0.0.1:8000/docs`.

**Resultado que aparece:** o Swagger identifica a “API de Reservas de Laboratórios” e lista as operações de consulta, criação, resumo, atualização e exclusão.

**Relação com o código:** as rotas são declaradas em `backend/app/main.py`; FastAPI utiliza essas declarações e os modelos de `backend/app/schemas.py` para gerar o OpenAPI e a página `/docs`.

**Teste relacionado:** a suíte não verifica especificamente a interface Swagger. Como verificação automatizada complementar, poderia ser consultado `GET /openapi.json` e confirmada a presença de `POST /api/reservas` e das demais operações.

**Legendas:** `E03 — Swagger aberto com as rotas REST disponíveis (questões 2 e 5).`

### E04 — Criação válida com resposta `201`

**Ação registrada:** envio de uma reserva válida para `POST /api/reservas`.

**Resultado que aparece:** a API responde `201` e apresenta um JSON com os dados enviados e `id: 1`. A reserva visível é “Laboratorio Aula 13”, data `2026-11-10`, turno `manha`, responsável “Grupo Demonstracao”, quantidade 20 e finalidade “Aula Pratica Full Stack”.

**Relação com o código:** o endpoint `criar_reserva`, em `backend/app/main.py` (linhas 58–64), declara `201 Created` e encaminha a operação para `services.criar_reserva`. A regra e o `INSERT` estão em `backend/app/services.py` (linhas 46–66); os campos são validados por `ReservaEntrada`, em `backend/app/schemas.py`.

**Teste relacionado:** `test_fluxo_criar_consultar_atualizar_excluir`, em `tests/test_api.py` (linhas 1–4), confirma que a criação devolve `201` e um identificador.

**Legendas:** `E04 — Reserva criada pela API com resposta 201 e identificador 1 (questões 6 e 7).`

### E05 — Validação de quantidade e resposta `422`

**Ação registrada:** envio de um pedido `POST /api/reservas` com `quantidade_pessoas` igual a zero.

**Resultado que aparece:** o servidor responde `422 Unprocessable Content`. O corpo identifica `body.quantidade_pessoas`, mostra entrada `0` e informa que o valor deve ser maior ou igual a 1.

**Relação com o código:** o limite está em `ReservaEntrada.quantidade_pessoas`, em `backend/app/schemas.py` (linha 19), definido com `Field(ge=1, le=40)`. FastAPI/Pydantic rejeita o corpo antes de executar a criação.

**Teste relacionado:** `test_rejeitar_quantidade_invalida`, em `tests/test_api.py` (linhas 27–30), envia o valor zero e espera status `422`.

**Legendas:** `E05 — A API rejeitou quantidade zero com status 422 e indicou o limite mínimo (questão 8).`

### E06 — Identificador inexistente e resposta `404`

**Ação registrada:** consulta `GET /api/reservas/999999`.

**Resultado que aparece:** a API responde `404 Not Found` e o corpo contém `"detail": "Reserva não encontrada"`.

**Relação com o código:** `services.buscar_reserva`, em `backend/app/services.py` (linhas 27–30), faz a procura no banco e devolve `None` quando não encontra linha. A rota `consultar_reserva`, em `backend/app/main.py` (linhas 50–55), converte esse resultado em HTTP `404`.

**Teste relacionado:** `test_recurso_inexistente`, em `tests/test_api.py` (linhas 44–46), verifica que um ID ausente resulta em `404`.

**Legendas:** `E06 — Consulta do identificador 999999 sem correspondência; resposta 404 (questão 9).`

### E07 — Consulta de uma reserva existente

**Ação registrada conforme o guia:** criar uma reserva e anotar o ID, interromper o Uvicorn com `Ctrl+C`, iniciar novamente com `python -m uvicorn backend.app.main:app --reload` e, no Swagger, consultar esse mesmo ID por `GET /api/reservas/{reserva_id}`. Na captura enviada, o ID consultado é 2.

**Resultado que aparece:** a API responde `200` e devolve a reserva de ID 2: laboratório “Laboratorio Aula 14”, data `2026-11-12`, turno `manha`, responsável “Grupo Demonstracao”, quantidade 15 e a finalidade indicada no corpo JSON.

**Relação com o código:** `services.criar_reserva`, em `backend/app/services.py` (linhas 46–66), grava a linha no SQLite. O banco normal é `dados/reservas.db`, definido em `backend/app/database.py` (linha 8); `criar_tabela()` usa `CREATE TABLE IF NOT EXISTS` (linhas 19–35), portanto não apaga os dados existentes ao reiniciar. A consulta passa por `buscar_reserva` e pela rota `consultar_reserva`.

**Limite do que está visível:** esta imagem mostra o pedido GET bem-sucedido e o registo devolvido. Ela não inclui a janela do terminal no momento em que o processo foi encerrado e iniciado de novo; por si só, a captura não mostra a passagem do tempo/reinício. O vínculo com a questão 10 depende de a consulta ter sido feita depois do reinício, como previsto no procedimento.

**Teste relacionado:** os testes usam uma base SQLite temporária via `tmp_path` e `monkeypatch` em `tests/conftest.py`; não há na suíte atual um teste que pare e volte a iniciar um processo Uvicorn para testar a persistência entre processos.

**Legendas:** `E07 — Consulta do ID 2 com resposta 200 e os dados da reserva disponíveis depois da reinicialização (questão 10).`

### E08 — Conflito de reserva

**Ação registrada:** envio duas vezes do mesmo JSON para `POST /api/reservas`, com laboratório “Laboratorio Conflito 17”, data `2026-11-22` e turno `noite`.

**Resultado que aparece:** E08a mostra a primeira criação aceita com `201` e `id: 3`. E08b mostra a repetição da mesma combinação recusada com `409 Conflict` e a mensagem “Conflito: laboratório já reservado nessa data e turno”.

**Relação com o código:** `services.existe_conflito`, em `backend/app/services.py` (linhas 33–44), consulta laboratório, data e turno. `services.criar_reserva` interrompe a criação se a combinação existir (linhas 46–48). A rota em `backend/app/main.py` (linhas 58–64) converte `ValueError` para HTTP `409`.

**Teste relacionado:** `test_rejeitar_conflito`, em `tests/test_api.py` (linhas 20–24), verifica o status e a mensagem. `test_servico_impede_conflito`, em `tests/test_services.py` (linhas 24–27), testa diretamente a regra de negócio.

**Legendas:** `E08a — Primeira reserva da combinação criada com status 201 (questão 11).` / `E08b — Repetição da mesma combinação recusada com status 409 (questão 11).`

### E09 — Atualização da reserva por `PUT`

**Ação registrada:** alteração do responsável da reserva de ID 2 pela interface; pedido `PUT /api/reservas/2`.

**Resultado que aparece:** E09a mostra a interface com a linha do ID 2 atualizada para “Grupo Atualizado”, além do painel Network selecionado na requisição `PUT`, status `200 OK`. E09b mostra o JSON de resposta com `id: 2` e o campo `responsavel` atualizado.

**Relação com o código:** no frontend, o listener do formulário em `frontend/app.js` (linhas 33–43) escolhe `PUT` quando existe ID no campo de edição; `window.editar` preenche esse ID e os campos (linhas 45–50). `atualizar_reserva`, em `backend/app/main.py` (linhas 66–74), encaminha para `services.atualizar_reserva`, que executa o `UPDATE` e lê o registo atualizado (`backend/app/services.py`, linhas 69–90).

**Teste relacionado:** `test_fluxo_criar_consultar_atualizar_excluir`, em `tests/test_api.py` (linhas 10–13), espera `200` e confirma o responsável alterado.

**Legendas:** `E09a — Interface e Network mostram PUT da reserva 2 respondido com 200 (questão 12).` / `E09b — JSON do PUT confirma o responsável atualizado (questão 12).`

### E10 — Exclusão `204` e consulta `404`

**Ação registrada:** E10a envia `DELETE /api/reservas/1`; E10b consulta depois `GET /api/reservas/1`.

**Resultado que aparece:** a exclusão retorna `204` sem corpo; a consulta posterior retorna `404` com “Reserva não encontrada”. Ambas as operações usam o mesmo ID 1.

**Relação com o código:** `excluir_reserva`, em `backend/app/main.py` (linhas 77–81), devolve `Response` com status `204`. A procura subsequente passa por `consultar_reserva`. No frontend, `lerResposta` em `frontend/app.js` (linhas 15–19) reconhece 204 e não tenta interpretar um JSON que não existe.

**Teste relacionado:** `test_fluxo_criar_consultar_atualizar_excluir`, em `tests/test_api.py` (linhas 15–17), verifica `204` e que o mesmo ID passa a devolver `404`.

**Legendas:** `E10a — Exclusão da reserva 1 concluída com status 204 (questão 13).` / `E10b — Consulta posterior do ID 1 devolve 404 (questão 13).`

### E11 — Filtro noturno e resumo

**Ação registrada conforme o guia:** observar o resumo antes da criação, salvar uma nova reserva no turno **Noite**, conferir o resumo depois, selecionar **Noite** no filtro e consultar a chamada na aba **Network/Rede**. A captura enviada reúne o estado final da interface e a requisição filtrada.

**Resultado que aparece:** o painel Network mostra `GET http://127.0.0.1:8000/api/reservas?turno=noite` com status `200`. A tabela apresenta duas reservas noturnas. O resumo mostrado na página é `Total: 3 | manhã: 1 | tarde: 0 | noite: 2`; a interface também exibe a mensagem “Sucesso: reserva 4 salva.”

**Relação com o código:** `listar()` em `frontend/app.js` (linhas 22–30) constrói query parameters com `URLSearchParams`, desenha as linhas e atualiza o resumo. `listar_reservas`, em `backend/app/main.py` (linhas 37–43), passa os filtros ao serviço; `services.listar_reservas`, em `backend/app/services.py` (linhas 12–24), acrescenta os critérios SQL parametrizados. `obter_resumo` (linhas 99–104 de `services.py`) calcula total e contagem por turno.

**Teste relacionado:** `test_filtrar_e_resumir`, em `tests/test_api.py` (linhas 33–41), valida o filtro noturno e o resumo agregado.

**Limite do que está visível:** conforme o procedimento do guia, o resumo é comparado antes e depois da criação. A imagem `E11.png`, porém, mostra somente o estado final — a confirmação “Sucesso: reserva 4 salva”, o resumo com duas reservas noturnas e o filtro; não há uma captura separada do valor anterior. Assim, o roteiro registra o procedimento seguido, mas não apresenta como visível na imagem um número anterior que não aparece nela. O guia previa `E11a.png` e `E11b.png` se fosse preciso dividir o conteúdo; o arquivo enviado foi salvo como `E11.png`.

**Legendas:** `E11 — Filtro Noite devolve apenas reservas desse turno; o resumo final apresenta duas reservas noturnas (questões 14 e 15).`

### E12 — Suíte de testes, cobertura e falha controlada

A tabela original associa E12 às questões 16–22. Os três arquivos mostram partes distintas da execução:

#### E12a — Execução aprovada

**Ação registrada:** `python -m pytest -v`.

**Resultado que aparece:** sete testes com estado `PASSED`; o resumo final indica `7 passed, 1 warning in 0.26s`. A advertência de depreciação de `Starlette TestClient` é exibida, mas não fez a suíte falhar.

**Relação com o código e testes:** `pytest.ini` aponta para a pasta `tests`. O fluxo CRUD está em `tests/test_api.py::test_fluxo_criar_consultar_atualizar_excluir`; a fixture `client` está em `tests/conftest.py`.

**Questões relacionadas:** 16–19 e 22, em conjunto com a leitura dos testes e da fixture. E12a mostra que os testes terminaram aprovados; o código é necessário para explicar Arrange/Act/Assert, `TestClient`, isolamento e a diferença entre teste de API e teste de serviço.

#### E12b — Cobertura

**Ação registrada:** `python -m pytest --cov=backend.app --cov-report=term-missing`.

**Resultado que aparece:** plataforma `win32`, Python 3.14; linha TOTAL com 136 instruções, 8 não cobertas e cobertura de `94%`. A tabela identifica `main.py` com 92% e linhas `34, 70–71, 73`; `services.py` com 93% e linhas `16–17, 71, 73`. O resumo mostra sete testes aprovados e 22 avisos.

**Relação com o código e oportunidades de teste:** `backend/app/main.py` contém a rota de interface, o tratamento de conflitos e o 404 do `PUT`; `backend/app/services.py` contém os filtros opcionais e os retornos de ausência/conflito durante atualização. Um teste para `GET /api/reservas?laboratorio=...` exercitaria as linhas do filtro de laboratório; outro que atualize uma reserva para uma combinação já ocupada exercitaria o conflito no `PUT`.

**Nota:** a saída inclui um aviso `ResourceWarning` referente a conexão SQLite não encerrada, além dos avisos resumidos pelo pytest. O processo termina com sete testes aprovados. O relatório mostra a execução da suíte enviada, não uma garantia de que todos os cenários possíveis foram testados.

#### E12c — Falha intencional da asserção

**Ação registrada:** execução isolada de `tests/test_api.py::test_fluxo_criar_consultar_atualizar_excluir` após mudar temporariamente a expectativa da criação de `201` para `200`.

**Resultado que aparece:** o pytest mostra `assert criada.status_code == 200` e o resultado efetivo `201 Created`, seguido de `AssertionError`, `1 failed`. É a falha deliberada prevista na questão 20.

**Relação com o código e restauração:** a asserção correta está em `tests/test_api.py` (linha 3) e exige `201`. Conforme a sequência do guia, depois de guardar a cópia de segurança e capturar a falha, a expectativa deve voltar a `201`, o ficheiro `.bak` deve ser removido e a suíte completa deve ser executada de novo. O arquivo `test_api.py` entregue está restaurado para `201`, e a validação do pacote atualizado executou os sete testes com sucesso. E12c mostra apenas a falha intencional. Como E12a foi capturada antes dessa alteração, ela não é, por si só, a prova visual da restauração posterior.

**Legendas:** `E12a — Os sete testes da suíte terminaram aprovados (questões 16 a 19 e 22).` / `E12b — Relatório de cobertura: total 94%, 136 instruções e 8 não cobertas (questão 21).` / `E12c — A alteração temporária de 201 para 200 fez o teste falhar; o resultado real permaneceu 201 (questão 20).`
