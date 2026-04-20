# Spec-Driven Development Doc

**Project:** Agentic Home Project Assistant

| Field | Value |
|---|---|
| Status | Draft v1.0 |
| Owner | User / Product + Engineering |
| Last Updated | 2026-04-19 |

---

## 1. Problem Statement

Homeowners frequently encounter small maintenance issues — a broken light bulb, a leaky faucet washer, a cracked outlet cover — but struggle to identify the exact replacement part, find it online, and order it. The process requires domain knowledge (bulb base type, wattage, color temperature) that most people lack.

Build an agentic system that accepts a photo of a home maintenance issue, analyzes the problem using vision AI, identifies the correct replacement product with precise specifications, searches available products on the market, presents options to the user, and — after explicit human confirmation — places the order.

The system is **human-in-the-loop by design**. It never places an order without the user reviewing and approving the product, price, and quantity.

---

## 2. Goals

1. Accept a user-submitted photo of a home maintenance issue.
2. Analyze the photo to identify the problem and the item that needs replacement.
3. Extract product specifications from the image (e.g., bulb type, wattage, base size, dimensions).
4. Search online retailers for matching replacement products.
5. Present a ranked list of product options with price, rating, and compatibility notes.
6. Allow the user to select a product and confirm the order.
7. Place the order on behalf of the user after explicit confirmation.
8. Store interaction history for repeat purchases and audit.

---

## 3. Non-Goals

1. Do not handle complex renovations requiring professional contractors.
2. Do not provide electrical, plumbing, or structural safety advice.
3. Do not store payment credentials directly — delegate to retailer checkout or payment provider.
4. Do not autonomously place orders without human confirmation.
5. Do not diagnose issues that require physical inspection beyond what a photo can show.
6. Do not provide price prediction or deal-timing advice.

---

## 4. Product Scope

### In Scope (v1)

- Photo-based issue identification for common home items (bulbs, batteries, filters, covers, knobs, fasteners)
- Specification extraction from photos (type, size, wattage, color, model number)
- Product search via retailer APIs (Amazon Product Advertising API or similar)
- Product comparison and ranking
- Human confirmation gate before ordering
- Order placement via retailer API
- Conversation history and order history storage

### Out of Scope (v1)

- Video-based analysis
- Multi-step repair instructions or tutorials
- Professional contractor matching
- Smart home device integration
- Price tracking and alerts
- Multi-item project planning (e.g., "remodel my bathroom")
- International shipping or multi-currency support

---

## 5. Target Users

1. **Homeowner** — non-technical person who wants to fix a simple issue without researching part numbers.
2. **Renter** — needs to replace a broken item quickly and correctly to avoid lease issues.
3. **Property manager** — handles multiple units and wants fast, repeatable ordering for common parts.

---

## 6. Operating Principle

The system should behave like a knowledgeable hardware store employee:

- **One agent looks at the photo** and figures out what's wrong.
- **One agent identifies the exact specs** of the item that needs replacement.
- **One agent searches the market** for matching products.
- **One agent ranks and presents options** with clear reasoning.
- **One agent handles the order** only after the human says "yes."

No single agent should both recommend a product and place the order without a human review step in between.

---

## 7. High-Level Workflow

1. User submits a photo and optional text description of the issue.
2. Vision agent analyzes the photo: identifies the item, the problem, and visible specs.
3. Spec extraction agent determines the full product specification (type, size, wattage, base, color temp, etc.).
4. If specs are ambiguous, the system asks the user clarifying questions.
5. Product search agent queries retailer APIs with extracted specs.
6. Ranking agent scores and filters results by relevance, price, rating, and availability.
7. System presents top 3–5 product options to the user with comparison details.
8. User selects a product (or requests more options / refines criteria).
9. System shows order summary: product, quantity, price, shipping, and estimated delivery.
10. User explicitly confirms the order.
11. Order agent places the order via retailer API.
12. System stores the interaction, specs, and order record for history and replay.

---

## 8. Functional Requirements

### FR-1: Photo Intake

The system shall accept photos in JPEG, PNG, and HEIC formats up to 20 MB. It shall accept an optional text description alongside the photo.

**Inputs:** Image file, optional text description.
**Outputs:** Stored image reference, session ID.

### FR-2: Issue Identification

The system shall analyze the photo using a vision model to determine:
- What item is shown (e.g., light bulb, faucet handle, outlet cover)
- What is wrong with it (e.g., broken, burned out, cracked, missing)
- Visible brand, model, or part numbers if readable

**Outputs:** Structured issue record with item category, problem type, and any visible identifiers.

### FR-3: Specification Extraction

