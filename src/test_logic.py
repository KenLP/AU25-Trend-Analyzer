from src.analyzer import Analyzer
from src.recommender import Recommender
import os

def test_integration():
    print("Testing Analyzer...")
    analyzer = Analyzer("data/au_2025.json")
    print(f"Loaded {len(analyzer.df)} records.")
    
    topics = analyzer.get_all_topics()
    print(f"Found topics: {topics}")
    
    trends = analyzer.summarize_trends()
    print(f"Top keywords: {trends['top_keywords'][:5]}")
    
    print("\nTesting Recommender...")
    recommender = Recommender(analyzer)
    suggestions = recommender.suggest_future_topics()
    
    print("Future Suggestions:")
    for s in suggestions:
        print(f"- {s['trend']} (Score: {s['score']}): {s['prediction']}")

if __name__ == "__main__":
    test_integration()
