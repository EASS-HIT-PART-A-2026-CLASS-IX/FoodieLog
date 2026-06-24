#!/usr/bin/env bash
# FoodieLog EX3 — local demo script
# Usage: bash scripts/demo.sh

set -euo pipefail

API="http://localhost:8000"

echo ""
echo "=== FoodieLog EX3 Demo ==="
echo ""

# ── 1. Health check ────────────────────────────────────────────────────────────
echo "--- 1. Health check ---"
curl -s "$API/health" | python3 -m json.tool
echo ""

# ── 2. Login + JWT (all restaurant endpoints require auth) ──────────────────────
echo "--- 2. Login and get JWT ---"
TOKEN=$(curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@foodielog.com","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
AUTH="Authorization: Bearer $TOKEN"
echo "Token: ${TOKEN:0:40}..."
echo ""

# ── 3. Seed some restaurants ───────────────────────────────────────────────────
echo "--- 3. Seeding restaurants ---"
for body in \
  '{"name":"Goocha","cuisine":"Seafood","city":"Tel Aviv","rating":4,"status":"Visited"}' \
  '{"name":"Vitrina","cuisine":"Burger","city":"Tel Aviv","rating":5,"status":"Visited","price_level":2}' \
  '{"name":"Pasta Roma","cuisine":"Italian","city":"Haifa","rating":3,"status":"Want to Go","tags":"romantic"}'
do
  curl -s -X POST "$API/restaurants" -H "Content-Type: application/json" -H "$AUTH" -d "$body" | python3 -m json.tool
done
echo ""

# ── 4. Pagination + search + X-Total-Count ─────────────────────────────────────
echo "--- 4. Paginated list (page 1, page_size 2) ---"
curl -si "$API/restaurants?page=1&page_size=2" -H "$AUTH" | grep -E "HTTP|X-Total|ETag|^\["
echo ""
echo "--- 4b. Search 'pasta' ---"
curl -s "$API/restaurants?search=pasta" -H "$AUTH" | python3 -m json.tool
echo ""

# ── 5. ETag — 304 Not Modified ────────────────────────────────────────────────
echo "--- 5. ETag caching ---"
ETAG=$(curl -si "$API/restaurants" -H "$AUTH" | grep -i etag | awk '{print $2}' | tr -d '\r')
echo "ETag: $ETAG"
curl -si "$API/restaurants" -H "$AUTH" -H "If-None-Match: $ETAG" | head -1
echo ""

# ── 6. Rate-limit headers ──────────────────────────────────────────────────────
echo "--- 6. Rate-limit headers ---"
curl -si "$API/restaurants" -H "$AUTH" | grep -i "X-RateLimit" || echo "(rate limiting disabled locally)"
echo ""

# ── 7. Protected DELETE ───────────────────────────────────────────────────────
echo "--- 7. Delete restaurant 1 (auth required) ---"
curl -si -X DELETE "$API/restaurants/1" -H "$AUTH" | head -1
echo ""

echo "--- 7b. Delete without token → 401 ---"
curl -si -X DELETE "$API/restaurants/2" | head -1
echo ""

# ── 8. Async refresh ──────────────────────────────────────────────────────────
echo "--- 8. Async refresh (requires Redis) ---"
echo "Run: uv run python scripts/refresh.py run --limit 3"
echo ""

echo "=== Demo complete ==="
