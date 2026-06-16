import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, Field, ConfigDict

# Configuração do Banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@localhost:5432/ecom_dev")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model SQLAlchemy
class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# Schemas Pydantic
class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome do produto")
    preco: float = Field(..., gt=0, description="Preço deve ser maior que zero")
    estoque: int = 0
    ativo: bool = True

class ProdutoResponse(ProdutoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Dependência do Banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Aplicação
app = FastAPI(title="E-commerce API")

@app.get("/produtos", response_model=list[ProdutoResponse], status_code=status.HTTP_200_OK)
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()

@app.post("/produtos", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos/{id}", response_model=ProdutoResponse, status_code=status.HTTP_200_OK)
def buscar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()