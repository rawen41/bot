from __future__ import annotations

import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import base64
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

from config import supabase_config

_supabase_client: Optional[Client] = None


def get_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not supabase_config.url or not supabase_config.key:
            raise RuntimeError(
                "Supabase credentials are not configured. Set SUPABASE_URL and SUPABASE_KEY.")
        _supabase_client = create_client(supabase_config.url, supabase_config.key)
    return _supabase_client


def init_supabase() -> None:
    """Create necessary tables if they do not exist.

    NOTE: Supabase usually manages schema via SQL migrations, but here we try
    to ensure a minimal schema using RPC or ignore errors if tables exist.
    This is a best-effort helper; you can also create tables manually.
    """

    client = get_client()

    # Users table
    client.table("users").select("id").limit(1).execute()
    # Referrals table
    client.table("referrals").select("id").limit(1).execute()
    # Rewards table
    client.table("rewards").select("id").limit(1).execute()
    # Responses table
    client.table("responses").select("trigger_word").limit(1).execute()
    # Managers table
    client.table("managers").select("tg_id").limit(1).execute()
    # Settings table
    client.table("settings").select("explanation_mode").limit(1).maybe_single().execute()


# Users helpers

def get_or_create_user(tg_id: int, username: Optional[str], referred_by: Optional[int] = None) -> Dict[str, Any]:
    client = get_client()

    existing = client.table("users").select("*").eq("tg_id", tg_id).maybe_single().execute()
    if existing and existing.data:
        user = existing.data
        user["__created__"] = False
        return user

    data = {
        "tg_id": tg_id,
        "username": username,
        "referral_count": 0,
        "referred_by": referred_by,
        "join_date": datetime.utcnow().isoformat(),
    }
    inserted = client.table("users").insert(data).execute()
    user = inserted.data[0]
    user["__created__"] = True
    return user


def increment_referral(referrer_tg_id: int, referred_user_id: int) -> int:
    client = get_client()

    # Check if this referral already exists to prevent duplicates
    existing_ref = (
        client.table("referrals")
        .select("id")
        .eq("user_id", referrer_tg_id)
        .eq("referred_user", referred_user_id)
        .maybe_single()
        .execute()
    )
    if existing_ref and existing_ref.data:
        # Already counted, just return current count
        user_res = (
            client.table("users")
            .select("referral_count")
            .eq("tg_id", referrer_tg_id)
            .maybe_single()
            .execute()
        )
        return user_res.data.get("referral_count", 0) if user_res.data else 0

    user_res = (
        client.table("users")
        .select("id, referral_count")
        .eq("tg_id", referrer_tg_id)
        .maybe_single()
        .execute()
    )
    if not user_res.data:
        return 0

    user_id = user_res.data["id"]
    referral_count = (user_res.data.get("referral_count") or 0) + 1

    client.table("users").update({"referral_count": referral_count}).eq("id", user_id).execute()
    # Store tg_id instead of internal id for easier retrieval
    client.table("referrals").insert({"user_id": referrer_tg_id, "referred_user": referred_user_id}).execute()
    return referral_count


def get_user_referrals(tg_id: int) -> List[Dict[str, Any]]:
    """Get list of users referred by this user with their names."""
    client = get_client()
    # Now we can directly query by tg_id since we store it directly
    res = (
        client.table("referrals")
        .select("referred_user")
        .eq("user_id", tg_id)
        .execute()
    )
    referred_ids = [row["referred_user"] for row in (res.data or [])]
    if not referred_ids:
        return []

    # Fetch user details for referred IDs
    users_res = (
        client.table("users")
        .select("tg_id, username")
        .in_("tg_id", referred_ids)
        .execute()
    )
    return users_res.data or []


def get_user_stats(tg_id: int) -> Optional[Dict[str, Any]]:
    client = get_client()
    res = client.table("users").select("*").eq("tg_id", tg_id).single().execute()
    return res.data


def get_top_referrers(limit: int = 10) -> List[Dict[str, Any]]:
    client = get_client()
    res = (
        client.table("users")
        .select("tg_id, username, referral_count")
        .order("referral_count", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


# Responses helpers

def add_response(trigger_word: str, response_type: str, content: str) -> None:
    client = get_client()
    client.table("responses").insert(
        {
            "trigger_word": trigger_word.lower(),
            "response_type": response_type,
            "content": content,
        }
    ).execute()


def delete_response(trigger_word: str) -> None:
    client = get_client()
    client.table("responses").delete().eq("trigger_word", trigger_word.lower()).execute()


def update_response_content(trigger_word: str, response_type: str, content: str) -> None:
    client = get_client()
    client.table("responses").update(
        {"response_type": response_type, "content": content}
    ).eq("trigger_word", trigger_word.lower()).execute()


def get_response(trigger_word: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    res = (
        client.table("responses")
        .select("*")
        .eq("trigger_word", trigger_word.lower())
        .maybe_single()
        .execute()
    )
    return res.data


# Managers helpers

def add_manager(tg_id: int, added_by: int) -> None:
    client = get_client()
    client.table("managers").insert({"tg_id": tg_id, "added_by": added_by}).execute()


def remove_manager(tg_id: int) -> None:
    client = get_client()
    client.table("managers").delete().eq("tg_id", tg_id).execute()


def is_manager(tg_id: int) -> bool:
    client = get_client()
    res = client.table("managers").select("tg_id").eq("tg_id", tg_id).maybe_single().execute()
    return bool(res.data)


# Settings helpers

def get_explanation_mode() -> bool:
    client = get_client()
    res = client.table("settings").select("explanation_mode").limit(1).maybe_single().execute()
    if res and res.data:
        return bool(res.data.get("explanation_mode", False))
    return False


def set_explanation_mode(enabled: bool) -> None:
    client = get_client()
    res = client.table("settings").select("id, explanation_mode").limit(1).maybe_single().execute()
    if not res.data:
        client.table("settings").insert({"explanation_mode": enabled}).execute()
    else:
        client.table("settings").update({"explanation_mode": enabled}).eq("id", res.data["id"]).execute()


# Rewards helpers

def has_reward_announcement_sent(tg_id: int) -> bool:
    client = get_client()
    res = (
        client.table("rewards")
        .select("id")
        .eq("tg_id", tg_id)
        .maybe_single()
        .execute()
    )
    return bool(res.data)


def mark_reward_sent(tg_id: int) -> None:
    client = get_client()
    client.table("rewards").insert({"tg_id": tg_id, "created_at": datetime.utcnow().isoformat()}).execute()


# Utilities for media (base64 encoding/decoding)

def encode_file_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def decode_base64_to_bytes(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))