The system shall infer or extract product specifications from the photo and context:
- For bulbs: base type (E26, E12, GU10), wattage, color temperature, shape (A19, BR30, PAR38), dimmable
- For batteries: size (AA, AAA, CR2032, 9V), chemistry
- For filters: dimensions, MERV rating, brand compatibility
- For hardware: size, thread type, material, finish

If specifications cannot be fully determined from the photo, the system shall ask the user targeted clarifying questions.

**Outputs:** Structured spec record with all identified parameters and confidence levels.

### FR-4: Product Search

The system shall search one or more retailer APIs using the extracted specifications. It shall return products that match the required specs.

**Inputs:** Structured spec record.
**Outputs:** Raw product list with title, price, rating, availability, URL, and images.

### FR-5: Product Ranking and Presentation

The system shall rank search results by:
- Specification match accuracy
- Customer rating and review count
- Price
- Availability and shipping speed
- Brand reputation

It shall present the top 3–5 options with a brief explanation of why each was selected.

### FR-6: User Selection and Clarification

The system shall allow the user to:
- Select a product from the presented options
- Ask for more options
- Refine search criteria (e.g., "I want LED, not incandescent")
- Ask questions about a specific product

### FR-7: Order Confirmation Gate

Before placing any order, the system shall display:
- Product name and image
- Quantity
- Unit price and total price
- Shipping cost and estimated delivery date
- Retailer name

The user must explicitly confirm (e.g., "Yes, place the order") before the system proceeds.

### FR-8: Order Placement

The system shall place the order via the retailer API using the user's pre-configured account/payment method. It shall return an order confirmation with order ID and tracking information when available.

### FR-9: Interaction History

The system shall store:
- All photos submitted
- Issue analysis results
- Spec extractions
- Search results
- User selections
- Order confirmations
- Timestamps and session IDs

This enables repeat purchases, debugging, and audit.

### FR-10: Error Handling and Fallback

- If the photo is unclear: ask the user for a better photo or additional angles.
- If specs cannot be determined: present what is known and ask the user to fill gaps.
- If no products match: broaden search and explain what was relaxed.
- If order placement fails: report the error and suggest manual purchase with a direct link.

---

## 9. Quality Requirements

### QR-1: Accuracy

Specification extraction must be correct for the primary identifying parameters (e.g., bulb base type, battery size) at least 90% of the time on clear photos.

### QR-2: Latency

Photo analysis through product presentation should complete within 15 seconds for a typical request.

### QR-3: Human-in-the-Loop Safety

No order shall be placed without explicit user confirmation. The confirmation step must be a separate, unambiguous interaction — not a default or auto-proceed.

### QR-4: Auditability

All intermediate outputs (photo analysis, specs, search results, user confirmations) shall be stored with session IDs and timestamps.

### QR-5: Graceful Degradation

If a retailer API is unavailable, the system shall try alternative sources or provide a manual search link. Partial results are better than no results.

### QR-6: Cost Control

Vision and LLM calls shall only run after basic input validation. Redundant API calls for the same specs within a session shall be cached.

### QR-7: Privacy

User photos and order data shall be stored securely. Photos shall not be shared with third parties beyond the vision model provider. Payment credentials shall never be stored by the system — delegate to the retailer.

---

## 10. Agent Architecture

### Agent A: Vision Analyst

**Responsibility:** Analyze the submitted photo to identify the item and the problem.

**Inputs:** Photo (image bytes), optional user text description.

**Outputs:** Structured issue record — item category, problem type, visible identifiers, confidence score.

### Agent B: Spec Extractor

**Responsibility:** Determine the full replacement product specification from the photo analysis and any visible markings.

**Inputs:** Issue record from Agent A, original photo for re-inspection if needed.

**Outputs:** Structured spec record with all relevant parameters (type, size, wattage, base, color, material, etc.) and confidence per field.

**Clarification behavior:** If any critical spec has confidence below threshold, generate a targeted question for the user.

### Agent C: Product Searcher

**Responsibility:** Query retailer APIs with the extracted specs to find matching products.

**Inputs:** Spec record, user preferences (price range, brand preference, Prime-eligible).

**Outputs:** Raw product list with metadata (title, price, rating, review count, availability, URL, image URL, ASIN/SKU).

### Agent D: Product Ranker

**Responsibility:** Score and rank search results, then present the top options with reasoning.

**Inputs:** Raw product list, spec record (for match scoring).

**Outputs:** Ranked product list (top 3–5) with match score, price, rating, and a one-sentence explanation per product.

### Agent E: Order Manager

**Responsibility:** Handle the confirmation flow and place the order.

