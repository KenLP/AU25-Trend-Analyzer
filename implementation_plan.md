# Implementation Plan - App & Scraper Refinement

## Goal
Optimize the scraper to reach ~162 classes, remove speaker data, and enhance the Streamlit app's analysis and display capabilities.

## User Review Required
> [!IMPORTANT]
> **Scraper Coverage**
> I will remove the strict `if '2025' in href` check in the scraper, as the search URL already filters for 2025. This might explain missing classes if their URLs don't explicitly contain the year.
>
> **Analysis Changes**
> I will switch the trend analysis to focus on:
> 1.  Topic frequency (using the 'Topics' tags).
> 2.  Key phrase extraction (Bigrams/Trigrams) from descriptions instead of single words.

## Proposed Changes

### src/scraper.py
#### [MODIFY] [scraper.py](file:///c:/Users/lep/.gemini/antigravity/scratch/au_trend_analyzer/src/scraper.py)
1.  **Remove Speaker Extraction:** Delete or comment out the speaker scraping logic.
2.  **Improve Loop:**
    *   Remove `if '2025' in href` check (rely on search filter).
    *   Increase wait time between pagination to ensure full load.
    *   Add a check for the total result count on the page (if visible) to verify against finding.

### app.py
#### [MODIFY] [app.py](file:///c:/Users/lep/.gemini/antigravity/scratch/au_trend_analyzer/app.py)
1.  **Class List Tab:** Replace `speakers` column with `summary` (renamed to Description).
2.  **Trend Tab:**
    *   Remove "Top Products" or move it lower.
    *   Add "Topic Distribution" chart.
    *   Update "Top Keywords" to "Common Phrases" (Bigrams).
3.  **Future Tab:**
    *   Update UI to show "Actionable Guides" (using new Recommender logic).

### src/analyzer.py
#### [MODIFY] [analyzer.py](file:///c:/Users/lep/.gemini/antigravity/scratch/au_trend_analyzer/src/analyzer.py)
1.  **Update `summarize_trends`:**
    *   Focus on `topics` counting.
    *   Implement better bigram/trigram extraction for `top_phrases`.

### src/recommender.py
#### [MODIFY] [recommender.py](file:///c:/Users/lep/.gemini/antigravity/scratch/au_trend_analyzer/src/recommender.py)
1.  **Update `suggest_future_topics`:**
    *   Generate specific "Research Guides" based on the top trends.
    *   Example structured output: `{ "trend": "AI in BIM", "guide": "Step 1: Explore X tool..." }`

## Verification Plan
1.  **Run Scraper:** `python -m src.scraper` (Expect ~162 results).
2.  **Run App:** `streamlit run app.py` and verify:
    *   No speakers column.
    *   Description column present.
    *   Topic charts and phrase analysis.
    *   Actionable guides in Future tab.
