# API E-commerce - Produtos

API REST para gerenciamento de produtos de um e-commerce, desenvolvida com FastAPI, SQLAlchemy e PostgreSQL, com testes automatizados via Pytest rodando contra banco real em container Docker.

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+
- pip

---

## Instalação das dependências

```bash
pip install -r requirements.txt
```

---

## Instruções para subir o banco de dados via Docker

Execute o comando abaixo para provisionar os bancos de dados em background (desenvolvimento e teste):

```bash
docker-compose up -d
```

Para subir apenas o banco de testes (necessário para rodar os testes):

```bash
docker-compose up -d db_test
```

Aguarde os containers ficarem `healthy`. Você pode verificar com:

```bash
docker-compose ps
```

A saída esperada é:

```
NAME        STATUS
db_dev      running (healthy)
db_test     running (healthy)
```

---

## Comando para executar os testes

```bash
pytest --cov=main -v
```

Para parar no primeiro erro (útil durante o desenvolvimento):

```bash
pytest --cov=main -v -x
```

Para ver as linhas não cobertas:

```bash
pytest --cov=main --cov-report=term-missing -v
```

---

## Saída esperada do Pytest

```
====================== test session starts ======================
platform linux -- Python 3.11.x, pytest-7.4.3, pluggy-1.x.x
rootdir: /seu_repositorio
configfile: pytest.ini

tests/test_produtos.py::test_listar_produtos_vazio PASSED                          [  9%]
tests/test_produtos.py::test_criar_produto_persistido PASSED                       [ 18%]
tests/test_produtos.py::test_criar_produto_aparece_listagem PASSED                 [ 27%]
tests/test_produtos.py::test_buscar_produto_por_id_sucesso PASSED                  [ 36%]
tests/test_produtos.py::test_buscar_produto_inexistente PASSED                     [ 45%]
tests/test_produtos.py::test_deletar_produto_sucesso PASSED                        [ 54%]
tests/test_produtos.py::test_deletar_produto_e_confirmar_remocao PASSED            [ 63%]
tests/test_produtos.py::test_deletar_produto_inexistente PASSED                    [ 72%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload0-nome] PASSED  [ 81%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload1-preco] PASSED [ 81%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload2-nome] PASSED  [ 81%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload3-preco] PASSED [ 81%]
tests/test_produtos.py::test_isolamento_banco_parte_1 PASSED                       [ 90%]
tests/test_produtos.py::test_isolamento_banco_parte_2 PASSED                       [100%]

---------- coverage: platform linux, python 3.11.x ----------
Name      Stmts   Miss  Cover
-----------------------------
main.py      42      2    95%
-----------------------------
TOTAL        42      2    95%

====================== 14 passed in 3.21s ======================
```

---

## Como funciona o isolamento entre testes

O isolamento é garantido pela fixture `client` definida em `conftest.py`, que opera em escopo de função (`scope="function"`), ou seja, é executada do zero para **cada teste individualmente**.

O ciclo de vida da fixture é:

1. **Setup** — antes do teste: `Base.metadata.create_all(bind=engine)` cria todas as tabelas no banco de teste (`ecom_test` na porta 5433) do zero.
2. **Override de dependência** — `app.dependency_overrides[get_db]` substitui a conexão padrão (banco de desenvolvimento) pela sessão apontada para o banco de teste, garantindo que nenhum teste toque o banco de produção/dev.
3. **Execução** — o teste roda com um `TestClient` conectado ao banco de teste isolado.
4. **Teardown** — após o teste: `Base.metadata.drop_all(bind=engine)` destrói todas as tabelas, apagando qualquer dado criado durante o teste.

Isso garante que:
- Cada teste começa com banco **completamente vazio**
- A **ordem de execução** dos testes não interfere nos resultados
- Não há vazamento de estado entre testes

A fixture auxiliar `produto_existente` depende de `client` e cria um produto via `POST /produtos` antes do teste, servindo como dado de entrada para testes que precisam de um produto já existente no banco.