**Inputs:** User-selected product, quantity, shipping preference.

**Outputs:** Order confirmation gate (summary for user review), then order confirmation (order ID, tracking).

**Rule:** This agent must never proceed to order placement without receiving an explicit "confirm" signal from the user.

---

## 11. Data Model

### 11.1 Session

| Field | Type |
|---|---|
| session_id | string |
| user_id | string |
| created_at | datetime |
| status | enum: active, completed, abandoned |
| photo_ids | string[] |

### 11.2 Photo

| Field | Type |
|---|---|
| photo_id | string |
| session_id | string |
| file_path | string |
| format | string (jpeg, png, heic) |
| size_bytes | int |
| uploaded_at | datetime |

### 11.3 IssueAnalysis

| Field | Type |
|---|---|
| analysis_id | string |
| session_id | string |
| photo_id | string |
| item_category | string (bulb, battery, filter, hardware, faucet, cover, other) |
| problem_type | string (broken, burned_out, cracked, missing, worn, other) |
| visible_brand | string (nullable) |
| visible_model | string (nullable) |
| visible_text | string[] |
| confidence | float 0–1 |
| raw_llm_output | json |

### 11.4 ProductSpec

| Field | Type |
|---|---|
| spec_id | string |
| session_id | string |
| analysis_id | string |
| item_category | string |
| attributes | json (key-value pairs, e.g., {"base_type": "E26", "wattage": 60, "color_temp_k": 2700}) |
| confidence_per_field | json (e.g., {"base_type": 0.95, "wattage": 0.80}) |
| clarification_needed | string[] (fields needing user input) |

### 11.5 ProductResult

| Field | Type |
|---|---|
| result_id | string |
| session_id | string |
| spec_id | string |
| retailer | string |
| title | string |
| price_cents | int |
| currency | string |
| rating | float |
| review_count | int |
| availability | string (in_stock, limited, out_of_stock) |
| url | string |
| image_url | string |
| asin_or_sku | string |
| match_score | float 0–1 |
| rank | int |

### 11.6 OrderRecord

| Field | Type |
|---|---|
| order_id | string |
| session_id | string |
| result_id | string |
| user_id | string |
| product_title | string |
| quantity | int |
| unit_price_cents | int |
| total_price_cents | int |
| shipping_cost_cents | int |
| retailer_order_id | string |
| status | enum: pending_confirmation, confirmed, placed, shipped, delivered, failed |
| confirmed_at | datetime (nullable) |
| placed_at | datetime (nullable) |

---

## 12. Ordering Flow (State Machine)

```
PHOTO_SUBMITTED
    → ANALYZING
        → SPECS_EXTRACTED
            → CLARIFICATION_NEEDED (loop back if user answers)
            → SEARCHING
                → RESULTS_PRESENTED
                    → USER_SELECTED
                        → CONFIRMATION_PENDING
                            → ORDER_PLACED (user confirmed)
                            → CANCELLED (user declined)
                    → REFINE_SEARCH (user wants different options)
        → ANALYSIS_FAILED (ask for better photo)
```

Key invariant: The transition from `CONFIRMATION_PENDING` to `ORDER_PLACED` requires an explicit user confirmation message. The system must not auto-advance this transition.

---

## 13. Suggested Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python | Strong ecosystem for vision/LLM/API work |
| Vision/LLM | OpenAI GPT-4o (vision) or Claude Sonnet | Multimodal, structured JSON output |
| Product Search | Amazon Product Advertising API, or SerpAPI for Google Shopping | Broad catalog, pricing, availability |
| Pipeline | Simple Python runner (batch per session) | Easy to debug, no orchestration overhead for MVP |
| Storage | SQLite (MVP) → Postgres (production) | Zero-config for MVP, easy migration |
| Image Storage | Local filesystem (MVP) → S3 (production) | Simple start |
| UI | CLI (MVP) → Web/chat interface (v2) | Fastest to build |
| API Framework | FastAPI (if web UI needed) | Lightweight, async-friendly |

---

## 14. Prompting / Structured Output Specs

All LLM agents must return strict JSON. Prompts must include the expected schema.

### Vision Analyst Output Schema

```json
{
  "item_category": "string",
  "problem_type": "string",
  "visible_brand": "string | null",
  "visible_model": "string | null",
  "visible_text": ["string"],
  "description": "string",
  "confidence": 0.0
}
```

### Spec Extractor Output Schema

```json
{
  "item_category": "string",
  "attributes": {
    "base_type": "string",
    "wattage": 0,
    "color_temperature_k": 0,
    "shape": "string",
    "dimmable": true,
    "finish": "string"
  },
  "confidence_per_field": {
    "base_type": 0.0,
    "wattage": 0.0
  },
  "clarification_questions": ["string"],
  "search_query": "string"
}
```

