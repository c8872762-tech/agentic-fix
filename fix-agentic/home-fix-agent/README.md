# 🔧 Home Fix Agent

An agentic system that takes a photo of a broken home item, identifies the problem, finds replacement products, and helps you order them.

## Quick Start

```bash
pip install -e ".[dev]"
export OPENAI_API_KEY=your-key-here

# Web UI (recommended for testing)
python -m src.main web
# Open http://localhost:8000

# CLI
python -m src.main analyze path/to/photo.jpg -d "kitchen light burned out"
python -m src.main history
python -m src.main replay <session_id>
```

## How It Works

1. **Upload a photo** of a broken/missing item
2. **Vision Analyst** identifies the item and problem
3. **Spec Extractor** determines replacement specs (bulb type, wattage, etc.)
4. **Product Searcher** finds matching products online
5. **Product Ranker** scores and ranks results
6. **You choose** a product and confirm the order

## Testing Without API Keys

The system uses mock product data when no SERPAPI_KEY is set. You still need an OPENAI_API_KEY for photo analysis.

```bash
pytest tests/
```
