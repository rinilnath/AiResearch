"""
AI Defect Agent Core
Handles natural language processing, categorization, prioritization, and solution recommendation
"""

import anthropic
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from vector_store import VectorStore
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

class AIDefectAgent:
    """
    Core AI Agent for Manufacturing Defect Analysis
    """

    def __init__(self, api_key: str):
        """Initialize the AI agent with Claude API"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.vector_store = VectorStore()

        # Define categories and priorities
        self.categories = [
            "Mechanical", 
            "Electrical", 
            "Quality Control", 
            "Safety", 
            "Process"
        ]

        self.priorities = {
            "CRITICAL": "Immediate safety risk or complete production halt",
            "HIGH": "Significant quality impact or multiple units affected",
            "MEDIUM": "Single unit affected, workaround available",
            "LOW": "Minor issue, cosmetic, no production impact"
        }

    def process_defect_report(
        self, 
        defect_description: str, 
        historical_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Main processing function - takes defect description and returns structured analysis
        
        Args:
            defect_description: Natural language defect report
            historical_data: DataFrame with historical defects for solution matching
            
        Returns:
            Dict with categorization, priority, solution, and similar cases
        """
        # 🆕 Step 1: Find similar past defects using vector search
        similar_defects = []
        try:
            matches = self.vector_store.find_similar(defect_description, top_k=3)
            for match in matches:
                similar_defects.append({
                    'ticket_id': match.metadata.get('ticket_id', 'Unknown'),
                    'description': match.metadata.get('description', ''),
                    'category': match.metadata.get('category', ''),
                    'priority': match.metadata.get('priority', ''),
                    'resolution': match.metadata.get('resolution', ''),
                    'similarity_score': round(match.score, 3)
                })
        except Exception as e:
            print(f"Vector search failed: {e}")
            # Continue without similar defects
        
        # Build the AI prompt (now with similar cases)
        prompt = self._build_analysis_prompt(defect_description, historical_data, similar_defects)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse the response
        result = self._parse_ai_response(response.content[0].text)
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['raw_input'] = defect_description
        
        # 🆕 Add similar cases to result
        result['similar_cases'] = similar_defects
        
        return result

    def _build_analysis_prompt(
        self, 
        defect_description: str, 
        historical_data: Optional[pd.DataFrame],
        similar_defects: Optional[List[Dict]] = None
    ) -> str:
        """Build the prompt for Claude API"""

        # Include historical context if available
        historical_context = ""
        if historical_data is not None and len(historical_data) > 0:
            recent_defects = historical_data.tail(10)
            historical_context = "\n\nHistorical Defect Examples:\n"
            for _, row in recent_defects.iterrows():
                historical_context += f"- {row['description']} | Category: {row['category']} | Solution: {row['resolution']}\n"

        # 🆕 Include similar defects from vector search
        similar_context = ""
        if similar_defects and len(similar_defects) > 0:
            similar_context = "\n\n🔍 MOST SIMILAR PAST DEFECTS (Semantic Search Results):\n"
            for i, defect in enumerate(similar_defects, 1):
                similar_context += f"""
    {i}. Ticket: {defect['ticket_id']} (Similarity: {defect['similarity_score']})
    Description: {defect['description']}
    Category: {defect['category']} | Priority: {defect['priority']}
    Resolution: {defect['resolution']}
    """

        prompt = f"""You are an AI assistant for a manufacturing plant's defect management system. 
    Analyze the following defect report and provide a structured response.

    DEFECT REPORT:
    {defect_description}

    {historical_context}
    {similar_context}

    TASK:
    Analyze this defect report and respond with a JSON object containing:

    1. **extracted_info**: Key information extracted from the report
    - equipment: What equipment/machine is affected
    - location: Where in the plant (line number, area, etc.)
    - issue: What is the specific problem
    - severity_signals: Keywords indicating severity (safety, halt, leak, etc.)

    2. **category**: Classify into ONE of these categories:
    - Mechanical (physical parts, hydraulics, pneumatics, wear)
    - Electrical (wiring, circuits, sensors, power)
    - Quality Control (finish, dimensions, defects in product)
    - Safety (hazards, risks, PPE issues)
    - Process (procedures, workflow, configuration)

    3. **priority**: Assign ONE priority level:
    - CRITICAL: Immediate safety risk OR complete production halt
    - HIGH: Significant quality impact OR multiple units affected
    - MEDIUM: Single unit affected, workaround exists
    - LOW: Minor/cosmetic issue, no production impact

    4. **priority_reasoning**: Brief explanation of why this priority was assigned

    5. **recommended_actions**: List of 3-5 specific action steps to resolve
    - Should be concrete and actionable
    - Include immediate actions and follow-up
    - **IMPORTANT**: If similar defects shown above had successful resolutions, prioritize those proven solutions

    6. **assigned_team**: Which team should handle this
    - Options: Maintenance, Quality Control, Safety, Production, Engineering

    7. **estimated_resolution_time**: Realistic time estimate (e.g., "2 hours", "1 day", "3 days")

    RESPOND ONLY WITH VALID JSON, NO MARKDOWN, NO EXPLANATIONS OUTSIDE JSON:
    """

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse the AI response into structured format"""
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())

            # Validate required fields
            required_fields = [
                'extracted_info', 'category', 'priority', 
                'recommended_actions', 'assigned_team'
            ]

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            return result

        except json.JSONDecodeError as e:
            # Fallback parsing if JSON fails
            return {
                'extracted_info': {'raw': response_text},
                'category': 'Unknown',
                'priority': 'MEDIUM',
                'priority_reasoning': 'Failed to parse AI response',
                'recommended_actions': ['Review defect manually', 'Categorize based on visual inspection'],
                'assigned_team': 'Engineering',
                'estimated_resolution_time': 'Unknown',
                'parsing_error': str(e)
            }

    def batch_process(self, defect_reports: List[str], historical_data: Optional[pd.DataFrame] = None) -> List[Dict]:
        """Process multiple defect reports"""
        results = []
        for report in defect_reports:
            result = self.process_defect_report(report, historical_data)
            results.append(result)
        return results

    def generate_summary_report(self, processed_defects: List[Dict]) -> Dict:
        """Generate summary statistics from processed defects"""
        if not processed_defects:
            return {
                'total_defects': 0,
                'by_category': {},
                'by_priority': {},
                'by_team': {}
            }

        # Count by category
        categories = {}
        for defect in processed_defects:
            cat = defect.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        # Count by priority
        priorities = {}
        for defect in processed_defects:
            pri = defect.get('priority', 'Unknown')
            priorities[pri] = priorities.get(pri, 0) + 1

        # Count by team
        teams = {}
        for defect in processed_defects:
            team = defect.get('assigned_team', 'Unknown')
            teams[team] = teams.get(team, 0) + 1

        return {
            'total_defects': len(processed_defects),
            'by_category': categories,
            'by_priority': priorities,
            'by_team': teams,
            'critical_count': priorities.get('CRITICAL', 0),
            'high_count': priorities.get('HIGH', 0)
        }


# Test function
def test_agent():
    """Test the AI agent with sample defect"""
    
    # You'll need to set your API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    agent = AIDefectAgent(api_key)
    
    # Test defect
    test_defect = "Hydraulic press on Line 3 is leaking oil near the base. Worker reported slippery floor and safety concern. Press is still operational but oil puddle is growing."
    
    print("Processing defect report...")
    result = agent.process_defect_report(test_defect)
    
    print("\n" + "="*60)
    print("AI ANALYSIS RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    # Run test
    test_agent()
