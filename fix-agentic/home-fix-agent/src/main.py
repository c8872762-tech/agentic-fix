"""CLI pipeline runner for the home fix agent."""
from __future__ import annotations
import argparse
import logging
import sys

from src.agents import vision_analyst, spec_extractor, product_searcher, product_ranker, order_manager
from src.intake.photo import validate_and_store
from src.models.schemas import PipelineResult, Session, SessionStatus
from src.storage.store import list_sessions, load_result, save_result

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(photo_path: str, description: str = "") -> PipelineResult:
    """Execute the full analysis pipeline. Returns PipelineResult."""
    session = Session(description=description)
    sid = session.session_id
    result = PipelineResult(session=session)

    # 1. Photo intake
    try:
        stored = validate_and_store(photo_path, sid)
        session.photo_path = stored
    except (FileNotFoundError, ValueError) as e:
        result.error = str(e)
        save_result(result)
        return result

    # 2. Vision analysis
    logger.info("Analyzing photo...")
    analysis = vision_analyst.analyze(stored, sid, description)
    result.analysis = analysis
    if analysis.confidence == 0.0:
        result.error = analysis.description or "Photo analysis failed. Try a clearer photo."
        save_result(result)
        return result

    # 3. Spec extraction
    logger.info("Extracting specs...")
    spec = spec_extractor.extract(analysis, stored)
    result.spec = spec

    # 4. Product search
    logger.info("Searching products...")
    products = product_searcher.search(spec)
    if not products:
        result.error = "No products found. Try a different description."
        save_result(result)
        return result

    # 5. Rank
    ranked = product_ranker.rank(products, spec)
    result.products = ranked[:5]

    session.status = SessionStatus.COMPLETED
    save_result(result)
    return result


def _print_result(result: PipelineResult):
    """Pretty-print pipeline result to terminal."""
    if result.error:
        print(f"\n❌ Error: {result.error}")
        return

    a = result.analysis
    if a:
        print(f"\n📋 Issue: {a.item_category} — {a.problem_type} (confidence: {a.confidence:.0%})")
        print(f"   {a.description}")
        if a.visible_text:
            print(f"   Visible text: {', '.join(a.visible_text)}")

    s = result.spec
    if s:
        print(f"\n🔧 Specs: {s.search_query}")
        for k, v in s.attributes.items():
            conf = s.confidence_per_field.get(k, 0)
            print(f"   {k}: {v} ({conf:.0%})")
        if s.clarification_questions:
            print(f"   ❓ Questions: {'; '.join(s.clarification_questions)}")

    if result.products:
        print(f"\n🛒 Top {len(result.products)} products:")
        for p in result.products:
            price = f"${p.price_cents / 100:.2f}"
            stars = f"⭐{p.rating}" if p.rating else ""
            print(f"   {p.rank}. {p.title}")
            print(f"      {price} | {stars} ({p.review_count} reviews) | Score: {p.match_score:.2f}")
            print(f"      {p.recommendation_reason}")
            if p.url:
                print(f"      {p.url}")


def cli_main():
    parser = argparse.ArgumentParser(description="Home Fix Agent")
    sub = parser.add_subparsers(dest="command")

    analyze_p = sub.add_parser("analyze", help="Analyze a photo and find products")
    analyze_p.add_argument("photo", help="Path to photo")
    analyze_p.add_argument("--description", "-d", default="", help="Optional description")

    sub.add_parser("history", help="List past sessions")

    replay_p = sub.add_parser("replay", help="Replay a past session")
    replay_p.add_argument("session_id", help="Session ID")

    sub.add_parser("web", help="Start web UI")

    args = parser.parse_args()

    if args.command == "analyze":
        result = run_pipeline(args.photo, args.description)
        _print_result(result)
        if result.products:
            print(f"\n💾 Session: {result.session.session_id}")
            try:
                choice = input("\nSelect product (1-5) or 'q' to quit: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(result.products):
                    product = result.products[int(choice) - 1]
                    order = order_manager.create_order(result.session.session_id, product)
                    price = f"${order.total_price_cents / 100:.2f}"
                    print(f"\n📦 Order: {order.product_title}")
                    print(f"   Total: {price}")
                    confirm = input("   Place order? (yes/no): ").strip().lower()
                    if confirm in ("yes", "y"):
                        order = order_manager.confirm_order(order)
                        result.order = order
                        save_result(result)
                        print(f"   ✅ Order placed! ID: {order.retailer_order_id}")
                    else:
                        order = order_manager.cancel_order(order)
                        result.order = order
                        save_result(result)
                        print("   ❌ Order cancelled.")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")

    elif args.command == "history":
        for s in list_sessions():
            print(f"  {s['session_id']}  {s.get('created_at', '')}  {s.get('category', '')}  {s.get('status', '')}")

    elif args.command == "replay":
        r = load_result(args.session_id)
        if r:
            _print_result(r)
        else:
            print(f"Session {args.session_id} not found.")

    elif args.command == "web":
        from src.web import start_server
        start_server()

    else:
        parser.print_help()


if __name__ == "__main__":
    cli_main()
