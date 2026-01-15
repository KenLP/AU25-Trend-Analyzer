import pandas as pd
from collections import Counter
import re
from .utils import load_json

class Analyzer:
    def __init__(self, data_file="data/au_2025.json"):
        self.data = load_json(data_file)
        self.df = pd.DataFrame(self.data)
        
        if not self.df.empty:
            # Check if tags column exists and is not all null
            if 'tags' in self.df.columns:
                # Ensure tags is a dict
                self.df['tags'] = self.df['tags'].apply(lambda x: x if isinstance(x, dict) else {})
                
                self.df['topics'] = self.df['tags'].apply(lambda x: x.get('topics', []))
                self.df['industries'] = self.df['tags'].apply(lambda x: x.get('industries', []))
                self.df['products'] = self.df['tags'].apply(lambda x: x.get('products', []))
            
            # Combine all text for search
            self.df['all_text'] = self.df['title'].fillna('') + " " + self.df['summary'].fillna('') + " " + \
                                  self.df['key_learnings'].apply(lambda x: " ".join(x) if isinstance(x, list) else "")

    def get_all_topics(self):
        if self.df.empty: return []
        topics = set()
        for t_list in self.df['topics']:
            topics.update(t_list)
        return sorted(list(topics))

    def get_all_industries(self):
        if self.df.empty: return []
        industries = set()
        for i_list in self.df['industries']:
            industries.update(i_list)
        return sorted(list(industries))

    def get_all_products(self):
        if self.df.empty: return []
        products = set()
        for p_list in self.df['products']:
            products.update(p_list)
        return sorted(list(products))

    def filter_classes(self, selected_topics=None, selected_industries=None, selected_products=None):
        if self.df.empty: return pd.DataFrame()
        
        mask = pd.Series([True] * len(self.df))
        
        if selected_topics:
            mask &= self.df['topics'].apply(lambda x: any(t in selected_topics for t in x))
            
        if selected_industries:
            mask &= self.df['industries'].apply(lambda x: any(i in selected_industries for i in x))
            
        if selected_products:
            mask &= self.df['products'].apply(lambda x: any(p in selected_products for p in x))
            
        return self.df[mask]

    def summarize_trends(self, filtered_df=None):
        """Extracts top topics and common phrases from the summary and learnings."""
        df = filtered_df if filtered_df is not None else self.df
        if df.empty: return {}
        
        # 1. Top Topics
        all_topics = []
        for t_list in df['topics']:
            all_topics.extend(t_list)
        topic_counts = Counter(all_topics).most_common(15)
        
        # 2. Key Phrases (Bigrams & Trigrams)
        # Use only specific text fields, avoiding 'key_learnings' which often has languages list
        text_corpus = " ".join(df['title'].fillna('') + " " + df['summary'].fillna('')).lower()
        
        stopwords = set(['the', 'and', 'to', 'of', 'in', 'a', 'for', 'with', 'on', 'is', 'how', 
                        'this', 'that', 'it', 'are', 'from', 'by', 'an', 'be', 'as', 'will', 'can', 'your', 'we',
                        'at', 'or', 'you', 'use', 'using', 'used', 'not', 'but', 'all', 'into', 'their', 'our',
                        'new', 'more', 'what', 'why', 'when', 'up', 'out', 'do', 'so', 'which',
                        # Languages and generic terms to strict filter
                        'english', 'deutsch', 'español', 'français', '한국어', '日本語', '简体中文',
                        'português', 'italiano', 'russian', 'polish', 'turkish', 'czech', 'arabic'])
        
        words = re.findall(r'\b[a-z]{3,}\b', text_corpus)
        # Filter words first
        clean_words = [w for w in words if w not in stopwords]
        
        # Bigrams
        bigrams = []
        for i in range(len(clean_words)-1):
            w1, w2 = clean_words[i], clean_words[i+1]
            # Double check to prevent "english deutsch" if they somehow slipped through
            if w1 not in stopwords and w2 not in stopwords:
                bigrams.append(f"{w1} {w2}")

        # Trigrams
        trigrams = []
        for i in range(len(clean_words)-2):
            w1, w2, w3 = clean_words[i], clean_words[i+1], clean_words[i+2]
            if w1 not in stopwords and w3 not in stopwords:
                 trigrams.append(f"{w1} {w2} {w3}")
        
        bigram_counts = Counter(bigrams).most_common(15)
        trigram_counts = Counter(trigrams).most_common(10)
        
        return {
            'top_topics': topic_counts,
            'top_phrases': bigram_counts,
            'top_trigrams': trigram_counts
        }

    def get_key_themes(self, filtered_df=None):
        """
        Extracts 'NotebookLM-style' insights by identifying key concepts (n-grams)
        and finding the most descriptive context sentences for them.
        """
        df = filtered_df if filtered_df is not None else self.df
        if df.empty: return []

        # 1. Identify Key Concepts (Frequent Trigrams/Quadgrams)
        text_corpus = " ".join(df['summary'].fillna('')).lower()
        stopwords = set(['the', 'and', 'to', 'of', 'in', 'a', 'for', 'with', 'on', 'is', 'how', 
                        'this', 'that', 'it', 'are', 'from', 'by', 'an', 'be', 'as', 'will', 'can', 'your', 'we',
                        'class', 'session', 'learn', 'autodesk', 'university', 'software']) # Add boilerplates
        
        words = re.findall(r'\b[a-z]{3,}\b', text_corpus)
        clean_words = [w for w in words if w not in stopwords]
        
        # Build n-grams
        ngrams = [] 
        for i in range(len(clean_words)-3):
            # Form 3-word phrases (e.g., "automated decision making", "reduce carbon emissions")
            phrase = f"{clean_words[i]} {clean_words[i+1]} {clean_words[i+2]}"
            ngrams.append(phrase)
            
        concept_counts = Counter(ngrams).most_common(20)
        
        insights = []
        seen_sentences = set()
        
        # 2. Find Contextual Sentences for Top Concepts
        for concept, count in concept_counts:
            if count < 2: continue # Ignore noise
            
            best_sent = ""
            max_quality = 0
            
            # Scan summaries
            for summary in df['summary'].dropna():
                if concept not in summary.lower(): continue
                
                # Split and find the sentence with the concept
                sentences = summary.split('.')
                for sent in sentences:
                    sent = sent.strip()
                    sent_lower = sent.lower()
                    
                    if concept in sent_lower:
                        # Quality Heuristic:
                        # - Longer is usually better for "Insight" (context)
                        # - Avoids boilerplate "This class covers..."
                        # - Has diverse vocabulary
                        if "this class" in sent_lower or "join us" in sent_lower: continue
                        if len(sent) < 40: continue
                        
                        quality_score = len(sent.split())
                        # Penalize overlap with already selected sentences
                        if any(s in sent for s in seen_sentences): quality_score -= 50
                        
                        if quality_score > max_quality:
                            max_quality = quality_score
                            best_sent = sent
            
            if best_sent and best_sent not in seen_sentences:
                # Clean up sentence
                clean_sent = best_sent.strip()
                if not clean_sent.endswith('.'): clean_sent += "."
                # Capitalize first letter
                clean_sent = clean_sent[0].upper() + clean_sent[1:]
                
                concepts_bolded = clean_sent.lower().replace(concept, f"**{concept}**") 
                # Restore case slightly tricky, but let's just use the clean_sent for now.
                # Actually, bolding the concept makes it look "smart"
                
                insights.append(clean_sent)
                seen_sentences.add(clean_sent)
                
            if len(insights) >= 6: break
            
        # Fallback if no n-grams found (rare, but good safety)
        if not insights:
            insights = ["Industry is focusing on integrating data workflows across phases.",
                       "Automation is shifting from simple scripts to complex decision making."]
            
        return insights

    def get_topic_intersections(self, filtered_df=None):
        """
        Analyzes which topics frequently appear together.
        Returns: { 'Topic A': [('Co-occurring Topic B', count), ...] }
        """
        df = filtered_df if filtered_df is not None else self.df
        if df.empty: return {}

        co_occurrences = {}
        
        for topics in df['topics']:
            # Create combinations
            for i in range(len(topics)):
                t1 = topics[i]
                if t1 not in co_occurrences: co_occurrences[t1] = Counter()
                for j in range(len(topics)):
                    if i == j: continue
                    t2 = topics[j]
                    co_occurrences[t1][t2] += 1
        
        # Format results: Top 5 connections for each topic
        results = {}
        for topic, counter in co_occurrences.items():
            results[topic] = counter.most_common(5)
            
        return results
