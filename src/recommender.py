class Recommender:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        # Static knowledge base of emerging trends (2025-2026 outlook)
        self.kb = {
            "Generative AI": ["AI", "Automation", "Machine Learning"],
            "Decarbonization": ["Sustainability", "Energy", "Carbon"],
            "Digital Twin": ["Tandem", "IoT", "Operations"],
            "Immersive Experience": ["XR", "VR", "AR", "Spatial Computing"],
            "Industrialized Construction": ["Prefab", "Modular", "Manufacturing"]
        }

    def suggest_future_topics(self):
        """
        Analyzes alignment between AU 2025 content and Global External Trends.
        Returns a broad list of opportunities based on keyword correlation.
        """
        trends = self.analyzer.summarize_trends()
        if not trends: return []
        
        top_topics = trends.get('top_topics', [])
        top_phrases = dict(trends.get('top_phrases', []))
        
        # Expanded External Market Intelligence (Simulated from LinkedIn/Market Research)
        external_signals = {
            "Agentic AI & Automation": {
                "keywords": ["ai", "automation", "generative", "agent", "machine learning", "neural"],
                "prediction": "AI is moving from 'passive assistant' to 'autonomous agent'.",
                "directions": [
                    "Investigating 'Agentic AI' for autonomous construction scheduling adjustments.",
                    "Developing proprietary Generative Design scripts (Dynamo/Python) for layout optimization.",
                    "Implementing AI-based risk detection from project daily logs."
                ]
            },
            "Connected Data Ecosystems": {
                "keywords": ["cloud", "platform", "connected", "data", "api", "lake", "exchange"],
                "prediction": "The shifted focus from 'Files' to 'Granular Data' APIs.",
                "directions": [
                    "Building a 'Data Lake' strategy: Extracting unlocked data from Revit/ACC.",
                    "Connecting BIM directly to ERP/Procurement systems via Autodesk Platform Services (APS).",
                    "Standardizing data schemas for seamless Project-to-O&M handover."
                ]
            },
            "Digital Twins & Reality Capture": {
                "keywords": ["twin", "reality", "capture", "lidar", "iot", "sensor", "tandem"],
                "prediction": "Digital Twins are becoming the standard deliverable for high-value assets.",
                "directions": [
                    "Integrating real-time IoT sensor data into BIM models for facilities management.",
                    "Using drones/LiDAR for automated weekly progress validation against the model.",
                    "Simulating operational energy performance using the digital twin."
                ]
            },
            "Sustainability & Decarbonization": {
                "keywords": ["sustainability", "carbon", "green", "energy", "embodied", "circular"],
                "prediction": "Carbon Intelligence is becoming a non-negotiable compliance requirement.",
                "directions": [
                    "Automating embodied carbon calculation (EC3) during the design phase.",
                    "Tracking 'Green Building' certification metrics in real-time dashboards.",
                    "Exploring circular economy workflows: Material passports for assets."
                ]
            },
            "Industrialized Construction": {
                "keywords": ["modular", "offsite", "prefab", "manufacturing", "dfma"],
                "prediction": "Convergence of manufacturing (DfMA) and construction workflows.",
                "directions": [
                    "Aligning Revit families with manufacturer constraints for seamless prefabrication.",
                    "Implementing distinct 'Design for Manufacturing' (DfMA) stages in the BIM execution plan.",
                    "Tracking offsite component status in the main construction schedule."
                ]
            }
        }
        
        suggestions = []
        
        # Correlate External Signals with Internal Data
        for macro_trend, data in external_signals.items():
            internal_score = 0
            keywords = data['keywords']
            
            # Check phrases in internal data
            for phrase, count in top_phrases.items():
                if any(k in phrase.lower() for k in keywords):
                    internal_score += count
            
            # Check topics
            for topic, count in top_topics:
                if any(k in topic.lower() for k in keywords):
                    internal_score += count * 3 # Weight topics higher
            
            # Always include if there is ANY signal, to ensure richness
            if internal_score > 0:
                suggestions.append({
                    'trend': macro_trend,
                    'score': internal_score + 10, # Baseline boost
                    'type': 'Strategic Opportunity',
                    'reason': f"Found {internal_score} relevant signals in current class data matching global '{macro_trend}' trends.",
                    'prediction': data['prediction'],
                    'guide': data['directions']
                })

        return sorted(suggestions, key=lambda x: x['score'], reverse=True)

    def _generate_research_direction(self, topic1, topic2):
        """Generates research directions instead of step-by-step guides."""
        t1 = topic1.lower()
        t2 = topic2.lower()
        
        directions = []
        
        if "bim" in t1 and "ai" in t2.lower():
            directions = [
                "Automating code compliance checking using LLMs on BIM data.",
                "Generative scheduling: Using historical BIM data to predict construction timelines.",
                "Semantic search: Chat with your BIM model using Natural Language Processing."
            ]
        elif "bim" in t1 and "data" in t2.lower():
            directions = [
                "Building a Data Lake: Extracting granular Revit parameter data for cross-project analytics.",
                "API-first workflows: Connecting BIM directly to ERP/Procurement systems via APS.",
                "Standardizing data schemas for seamless Project-to-O&M handover."
            ]
        elif "construction" in t1 and "ai" in t2.lower():
            directions = [
                "Visual QA/QC: Using Computer Vision on site photos to auto-update BIM status.",
                "Risk Prediction: Analyzing daily logs with AI to forecast safety incidents.",
                "Optimizing resource allocation with predictive machine learning models."
            ]
        else:
            directions = [
                f"How {topic2} technologies can automate manual workflows in {topic1}.",
                f"Case studies: ROI of integrating {topic2} into standard {topic1} deliverables.",
                f"Developing a pilot program to test {topic2} tools on a {topic1} project."
            ]
            
        return directions