### Product Ranker Output Schema

```json
{
  "ranked_products": [
    {
      "result_id": "string",
      "match_score": 0.0,
      "recommendation_reason": "string",
      "warnings": ["string"]
    }
  ]
}
```

---

## 15. Example Scenarios

### Scenario 1: Broken Light Bulb

1. User uploads photo of a burned-out bulb still in the socket.
2. Vision Analyst: "item_category: bulb, problem_type: burned_out, visible_text: ['60W', 'E26']"
3. Spec Extractor: "base_type: E26, wattage: 60, shape: A19, color_temp: 2700K (inferred from warm appearance), dimmable: unknown"
4. System asks: "Is this bulb on a dimmer switch?"
5. User: "No"
6. Product Search returns 12 results for "E26 60W A19 LED bulb 2700K"
7. Ranker presents top 3: best match, best value, best rated.
8. User selects option 2.
9. System shows: "Philips LED A19 60W 2700K, $3.97, arrives Thursday. Place order?"
10. User: "Yes"
11. Order placed. Confirmation shown.

### Scenario 2: Unknown Battery Size

1. User uploads photo of a remote control with battery compartment open.
2. Vision Analyst: "item_category: battery, problem_type: missing, visible_text: ['CR2032']"
3. Spec Extractor: "size: CR2032, chemistry: lithium, voltage: 3V"
4. No clarification needed — specs are clear from visible text.
5. Search, rank, confirm, order.

### Scenario 3: Ambiguous Photo

1. User uploads a blurry photo of a ceiling fixture.
2. Vision Analyst: "item_category: bulb, problem_type: burned_out, confidence: 0.4"
3. System: "I can see this is a ceiling light, but the photo is too blurry to read the bulb specs. Can you take a closer photo of the bulb itself, or tell me the bulb type?"
4. User provides a clearer photo or types "it's a GU10 spot light."
5. Flow continues with higher confidence.

---

## 16. Recommendation Presentation Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔧 Home Fix Assistant — Product Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: Burned-out light bulb (E26, 60W, 2700K, A19)

Option 1 ⭐ Best Match
  Philips LED A19 60W Equivalent 2700K
  $3.97 | ⭐ 4.7 (12,340 reviews) | In Stock
  ✅ Exact spec match | Ships tomorrow
  Why: Matches all specs, top-rated, lowest price.

Option 2 💰 Best Value
  Amazon Basics A19 LED 60W 2700K (4-pack)
  $8.49 ($2.12/bulb) | ⭐ 4.5 (8,200 reviews) | In Stock
  ✅ Exact spec match | Multi-pack value
  Why: Same specs, better per-unit price if you need spares.

Option 3 🏆 Highest Rated
  Cree A19 LED 60W 2700K Dimmable
  $5.49 | ⭐ 4.8 (6,100 reviews) | In Stock
  ✅ Exact spec match | Dimmable (bonus feature)
  Why: Highest rated, dimmable for future flexibility.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply with 1, 2, or 3 to select, or type
"more options" / "I want [criteria]" to refine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 17. MVP Implementation Package

### 17.1 MVP Goal

Build a CLI-based home project assistant that:

1. Accepts a photo of a broken/missing home item.
2. Analyzes the photo to identify the item and problem.
3. Extracts replacement product specifications.
4. Searches for matching products online.
5. Presents ranked options to the user.
6. Confirms with the user before placing an order.
7. Stores all interaction artifacts for replay and debugging.

The MVP is a **single-user CLI tool**. No web UI, no multi-user auth, no real-time streaming.

### 17.2 MVP User Story

As a homeowner, I want to take a photo of a broken item, run a command, and get a list of replacement products I can buy — so that I don't have to figure out part numbers myself.

### 17.3 MVP Scope

**Included:**
- Photo input via CLI (file path)
- Vision analysis via OpenAI GPT-4o or equivalent
- Spec extraction with clarification prompts
- Product search via SerpAPI (Google Shopping) or mock retailer
- Ranked product presentation in terminal
- Order confirmation prompt (y/n)
- Order placement via API (or mock in MVP)
- SQLite storage for sessions, analyses, specs, results, orders
- Replay: view past sessions and their outputs

**Excluded:**
- Web or mobile UI
- Real payment processing (mock order placement in MVP)
- Multi-user accounts
- Image preprocessing or enhancement
- Multi-language support

### 17.4 MVP Success Criteria

