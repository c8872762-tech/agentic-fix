"""Web UI: FastAPI server with HTML frontend."""
from __future__ import annotations
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.agents import order_manager, product_ranker, product_searcher, spec_extractor, vision_analyst
from src.intake.photo import validate_and_store
from src.models.schemas import PipelineResult, Session, SessionStatus
from src.storage.store import list_sessions, load_result, save_result
from src.utils.config import STATIC_DIR

app = FastAPI(title="Home Fix Agent")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC_DIR / "index.html").read_text()


@app.post("/analyze")
async def analyze(photo: UploadFile = File(...), description: str = Form("")):
    """Run the full pipeline on an uploaded photo."""
    # Save upload to temp file
    suffix = Path(photo.filename or "photo.jpg").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(photo.file, tmp)
        tmp_path = tmp.name

    session = Session(description=description)
    sid = session.session_id
    result = PipelineResult(session=session)

    try:
        stored = validate_and_store(tmp_path, sid)
        session.photo_path = stored
    except (FileNotFoundError, ValueError) as e:
        result.error = str(e)
        return JSONResponse(result.model_dump(mode="json"))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Vision analysis
    analysis = vision_analyst.analyze(stored, sid, description)
    result.analysis = analysis
    if analysis.confidence == 0.0:
        result.error = analysis.description or "Photo analysis failed. Try a clearer photo."
        save_result(result)
        return JSONResponse(result.model_dump(mode="json"))

    # Spec extraction
    spec = spec_extractor.extract(analysis, stored)
    result.spec = spec

    # Product search + rank
    products = product_searcher.search(spec)
    if not products:
        result.error = "No products found."
        save_result(result)
        return JSONResponse(result.model_dump(mode="json"))

    result.products = product_ranker.rank(products, spec)[:5]
    session.status = SessionStatus.COMPLETED
    save_result(result)
    return JSONResponse(result.model_dump(mode="json"))


@app.post("/order")
async def place_order(session_id: str = Form(...), product_index: int = Form(...)):
    """Place an order for a selected product."""
    r = load_result(session_id)
    if not r or product_index < 0 or product_index >= len(r.products):
        return JSONResponse({"error": "Invalid session or product"}, status_code=400)

    product = r.products[product_index]
    order = order_manager.create_order(session_id, product)
    order = order_manager.confirm_order(order)
    r.order = order
    save_result(r)
    return JSONResponse(order.model_dump(mode="json"))


@app.get("/history")
async def history():
    return JSONResponse(list_sessions())


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    r = load_result(session_id)
    if not r:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse(r.model_dump(mode="json"))


def start_server():
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting web UI at http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
