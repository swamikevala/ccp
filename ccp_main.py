import agent_science
import agent_irony
import os  # <--- Added to find file path
from datetime import datetime

def generate_dossier():
    print("🚀 LAUNCHING CONSCIOUS CURATION PIPELINE...\n")
    
    # 1. INITIALIZE AGENTS
    scout_science = agent_science.ScienceScout()
    scout_irony = agent_irony.IronyScout()
    
    dossier_lines = []
    dossier_lines.append(f"THE MYSTIC'S DOSSIER - {datetime.now().strftime('%Y-%m-%d')}")
    dossier_lines.append("="*60)
    dossier_lines.append("")

    # ---------------------------------------------------------
    # SECTION 1: THE HIDDEN MECHANICS (Science Scout)
    # ---------------------------------------------------------
    print("🔬 Step 1: Querying Science Vector...")
    science_queries = {
        "Mechanics of Consciousness": "mitochondria AND sleep",
        "Ecological Intelligence": "plant signaling",
        "Quantum Bridges": "quantum biology"
    }
    
    dossier_lines.append("SECTION I: THE HIDDEN MECHANICS (Science)")
    dossier_lines.append("-" * 40)
    
    for topic, query in science_queries.items():
        print(f"   -> Scouting: {topic}...")
        papers = scout_science.fetch_papers(query, days_back=120)
        
        if papers:
            top_paper = papers[0] 
            dossier_lines.append(f"Topic:    {topic}")
            dossier_lines.append(f"Headline: {top_paper['Headline']}")
            dossier_lines.append(f"Source:   {top_paper['Journal']} ({top_paper['Date']})")
            dossier_lines.append(f"Insight:  {top_paper['Abstract_Snippet']}")
            dossier_lines.append(f"Link:     {top_paper['URL']}")
            dossier_lines.append("")
        else:
            print(f"      (No papers found for {topic})")
            dossier_lines.append(f"Topic: {topic} - No high-confidence signal today.\n")

    dossier_lines.append("")

    # ---------------------------------------------------------
    # SECTION 2: THE HUMAN PREDICAMENT (Irony Scout)
    # ---------------------------------------------------------
    print("🎭 Step 2: Querying Societal Paradox Vector...")
    irony_queries = {
        "The Tech Trap": '"Artificial Intelligence" (risk OR error)',
        "The Expensive Failure": 'budget (waste OR cost OR delay)',
        "The Green Dilemma": 'environment (problem OR crisis)'
    }
    
    dossier_lines.append("SECTION II: THE HUMAN PREDICAMENT (Society)")
    dossier_lines.append("-" * 40)
    
    for theme, query in irony_queries.items():
        print(f"   -> Scouting: {theme}...")
        stories = scout_irony.fetch_irony(query, theme)
        
        if stories:
            top_story = stories[0] 
            dossier_lines.append(f"Theme:    {theme}")
            dossier_lines.append(f"Headline: {top_story['Headline']}")
            dossier_lines.append(f"Tone:     {top_story['Tone_Score']} (Signal)")
            dossier_lines.append(f"Link:     {top_story['URL']}")
            dossier_lines.append("")
        else:
            print(f"      (No stories found for {theme})")
            dossier_lines.append(f"Theme: {theme} - No high-confidence signal today.\n")

    # ---------------------------------------------------------
    # FINAL: SAVE TO DISK WITH DIAGNOSTICS
    # ---------------------------------------------------------
    final_text = "\n".join(dossier_lines)
    
    filename = "Daily_Dossier.txt"
    
    # Get the ABSOLUTE path so there is no confusion where it went
    full_path = os.path.abspath(filename) 
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(final_text)
        f.flush() # Force write to disk
        os.fsync(f.fileno()) # Force OS to confirm write
        
    print("\n" + "="*60)
    print(f"✅ SUCCESS!")
    print(f"📄 FILE SAVED AT: {full_path}")
    print("="*60)

    # Verify it exists
    if os.path.exists(full_path):
        print("   (System confirms file exists on disk)")
    else:
        print("   (WARNING: System cannot find the file after writing!)")

if __name__ == "__main__":
    generate_dossier()