The MVP is successful if:
- It correctly identifies the item category in 8/10 test photos.
- It extracts the primary spec (e.g., bulb base type) correctly in 8/10 clear photos.
- It returns at least 3 relevant products for each successful spec extraction.
- The confirmation gate blocks every order until the user types "yes."
- A past session can be replayed and inspected.

### 17.5 MVP Architecture

```
User (CLI)
  │
  ├─ photo path + optional description
  │
  ▼
Pipeline Runner (main.py)
  │
  ├─ 1. Photo Intake ──────────► validate + store image
  ├─ 2. Vision Analyst ────────► LLM vision call → IssueAnalysis
  ├─ 3. Spec Extractor ────────► LLM call → ProductSpec
  │     └─ (clarification loop if needed)
  ├─ 4. Product Searcher ──────► retailer API → ProductResult[]
  ├─ 5. Product Ranker ────────► LLM or heuristic → ranked list
  ├─ 6. Present Options ───────► terminal display
  ├─ 7. User Selection ────────► stdin prompt
  ├─ 8. Confirmation Gate ─────► show summary, require "yes"
  ├─ 9. Order Placement ───────► retailer API (or mock)
  └─ 10. Save Session ─────────► SQLite
```

**Decision:** Use a simple sequential pipeline, not a multi-agent framework. Each "agent" is a Python module with a strict input/output contract. This is easier to debug, test, and replay.

---

## 18. MVP Module Specifications

### Module A: Photo Intake

**Purpose:** Validate and store the user's photo.

**Inputs:** File path from CLI argument.

**Outputs:** Photo record (photo_id, file_path, format, size).

**Acceptance Criteria:**
- Rejects files that are not JPEG/PNG/HEIC.
- Rejects files over 20 MB.
- Copies file to session storage directory.

**Failure Modes:**
- File not found → clear error message.
- Unsupported format → list supported formats.
- File too large → show size limit.

### Module B: Vision Analyst

**Purpose:** Analyze the photo to identify the item and problem.

**Inputs:** Photo file path, optional user description.

**Outputs:** IssueAnalysis record (item_category, problem_type, visible identifiers, confidence).

**Acceptance Criteria:**
- Returns structured JSON matching the IssueAnalysis schema.
- Confidence score reflects actual certainty (blurry photo → low confidence).
- Does not hallucinate text that isn't visible in the photo.

**Prompt Contract:**
- Must describe what it sees, not what it assumes.
- Must flag when the image is unclear.
- Must not recommend products (that's a later agent's job).

### Module C: Spec Extractor

**Purpose:** Determine full replacement product specifications.

**Inputs:** IssueAnalysis record, original photo (for re-inspection).

**Outputs:** ProductSpec record with attributes, confidence per field, and clarification questions.

**Acceptance Criteria:**
- Extracts all critical specs for the item category.
- Generates a search query string suitable for retailer APIs.
- Asks clarification questions when confidence is below 0.7 on a critical field.

**Clarification Behavior:**
- System prints the question to the terminal.
- User types an answer.
- Spec Extractor re-runs with the additional context.
- Maximum 3 clarification rounds, then proceed with best-effort specs.

### Module D: Product Searcher

**Purpose:** Query retailer APIs for matching products.

**Inputs:** ProductSpec (specifically the search_query and key attributes).

**Outputs:** List of ProductResult records.

**Acceptance Criteria:**
- Returns at least 3 results when products exist.
- Handles API rate limits and errors gracefully.
- Caches results within a session to avoid redundant calls.

**MVP Implementation:** Use SerpAPI Google Shopping endpoint, or a mock JSON file for offline testing.

### Module E: Product Ranker

**Purpose:** Score and rank search results by relevance.

**Inputs:** ProductResult list, ProductSpec (for match scoring).

**Outputs:** Ranked list with match_score and recommendation_reason per product.

**Scoring Factors:**
- Spec match (does the product match extracted specs?) — weight 0.40
- Rating (customer rating normalized) — weight 0.20
- Price (lower is better, normalized) — weight 0.20
- Availability (in-stock preferred) — weight 0.10
- Review count (more reviews = more trustworthy) — weight 0.10

**Acceptance Criteria:**
- Ranking is deterministic given the same inputs.
- Top result has the highest spec match unless significantly worse on other factors.

### Module F: Order Manager

**Purpose:** Handle selection, confirmation, and order placement.

**Inputs:** Ranked product list, user selection.

**Outputs:** Order confirmation summary, then OrderRecord after placement.

**Acceptance Criteria:**
- Displays full order summary before asking for confirmation.
- Only proceeds on explicit "yes" / "y" input.
- Any other input (including empty) is treated as "no."
- Stores OrderRecord regardless of outcome (confirmed or cancelled).

