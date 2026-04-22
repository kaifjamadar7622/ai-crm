from db.database import conn, cursor

_interactions_store = []


def _is_db_available():
    return cursor is not None and conn is not None


# ✅ 1. Log Interaction
def log_interaction(data):
    if not _is_db_available():
        interaction_id = len(_interactions_store) + 1
        _interactions_store.append(
            {
                "id": interaction_id,
                "hcp_name": data.get("hcp_name", "Unknown"),
                "interaction_type": data.get("interaction_type", "General"),
                "notes": data.get("notes", ""),
            }
        )
        return {
            "status": "Logged successfully (demo mode)",
            "id": interaction_id,
            "hcp_name": data.get("hcp_name", "Unknown"),
        }

    try:
        cursor.execute(
            "INSERT INTO interactions (hcp_name, interaction_type, notes) VALUES (%s, %s, %s)",
            (data.get("hcp_name"), data.get("interaction_type"), data.get("notes", "")),
        )
        conn.commit()
        return {"status": "interaction saved"}
    except Exception as exc:
        return {"error": f"database write failed: {exc}"}


# ✅ 2. Edit Interaction
def edit_interaction(id, new_notes):
    if not _is_db_available():
        for item in _interactions_store:
            if item["id"] == id:
                item["notes"] = new_notes
                return {"status": "interaction updated (demo mode)", "id": id}
        return {"error": f"interaction {id} not found"}

    try:
        cursor.execute("UPDATE interactions SET notes=%s WHERE id=%s", (new_notes, id))
        conn.commit()
        return {"status": "interaction updated"}
    except Exception as exc:
        return {"error": f"database update failed: {exc}"}


# ✅ 3. Get HCP Info
def get_hcp_info(name):
    return {"hcp_name": name, "specialization": "Cardiologist"}


# ✅ 4. Summarize Interaction
def summarize_interaction(text):
    return {"summary": text[:50]}


# ✅ 5. Suggest Follow-up
def suggest_followup(text):
    return {"suggestion": "Schedule next meeting in 2 weeks"}


# ✅ 6. Compliance Check
def compliance_check(text):
    text_l = (text or "").lower()
    flags = []

    if any(word in text_l for word in ["patient name", "mrn", "phone", "email", "address"]):
        flags.append("Possible PII/PHI in note")

    if any(word in text_l for word in ["guarantee", "cure", "no side effects", "100% safe"]):
        flags.append("Potential non-compliant medical claim")

    if any(word in text_l for word in ["off-label", "unapproved use"]):
        flags.append("Potential off-label discussion")

    return {
        "status": "review_required" if flags else "clear",
        "flags": flags,
        "message": "Compliance review suggested before logging." if flags else "No obvious compliance flags detected.",
    }


# ✅ 7. Sentiment Extraction
def extract_sentiment(text):
    text_l = (text or "").lower()

    positive_hits = ["interested", "positive", "keen", "good", "promising", "agreed", "scheduled"]
    negative_hits = ["not interested", "concern", "declined", "negative", "skeptical", "no interest", "resistant"]

    pos = sum(1 for token in positive_hits if token in text_l)
    neg = sum(1 for token in negative_hits if token in text_l)

    if pos > neg:
        label = "positive"
    elif neg > pos:
        label = "negative"
    else:
        label = "neutral"

    return {
        "sentiment": label,
        "score": pos - neg,
    }