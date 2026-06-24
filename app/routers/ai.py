"""AI assistant router — POST /ai/chat.

Builds a context summary of the user's restaurant collection and sends it,
together with the user's question, to Groq (OpenAI-compatible API).
"""
from __future__ import annotations

from collections import Counter
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

import json

from app.config import Settings
from app.database import get_settings, SessionDep
from app.models import ChatRequest, ChatResponse, Recommendation, Restaurant

router = APIRouter(prefix="/ai", tags=["ai"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def require_token(
    token: str = Security(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Any authenticated user may use the assistant (Session 11)."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def _build_context(session: SessionDep) -> str:
    restaurants = list(session.exec(select(Restaurant)).all())
    if not restaurants:
        return "The user has no restaurants saved yet."

    total = len(restaurants)
    visited = sum(1 for r in restaurants if r.status == "Visited")
    want = total - visited
    avg = round(sum(r.rating for r in restaurants) / total, 1)
    cuisines = Counter(r.cuisine for r in restaurants)
    cities = Counter(r.city for r in restaurants)

    lines = [
        "=== USER'S RESTAURANT COLLECTION ===",
        f"Total: {total} | Visited: {visited} | Want to Go: {want} | Avg rating: {avg}/5",
        f"Cuisines: {', '.join(f'{c} ({n})' for c, n in cuisines.most_common())}",
        f"Cities: {', '.join(f'{c} ({n})' for c, n in cities.most_common())}",
        "",
        "=== FULL LIST ===",
    ]
    for r in restaurants:
        lines.append(f"- {r.name} | {r.cuisine} | {r.city} | {r.rating}★ | {r.status}")
    return "\n".join(lines)


_SYSTEM_INSTRUCTION = """You are FoodieLog AI, a friendly and knowledgeable food & restaurant assistant.
You have access to the user's saved restaurant collection (provided as context).
You can answer questions about their collection (counts, ratings, recommendations from their list)
AND general food questions (cuisines, dishes, what to order, dining tips).
Be concise, warm, and practical. Use the user's data when relevant. If they ask about
something not in their list, answer from general knowledge. Keep replies short unless asked for detail."""


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
    _claims: Annotated[dict, Depends(require_token)],
) -> ChatResponse:
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI is not configured. Set FOODIE_GROQ_API_KEY in the environment.",
        )

    from openai import OpenAI

    client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
    context = _build_context(session)
    full_message = f"{context}\n\n=== USER QUESTION ===\n{body.message}"

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": _SYSTEM_INSTRUCTION},
                {"role": "user", "content": full_message},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return ChatResponse(reply=response.choices[0].message.content or "")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI assistant is temporarily unavailable. Please try again.",
        ) from exc


@router.post("/recommend", response_model=Recommendation)
def recommend(
    session: SessionDep,
    settings: Annotated[Settings, Depends(get_settings)],
    _claims: Annotated[dict, Depends(require_token)],
) -> Recommendation:
    """Suggest a brand-new restaurant (not already in the user's list) based on their taste."""
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI is not configured. Set FOODIE_GROQ_API_KEY in the environment.",
        )

    from openai import OpenAI

    client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
    context = _build_context(session)
    prompt = (
        f"{context}\n\n"
        "Recommend ONE real restaurant the user is likely to enjoy but does NOT already have "
        "in their list, ideally in a city they already visit. Respond ONLY with a JSON object "
        'with keys: "name", "cuisine", "city", "reason" (one short sentence). No extra text.'
    )

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": "You are a restaurant recommendation engine. Output strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return Recommendation(
            name=str(data.get("name", "")).strip() or "Unknown",
            cuisine=str(data.get("cuisine", "")).strip() or "Unknown",
            city=str(data.get("city", "")).strip() or "Unknown",
            reason=str(data.get("reason", "")).strip(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate a recommendation. Please try again.",
        ) from exc
