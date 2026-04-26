.PHONY: install test run lint format clean docker-build docker-up docker-down

# Ambiente Python
PYTHON := python
PIP := pip

# Instalar dependências
install:
	$(PIP) install -r requirements.txt

# Rodar testes
test:
	pytest tests/ -v

# Rodar testes com cobertura
test-cov:
	pytest tests/ -v --cov=app --cov-report=term-missing

# Iniciar servidor de desenvolvimento
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificar formatação e lint (requer ruff/black opcional)
lint:
	ruff check app/ tests/ || echo "ruff não instalado"
	black --check app/ tests/ || echo "black não instalado"

# Formatar código (requer ruff/black opcional)
format:
	ruff format app/ tests/ || echo "ruff não instalado"
	black app/ tests/ || echo "black não instalado"

# Limpar cache e arquivos temporários
clean:
	rmdir /s /q __pycache__ 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q .coverage 2>nul || true
	for /d /r . %%d in (__pycache__) do @rmdir /s /q "%%d" 2>nul || true

# Docker
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

# Teste rápido com curl
curl-test:
	curl -X POST http://localhost:8000/messages \
		-H "Content-Type: application/json" \
		-d '{"message":"O que é composição?"}'