---

## 19. MVP Data Contracts

### Session Record

```json
{
  "session_id": "sess_20260419_001",
  "user_id": "default_user",
  "created_at": "2026-04-19T08:30:00Z",
  "status": "completed",
  "photo_path": "data/sessions/sess_20260419_001/photo.jpg"
}
```

### Issue Analysis Output

```json
{
  "analysis_id": "ana_001",
  "session_id": "sess_20260419_001",
  "item_category": "bulb",
  "problem_type": "burned_out",
  "visible_brand": "Philips",
  "visible_model": null,
  "visible_text": ["60W", "E26", "2700K"],
  "description": "A burned-out A19 light bulb in a standard ceiling fixture. The base is E26 screw type. Text on the bulb reads 60W and 2700K.",
  "confidence": 0.92
}
```

### Product Spec Output

```json
{
  "spec_id": "spec_001",
  "session_id": "sess_20260419_001",
  "item_category": "bulb",
  "attributes": {
    "base_type": "E26",
    "wattage_equivalent": 60,
    "color_temperature_k": 2700,
    "shape": "A19",
    "technology": "LED",
    "dimmable": false
  },
  "confidence_per_field": {
    "base_type": 0.95,
    "wattage_equivalent": 0.90,
    "color_temperature_k": 0.85,
    "shape": 0.80,
    "technology": 0.70,
    "dimmable": 0.50
  },
  "clarification_questions": ["Is this bulb on a dimmer switch?"],
  "search_query": "E26 60W equivalent A19 LED bulb 2700K"
}
```

### Order Record

```json
{
  "order_id": "ord_001",
  "session_id": "sess_20260419_001",
  "result_id": "res_003",
  "product_title": "Philips LED A19 60W Equivalent Soft White 2700K",
  "quantity": 1,
  "unit_price_cents": 397,
  "total_price_cents": 397,
  "shipping_cost_cents": 0,
  "retailer_order_id": "114-3941689-8772232",
  "status": "placed",
  "confirmed_at": "2026-04-19T08:32:15Z",
  "placed_at": "2026-04-19T08:32:16Z"
}
```

---

## 20. Suggested Repository Structure

```
home-fix-agent/
  README.md
  pyproject.toml
  .env.example
  configs/
    categories.yaml       # supported item categories and their spec fields
    ranking.yaml          # ranking weights
    retailers.yaml        # API endpoints and keys
  src/
    __init__.py
    main.py               # CLI entry point and pipeline runner
    intake/
      photo.py            # photo validation and storage
    agents/
      vision_analyst.py   # photo analysis via vision LLM
      spec_extractor.py   # spec extraction via LLM
      product_searcher.py # retailer API queries
      product_ranker.py   # scoring and ranking
      order_manager.py    # confirmation and order placement
    models/
      schemas.py          # Pydantic data models
    storage/
      db.py               # SQLite operations
      store.py            # session save/load
    utils/
      config.py           # config loader
      llm.py              # LLM client wrapper
  prompts/
    vision_analyst.md
    spec_extractor.md
  tests/
    unit/
    integration/
    fixtures/
      sample_photos/
      mock_search_results.json
  data/
    sessions/             # per-session storage
```

---

## 21. Supported Item Categories (MVP)

Each category defines which spec fields are required, optional, and their valid values.

### Bulbs

| Field | Required | Example Values |
|---|---|---|
| base_type | yes | E26, E12, GU10, GU5.3, G9, BA15D |
| wattage_equivalent | yes | 40, 60, 75, 100 |
| color_temperature_k | yes | 2700, 3000, 4000, 5000 |
| shape | yes | A19, A21, BR30, PAR38, MR16, candelabra |
| technology | yes | LED, CFL, incandescent, halogen |
| dimmable | optional | true, false |
| finish | optional | clear, frosted |

### Batteries

| Field | Required | Example Values |
|---|---|---|
| size | yes | AA, AAA, C, D, 9V, CR2032, CR2025, CR123A |
| chemistry | optional | alkaline, lithium, NiMH |
| voltage | optional | 1.5, 3.0, 9.0 |
| quantity | optional | 1, 2, 4, 8 |

### Filters (HVAC / Air)

| Field | Required | Example Values |
|---|---|---|
| length_inches | yes | 16, 20, 24 |
| width_inches | yes | 20, 25 |
| depth_inches | yes | 1, 2, 4 |
| merv_rating | optional | 8, 11, 13 |

### Hardware (Fasteners, Knobs, Covers)

