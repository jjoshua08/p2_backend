import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Força o uso do banco de teste
os.environ["DATABASE_URL"] = "postgresql://admin:adminpassword@localhost:5433/ecom_test"

from main import app, Base, get_db

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    # Cria as tabelas do zero antes de cada teste
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
        
    # Destrói tudo no teardown garantindo isolamento total
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def produto_existente(client):
    payload = {"nome": "Teclado Mecânico", "preco": 350.00, "estoque": 10, "ativo": True}
    response = client.post("/produtos", json=payload)
    return response.json()