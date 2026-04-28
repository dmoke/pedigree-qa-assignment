# Pedigree QA Assignment

## Setup

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Install Playwright browsers

```bash
poetry run playwright install
```

## Running the Application

### API Server

```bash
poetry run uvicorn src.pedigree.api.app:app --reload
```

### Web Server

```bash
python -m http.server 5500 --directory src/pedigree/web
```

## Accessing Services

- **API Docs**: http://127.0.0.1:8000/docs
- **Dashboard Index Page**: http://localhost:5500/

## Running Tests

### Individual Data Integrity Tests

```bash
poetry run pytest tests/data-integrity/ -v --ignore=tests/data-integrity/test_integration_all_validations.py
```

### Full Integrity Validation

```bash
poetry run pytest -m full_validation -v --tb=short
```

### Regenerate Test Scenarios

```bash
for config in data/manipulation/configs/*.json; do python data/manipulation/mutate.py --config "$config"; done
```

### API Tests

```bash
poetry run pytest tests/api/ -v
```

### UI Tests

```bash
poetry run pytest tests/ui/ -v
```
#
#### Some settings are controlled via a .env file in the project root:

```env
INTEGRITY_FULL_VALIDATION_DATA_PATH=data/Dogs Pedigree.csv
API_BASE_URL=http://127.0.0.1:8000
UI_BASE_URL=http://localhost:5500
HEADLESS=true
```
