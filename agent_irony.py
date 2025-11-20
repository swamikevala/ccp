import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IronyScout:
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_irony(self, query_term, theme_name):
        params = {
            "query": f"{query_term} sourcelang:eng",
            "mode": "artlist",
            "maxrecords": "5",
            "timespan": "7d", 
            "format": "json",
            "sort": "toneasc" # Still asking for the "worst" news first
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, verify=False, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Error for {theme_name}: {e}")
            return []

        articles = data.get("articles", [])
        clean_results = []

        for art in articles:
            try:
                tone = float(art.get("avgtone", 0))
            except:
                tone = 0

            # FILTER REMOVED: Pass everything through for the POC
            clean_results.append({
                "Theme": theme_name,
                "Headline": art.get("title", "No Title"),
                "Tone_Score": tone, 
                "Source": art.get("source name", "Unknown"),
                "URL": art.get("url"),
                "Date": art.get("seendate", "")[:8] 
            })

        return clean_results

if __name__ == "__main__":
    # Quick test logic
    agent = IronyScout()
    print("Testing Unfiltered Agent...")
    res = agent.fetch_irony('"Artificial Intelligence"', "Test")
    print(f"Found {len(res)} items.")