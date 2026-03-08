from scraper import ask_groq
import json

def analyse_reviews(reviews_text, product_name):
    prompt = f"""You are a senior product manager analysing customer reviews for {product_name}.

Reviews:
{reviews_text[:4000]}

Return ONLY a valid JSON object, no markdown, no extra text:
{{
  "overall_sentiment": "Positive/Neutral/Negative",
  "sentiment_score": 7.2,
  "total_reviews_analysed": 50,
  "top_pain_points": [
    {{"issue": "issue description", "frequency": "High/Medium/Low", "impact": "High/Medium/Low", "example_quote": "actual quote from reviews"}}
  ],
  "top_feature_requests": [
    {{"feature": "feature description", "frequency": "High/Medium/Low", "business_value": "High/Medium/Low"}}
  ],
  "what_users_love": ["thing 1", "thing 2", "thing 3"],
  "prioritised_backlog": [
    {{"rank": 1, "item": "what to build/fix", "type": "Bug Fix/Feature/Improvement", "effort": "Low/Medium/High", "impact": "Low/Medium/High", "rationale": "why this is priority 1"}}
  ],
  "executive_summary": "3 sentence summary of the product's current standing based on reviews"
}}

Include at least 5 pain points, 5 feature requests, 5 backlog items. Be specific and actionable."""

    response = ask_groq(prompt, max_tokens=3000)
    response = response.strip()
    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]
    return json.loads(response.strip())

def analyse_competitor(competitor_name, competitor_url, content, your_product_name):
    prompt = f"""You are a product strategy consultant analysing {competitor_name} as a competitor to {your_product_name}.

Scraped content from {competitor_name}:
{content[:3000]}

Return ONLY a valid JSON object, no markdown, no extra text:
{{
  "company": "{competitor_name}",
  "url": "{competitor_url}",
  "positioning": "one line positioning statement",
  "target_audience": "who they target",
  "key_features": ["feature 1", "feature 2", "feature 3", "feature 4", "feature 5"],
  "pricing": "pricing info if found, else Unknown",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "opportunities_for_you": ["opportunity 1", "opportunity 2", "opportunity 3"]
}}"""

    response = ask_groq(prompt, max_tokens=2000)
    response = response.strip()
    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]
    return json.loads(response.strip())

def generate_strategy(product_name, review_analysis, competitor_analyses):
    competitors_summary = ""
    for c in competitor_analyses:
        competitors_summary += f"""
Competitor: {c.get('company')}
Strengths: {', '.join(c.get('strengths', []))}
Weaknesses: {', '.join(c.get('weaknesses', []))}
Opportunities for you: {', '.join(c.get('opportunities_for_you', []))}
"""

    pain_points = "\n".join([f"- {p['issue']} ({p['impact']} impact)" 
                              for p in review_analysis.get('top_pain_points', [])])
    
    top_backlog = "\n".join([f"{b['rank']}. {b['item']}" 
                              for b in review_analysis.get('prioritised_backlog', [])[:5]])

    prompt = f"""You are a Chief Product Officer advising {product_name}.

Customer Pain Points:
{pain_points}

Top Backlog Items:
{top_backlog}

Competitive Landscape:
{competitors_summary}

Write a strategic recommendation report with these sections:

1. SITUATION SUMMARY (2-3 sentences)
2. TOP 3 STRATEGIC PRIORITIES (each with rationale linking customer pain + competitor gap)
3. QUICK WINS (3 things to ship in next 30 days)
4. 90-DAY ROADMAP (month by month)
5. COMPETITIVE POSITIONING RECOMMENDATION (how to differentiate)
6. KEY RISKS TO WATCH

Be specific, actionable, and data-driven. Reference actual pain points and competitor weaknesses."""

    return ask_groq(prompt, max_tokens=3000)

def generate_competitive_table(your_product, competitor_analyses):
    """Generate a feature comparison table"""
    all_features = set()
    for c in competitor_analyses:
        for f in c.get('key_features', []):
            all_features.add(f)
    
    prompt = f"""Given these competitors and their features, create a competitive comparison.

Your product: {your_product}
Competitors: {[c.get('company') for c in competitor_analyses]}
All features found: {list(all_features)}

Return ONLY a valid JSON object:
{{
  "features": ["feature 1", "feature 2", "feature 3", "feature 4", "feature 5", "feature 6"],
  "comparison": {{
    "{your_product}": [true, false, true, true, false, true],
    "competitor_name": [true, true, false, true, true, false]
  }}
}}

Use exactly the competitor names: {[c.get('company') for c in competitor_analyses]}
Features should be the 6 most strategically important ones."""

    response = ask_groq(prompt, max_tokens=1000)
    response = response.strip()
    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]
    return json.loads(response.strip())