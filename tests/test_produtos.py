import pytest

# 1. Listar quando vazio
def test_listar_produtos_vazio(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

# 2. Criar e verificar persistência (via payload de retorno)
def test_criar_produto_persistido(client):
    payload = {"nome": "Monitor", "preco": 1200.50}
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome"] == "Monitor"
    assert data["estoque"] == 0 # Default

# 3. Criar e verificar na listagem
def test_criar_produto_aparece_listagem(client):
    client.post("/produtos", json={"nome": "Mouse", "preco": 150.0})
    response = client.get("/produtos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nome"] == "Mouse"

# 4. Buscar produto por id (Sucesso)
def test_buscar_produto_por_id_sucesso(client, produto_existente):
    id_produto = produto_existente["id"]
    response = client.get(f"/produtos/{id_produto}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Teclado Mecânico"

# 5. Buscar produto inexistente (404)
def test_buscar_produto_inexistente(client):
    response = client.get("/produtos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"

# 6. Deletar produto (204)
def test_deletar_produto_sucesso(client, produto_existente):
    id_produto = produto_existente["id"]
    response = client.delete(f"/produtos/{id_produto}")
    assert response.status_code == 204

# 7. Deletar e confirmar remoção com GET
def test_deletar_produto_e_confirmar_remocao(client, produto_existente):
    id_produto = produto_existente["id"]
    client.delete(f"/produtos/{id_produto}")
    response = client.get(f"/produtos/{id_produto}")
    assert response.status_code == 404

# 8. Deletar produto inexistente (404)
def test_deletar_produto_inexistente(client):
    response = client.delete("/produtos/999")
    assert response.status_code == 404

# 9. Teste parametrizado (Erros de validação 422)
@pytest.mark.parametrize("payload, campo_falho", [
    ({"nome": "", "preco": 100}, "nome"),           # Nome vazio
    ({"nome": "Cadeira", "preco": -10}, "preco"),   # Preço negativo
    ({"preco": 100}, "nome"),                       # Faltando nome
    ({"nome": "Cadeira"}, "preco")                  # Faltando preço
])
def test_criar_produto_payload_invalido(client, payload, campo_falho):
    response = client.post("/produtos", json=payload)
    assert response.status_code == 422
    erros = response.json()["detail"]
    assert any(erro["loc"][-1] == campo_falho for erro in erros)

# 10. Validação de Isolamento de Banco
def test_isolamento_banco_parte_1(client, produto_existente):
    # Se o isolamento falhar e esse rodar depois da parte 2, o count estará errado
    response = client.get("/produtos")
    assert len(response.json()) == 1

def test_isolamento_banco_parte_2(client):
    # O banco DEVE estar vazio aqui por causa do drop_all/create_all no fixture client
    response = client.get("/produtos")
    assert len(response.json()) == 0