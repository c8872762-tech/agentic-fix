"""Unit tests for the home fix agent."""
import json
import tempfile
from pathlib import Path

import pytest

from src.models.schemas import (
    IssueAnalysis, OrderRecord, OrderStatus, PipelineResult,
    ProductResult, ProductSpec, Session, SessionStatus,
)
from src.agents.product_ranker import rank, _normalize
from src.agents.order_manager import create_order, confirm_order, cancel_order
from src.intake.photo import validate_and_store, ALLOWED_EXTENSIONS

FIXTURES = Path(__file__).parent.parent / "fixtures"


# --- Schema tests ---

class TestSchemas:
    def test_session_defaults(self):
        s = Session()
        assert s.session_id
        assert s.status == SessionStatus.ACTIVE

    def test_issue_analysis(self):
        a = IssueAnalysis(item_category="bulb", problem_type="burned_out", confidence=0.9)
        assert a.analysis_id
        assert a.visible_text == []

    def test_product_spec(self):
        s = ProductSpec(item_category="bulb", attributes={"base_type": "E26"}, search_query="E26 bulb")
        assert s.spec_id
        assert s.attributes["base_type"] == "E26"

    def test_pipeline_result(self):
        r = PipelineResult(session=Session())
        assert r.analysis is None
        assert r.products == []


# --- Photo intake tests ---

class TestPhotoIntake:
    def test_rejects_missing_file(self):
        with pytest.raises(FileNotFoundError):
            validate_and_store("/nonexistent/photo.jpg", "test_session")

    def test_rejects_bad_format(self):
        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as f:
            f.write(b"fake")
            f.flush()
            with pytest.raises(ValueError, match="Unsupported format"):
                validate_and_store(f.name, "test_session")
            Path(f.name).unlink()

    def test_rejects_oversized(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"x" * (21 * 1024 * 1024))
            f.flush()
            with pytest.raises(ValueError, match="too large"):
                validate_and_store(f.name, "test_session")
            Path(f.name).unlink()

    def test_accepts_valid_jpg(self, tmp_path):
        photo = tmp_path / "test.jpg"
        photo.write_bytes(b"\xff\xd8\xff" + b"x" * 100)
        result = validate_and_store(str(photo), "test_intake")
        assert Path(result).exists()
        assert result.endswith(".jpg")


# --- Ranking tests ---

class TestRanking:
    def _make_products(self) -> list[ProductResult]:
        return [
            ProductResult(title="Philips LED A19 60W 2700K", price_cents=897, rating=4.7, review_count=12000, availability="in_stock"),
            ProductResult(title="Cheap Bulb", price_cents=199, rating=3.5, review_count=100, availability="in_stock"),
            ProductResult(title="Premium LED A19 60W 2700K Dimmable", price_cents=1299, rating=4.9, review_count=5000, availability="in_stock"),
        ]

    def test_normalize(self):
        assert _normalize([1, 2, 3]) == [0.0, 0.5, 1.0]
        assert _normalize([1, 2, 3], invert=True) == [1.0, 0.5, 0.0]
        assert _normalize([5, 5, 5]) == [1.0, 1.0, 1.0]

    def test_rank_deterministic(self):
        products = self._make_products()
        spec = ProductSpec(item_category="bulb", search_query="LED A19 60W 2700K")
        r1 = rank(products[:], spec)
        r2 = rank(products[:], spec)
        assert [p.result_id for p in r1] == [p.result_id for p in r2]

    def test_rank_spec_match_matters(self):
        products = self._make_products()
        spec = ProductSpec(item_category="bulb", search_query="LED A19 60W 2700K")
        ranked = rank(products, spec)
        # "Cheap Bulb" has no spec terms in title, should rank last
        assert ranked[-1].title == "Cheap Bulb"

    def test_rank_assigns_ranks(self):
        products = self._make_products()
        spec = ProductSpec(item_category="bulb", search_query="LED A19 60W 2700K")
        ranked = rank(products, spec)
        assert [p.rank for p in ranked] == [1, 2, 3]


# --- Order manager tests ---

class TestOrderManager:
    def test_create_order(self):
        p = ProductResult(title="Test Bulb", price_cents=500)
        order = create_order("sess1", p)
        assert order.status == OrderStatus.PENDING
        assert order.total_price_cents == 500

    def test_confirm_order(self):
        p = ProductResult(title="Test Bulb", price_cents=500)
        order = create_order("sess1", p)
        confirmed = confirm_order(order)
        assert confirmed.status == OrderStatus.PLACED
        assert confirmed.retailer_order_id.startswith("MOCK-")
        assert confirmed.confirmed_at is not None

    def test_cancel_order(self):
        p = ProductResult(title="Test Bulb", price_cents=500)
        order = create_order("sess1", p)
        cancelled = cancel_order(order)
        assert cancelled.status == OrderStatus.CANCELLED

    def test_quantity(self):
        p = ProductResult(title="Test Bulb", price_cents=500)
        order = create_order("sess1", p, quantity=3)
        assert order.total_price_cents == 1500


# --- Mock search tests ---

class TestMockSearch:
    def test_mock_fixture_loads(self):
        from src.agents.product_searcher import _MOCK_FILE
        data = json.loads(_MOCK_FILE.read_text())
        assert "bulb" in data
        assert len(data["bulb"]) >= 3

    def test_mock_search_returns_products(self):
        from src.agents.product_searcher import _search_mock
        results = _search_mock("LED bulb E26")
        assert len(results) >= 3
        assert all(isinstance(r, ProductResult) for r in results)