| Field | Required | Example Values |
|---|---|---|
| item_type | yes | screw, bolt, nut, outlet_cover, switch_plate, knob |
| size | yes | varies by item_type |
| material | optional | plastic, metal, brass, stainless |
| color_finish | optional | white, ivory, black, brushed_nickel |

---

## 22. MVP Prompt Specifications

### Vision Analyst Prompt

```
You are a home maintenance expert analyzing a photo. Describe exactly what you see:

1. What item is shown? (e.g., light bulb, battery, air filter, faucet, outlet cover)
2. What is wrong with it? (e.g., broken, burned out, cracked, missing, worn)
3. Read any visible text: brand names, model numbers, wattage, voltage, size markings.
4. Describe the physical characteristics: shape, color, size relative to surroundings, base/connector type.

Rules:
- Only report what is VISIBLE in the photo. Do not guess text you cannot read.
- If the image is blurry or unclear, say so and set confidence low.
- Do not recommend products. Only describe what you see.

Return a JSON object with: item_category, problem_type, visible_brand, visible_model, visible_text, description, confidence.
```

### Spec Extractor Prompt

```
You are a product specification expert. Given an issue analysis of a home item, determine the exact replacement product specifications.

Use the visible text, item category, and physical description to infer specs. For a light bulb, determine: base_type, wattage_equivalent, color_temperature_k, shape, technology, dimmable. For a battery, determine: size, chemistry, voltage.

Rules:
- Use visible text as primary evidence (e.g., "60W" on a bulb means 60W equivalent).
- Infer from physical characteristics when text is not visible (e.g., standard US ceiling fixture → likely E26).
- Set confidence per field. If you are guessing, confidence must be below 0.7.
- Generate clarification questions for any critical field with confidence below 0.7.
- Generate a search_query string suitable for searching a shopping site.

Return a JSON object with: item_category, attributes, confidence_per_field, clarification_questions, search_query.
```

---

## 23. MVP Test Plan

### Unit Tests

- Photo validation: rejects bad formats, oversized files, missing files.
- Schema validation: all Pydantic models serialize/deserialize correctly.
- Ranking engine: deterministic scoring given same inputs; higher spec match → higher rank.
- Order confirmation gate: only "yes"/"y" proceeds; everything else blocks.
- Config loader: loads YAML configs without error.

### Integration Tests

- End-to-end pipeline with a fixture photo and mock search results.
- Vision Analyst returns valid JSON matching IssueAnalysis schema.
- Spec Extractor returns valid JSON matching ProductSpec schema.
- Product Searcher handles API errors gracefully (returns empty list, not crash).
- Full session is saved to SQLite and can be reloaded.

### LLM Contract Tests

- Invalid JSON from LLM is retried or repaired.
- Vision Analyst does not recommend products (only describes).
- Spec Extractor generates clarification questions when confidence is low.
- Spec Extractor search_query is non-empty for all supported categories.

### Manual Test Matrix

| Photo | Expected Category | Expected Key Spec | Pass Criteria |
|---|---|---|---|
| Burned-out A19 bulb with visible text | bulb | E26, 60W | Correct base + wattage |
| CR2032 battery in remote | battery | CR2032 | Correct size |
| HVAC filter with size printed | filter | Correct dimensions | Matches printed size |
| Blurry photo of ceiling light | bulb | Low confidence | Asks for better photo |
| Photo of a faucet handle | hardware/other | Identifies item | Does not crash |

---

## 24. MVP Roadmap

### Phase 1: Skeleton (Week 1)

- Repository setup, configs, schemas.
- Pipeline runner with stub modules.
- SQLite storage layer.
- CLI entry point.

### Phase 2: Vision + Specs (Week 2)

- Vision Analyst agent with LLM integration.
- Spec Extractor agent with clarification loop.
- Prompt engineering and testing with sample photos.

### Phase 3: Search + Ranking (Week 3)

- Product Searcher with SerpAPI or mock data.
- Product Ranker with weighted scoring.
- Terminal presentation of ranked results.

### Phase 4: Ordering + Storage (Week 4)

- Order Manager with confirmation gate.
- Mock order placement.
- Full session persistence and replay CLI.

### Phase 5: Polish + Evaluation (Week 5)

- Test with 20+ real photos across categories.
- Measure accuracy metrics.
- Fix failure modes discovered in testing.
- Documentation.

---

## 25. MVP Engineering Tickets

### EPIC 1: Core Platform

- Define Pydantic schemas for all data models.
- Create SQLite database layer (create tables, CRUD operations).
- Build config loader (categories.yaml, ranking.yaml, retailers.yaml).
- Build pipeline runner (main.py) with step orchestration.
- CLI argument parsing (photo path, optional description, replay mode).

