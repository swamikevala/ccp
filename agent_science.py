import requests
import datetime
import urllib3
from typing import List, Dict

# Disable warnings just in case, though pip-system-certs usually handles it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ScienceScout:
    def __init__(self, email="your_email@example.com"):
        self.base_url = "https://api.openalex.org/works"
        # Identify yourself to get faster/better pool access
        self.headers = {"User-Agent": f"mailto:{email}"}

    def reconstruct_abstract(self, inverted_index: Dict) -> str:
        """
        Reconstructs the abstract from the inverted index provided by OpenAlex.
        """
        if not inverted_index:
            return "No abstract available."
        
        word_list = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_list.append((pos, word))
        
        sorted_words = sorted(word_list, key=lambda x: x[0])
        return " ".join([word for _, word in sorted_words])

    def fetch_papers(self, query: str, days_back: int = 60) -> List[Dict]:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days_back)
        
        # API Parameters
        params = {
            "filter": f"default.search:{query},from_publication_date:{start_date}",
            "sort": "cited_by_count:desc,relevance_score:desc",
            "per_page": 5,
            "select": "id,title,publication_date,primary_location,open_access,abstract_inverted_index,concepts"
        }

        try:
            # Added timeout to prevent hanging
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status() # Check for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []

        results = response.json().get('results', [])
        clean_results = []

        for work in results:
            # --- DEFENSIVE CODING FIX ---
            # 1. Get primary_location, default to empty dict if None
            primary_loc = work.get('primary_location') or {}
            
            # 2. Get source, default to empty dict if None (The previous crash point)
            source = primary_loc.get('source') or {}
            
            # 3. Get display_name safely
            source_name = source.get('display_name', 'Unknown Source')
            # -----------------------------

            abstract_text = self.reconstruct_abstract(work.get('abstract_inverted_index'))
            
            # Handle Concepts safely
            concepts = work.get('concepts', []) or []
            top_concepts = [c.get('display_name') for c in concepts[:3]]

            # Handle URL safely
            open_access = work.get('open_access') or {}
            url = open_access.get('oa_url') or primary_loc.get('landing_page_url') or "No URL"

            clean_results.append({
                "Headline": work.get('title', 'No Title'),
                "Journal": source_name,
                "Date": work.get('publication_date', 'Unknown Date'),
                "Abstract_Snippet": abstract_text[:300] + "..." if len(abstract_text) > 300 else abstract_text,
                "URL": url,
                "Key_Topics": top_concepts
            })

        return clean_results

# --- EXECUTION BLOCK ---

if __name__ == "__main__":
    agent = ScienceScout(email="test@example.com")
    
    search_pillars = {
        "The Mechanics of Consciousness": "mitochondria AND sleep AND energy",
        "Ecological Intelligence": "plant signaling AND root communication",
        "Quantum Bridges": "quantum biology AND consciousness",
        "Human Mechanism": "gut microbiome AND brain axis AND mood"
    }

    print("🔎 AGENT A: SCOUTING SCIENTIFIC DATABASES (Defensive Mode)...\n")

    for pillar, query in search_pillars.items():
        print(f"--- Scouting Pillar: {pillar} ---")
        papers = agent.fetch_papers(query, days_back=120) # Increased lookback to ensure hits
        
        if not papers:
            print("   No high-confidence matches found.")
            continue

        for p in papers:
            print(f"Found: {p['Headline']}")
            print(f"   Source: {p['Journal']} ({p['Date']})")
            print(f"   Snippet: {p['Abstract_Snippet']}")
            print(f"   Link: {p['URL']}")
            print("-" * 40)
        print("\n")