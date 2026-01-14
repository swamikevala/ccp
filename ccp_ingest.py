import argparse
import hashlib
from datetime import datetime
from typing import Dict, Iterable, List

import agent_irony
import agent_science
from ccp_storage import init_db, save_items, DEFAULT_DB_PATH


def _make_item_id(parts: Iterable[str]) -> str:
    payload = "||".join(part.strip().lower() for part in parts if part)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalize_science_item(topic: str, paper: Dict) -> Dict:
    return {
        "id": _make_item_id([topic, paper.get("Headline"), paper.get("URL"), paper.get("Date")]),
        "item_type": "science",
        "topic": topic,
        "headline": paper.get("Headline", "Untitled"),
        "source": paper.get("Journal", "Unknown Source"),
        "published_date": paper.get("Date"),
        "summary": paper.get("Abstract_Snippet"),
        "url": paper.get("URL"),
        "tone": None,
        "created_at": datetime.utcnow().isoformat(),
    }


def _normalize_irony_item(theme: str, story: Dict) -> Dict:
    return {
        "id": _make_item_id([theme, story.get("Headline"), story.get("URL"), story.get("Date")]),
        "item_type": "society",
        "topic": theme,
        "headline": story.get("Headline", "Untitled"),
        "source": story.get("Source", "Unknown"),
        "published_date": story.get("Date"),
        "summary": None,
        "url": story.get("URL"),
        "tone": story.get("Tone_Score"),
        "created_at": datetime.utcnow().isoformat(),
    }


def ingest(db_path: str, days_back: int) -> int:
    init_db(db_path)
    scout_science = agent_science.ScienceScout()
    scout_irony = agent_irony.IronyScout()

    science_queries = {
        "Mechanics of Consciousness": "mitochondria AND sleep",
        "Ecological Intelligence": "plant signaling",
        "Quantum Bridges": "quantum biology",
    }
    irony_queries = {
        "The Tech Trap": '"Artificial Intelligence" (risk OR error)',
        "The Expensive Failure": "budget (waste OR cost OR delay)",
        "The Green Dilemma": "environment (problem OR crisis)",
    }

    items: List[Dict] = []
    for topic, query in science_queries.items():
        papers = scout_science.fetch_papers(query, days_back=days_back)
        items.extend(_normalize_science_item(topic, paper) for paper in papers)

    for theme, query in irony_queries.items():
        stories = scout_irony.fetch_irony(query, theme)
        items.extend(_normalize_irony_item(theme, story) for story in stories)

    return save_items(items, db_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest items into the CCP database.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to the SQLite database.")
    parser.add_argument("--days-back", type=int, default=120, help="Days back for science queries.")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    inserted = ingest(args.db_path, args.days_back)
    print(f"Inserted {inserted} items into {args.db_path}")