### EPIC 2: Photo Intake

- Photo validation (format, size).
- Copy to session directory.
- Store Photo record in database.

### EPIC 3: Vision + Spec Extraction

- Vision Analyst agent: LLM vision call, JSON parsing, retry on bad output.
- Spec Extractor agent: LLM call, confidence scoring, clarification question generation.
- Clarification loop: terminal prompt, re-run extractor with user input.
- Prompt files for both agents.

### EPIC 4: Product Search + Ranking

- Product Searcher: SerpAPI integration (or mock adapter).
- Result normalization: map API response to ProductResult schema.
- Product Ranker: weighted scoring engine.
- Terminal presentation: formatted product comparison display.

### EPIC 5: Order Management

- Order confirmation gate: display summary, require explicit "yes."
- Order placement: retailer API call (or mock).
- OrderRecord storage.
- Order status display.

### EPIC 6: Storage + Replay

- Session save: all artifacts per session to SQLite + filesystem.
- Session list: show past sessions with date, category, status.
- Session replay: load and display a past session's analysis, specs, results, and order.

### EPIC 7: Testing + Quality

- Unit tests for all modules.
- Integration test with fixture photos and mock search.
- LLM contract tests.
- Sample photo fixtures for each supported category.

---

## 26. Acceptance Criteria for MVP Launch

The MVP is launch-ready when:

1. `python -m src.main analyze <photo_path>` produces a ranked product list for a clear photo of a supported item.
2. Each product recommendation includes the spec match reason and price.
3. The confirmation gate blocks order placement until the user explicitly types "yes."
4. All intermediate artifacts (analysis, specs, search results, order) are stored and retrievable.
5. `python -m src.main history` lists past sessions.
6. `python -m src.main replay <session_id>` shows the full pipeline output of a past session.
7. The system handles unclear photos gracefully (asks for better photo or clarification).
8. At least 80% accuracy on primary spec extraction across 10 test photos of supported categories.

---

## 27. Open Questions

1. Which retailer API to use for product search? Amazon PA-API requires an Associates account. SerpAPI is simpler but costs per query. A mock adapter may be sufficient for MVP.
2. Should the system support multiple items per photo (e.g., a photo showing 3 different broken things)?
3. How should payment/shipping be handled? Pre-configured retailer account? OAuth flow? For MVP, mock is acceptable.
4. Should the system learn from past corrections (user says "that's wrong, it's actually GU10")? Useful but out of scope for MVP.
5. What is the acceptable LLM cost per session? Vision calls are more expensive than text-only.
6. Should the system support non-English labels on products (e.g., imported bulbs with Chinese text)?

---

## 28. Appendix: Example End-to-End Session

```
$ python -m src.main analyze photos/broken_bulb.jpg --description "kitchen ceiling light burned out"

🔍 Analyzing photo...

📋 Issue Identified:
   Item: Light bulb (burned out)
   Visible text: "60W", "E26"
   Confidence: 92%

🔧 Specifications Extracted:
   Base: E26 (95% confident)
   Wattage: 60W equivalent (90%)
   Color temp: 2700K (85%)
   Shape: A19 (80%)
   Technology: LED (70%)

❓ Quick question: Is this bulb on a dimmer switch? (yes/no/skip)
> no

🔎 Searching for: E26 60W A19 LED 2700K non-dimmable...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔧 Home Fix Assistant — Product Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1 ⭐ Best Match
  Philips LED A19 60W Equivalent Soft White 2700K (4-pack)
  $8.97 ($2.24/bulb) | ⭐ 4.7 (12,340 reviews) | In Stock
  ✅ Exact spec match

Option 2 💰 Best Value
  Amazon Basics A19 LED 60W 2700K (6-pack)
  $11.49 ($1.92/bulb) | ⭐ 4.5 (8,200 reviews) | In Stock
  ✅ Exact spec match

Option 3 🏆 Highest Rated
  Cree A19 LED 60W 2700K
  $4.97 | ⭐ 4.8 (6,100 reviews) | In Stock
  ✅ Exact spec match

Select option (1-3), or type "more" / "refine": 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦 Order Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Product: Philips LED A19 60W Equivalent Soft White 2700K (4-pack)
  Quantity: 1
  Price: $8.97
  Shipping: FREE (Prime)
  Estimated delivery: Thursday, Apr 23
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Place this order? (yes/no): yes

✅ Order placed! Order ID: 114-3941689-8772232
   Track at: https://www.amazon.com/gp/your-account/order-history

Session saved: sess_20260419_001
```
