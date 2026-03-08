import streamlit as st
import json
from scraper import scrape_app_reviews, scrape_competitor
from analyser import analyse_reviews, analyse_competitor, generate_strategy, generate_competitive_table

st.set_page_config(page_title="AI Product Intelligence", page_icon="🧠", layout="wide")

st.title("🧠 AI Product & Competitive Intelligence")
st.caption("Analyse customer feedback + competitors to build winning product strategy")

tab1, tab2, tab3 = st.tabs(["📊 Voice of Customer", "🔍 Competitor Intelligence", "⚡ Strategic Synthesis"])

# ─── TAB 1: VOICE OF CUSTOMER ───
with tab1:
    st.subheader("Analyse Customer Reviews")
    col1, col2 = st.columns([1, 1])

    with col1:
        product_name = st.text_input("Your Product Name", placeholder="e.g. Swiggy, Notion, Razorpay")
        reviews_input = st.text_area(
            "Paste reviews or App Store / Play Store URL",
            height=300,
            placeholder="Paste raw reviews here...\n\nOr paste a URL like:\nhttps://play.google.com/store/apps/details?id=..."
        )

    with col2:
        st.subheader("Analysis Results")

        if st.button("Analyse Reviews", type="primary"):
            if not product_name or not reviews_input:
                st.error("Please enter product name and reviews")
            else:
                with st.spinner("Analysing customer feedback..."):
                    raw = scrape_app_reviews(reviews_input)
                    result = analyse_reviews(raw, product_name)
                    st.session_state['review_analysis'] = result
                    st.session_state['product_name'] = product_name

        if 'review_analysis' in st.session_state:
            r = st.session_state['review_analysis']

            # Sentiment Score
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Sentiment", r.get('overall_sentiment', 'N/A'))
            col_b.metric("Score", f"{r.get('sentiment_score', 0)}/10")
            col_c.metric("Reviews Analysed", r.get('total_reviews_analysed', 'N/A'))

            st.markdown("---")

            # Pain Points
            st.markdown("#### 🔴 Top Pain Points")
            for p in r.get('top_pain_points', []):
                with st.expander(f"{p['issue']} — Impact: {p['impact']} | Frequency: {p['frequency']}"):
                    st.write(f"💬 *\"{p.get('example_quote', 'N/A')}\"*")

            # Feature Requests
            st.markdown("#### 💡 Top Feature Requests")
            for f in r.get('top_feature_requests', []):
                with st.expander(f"{f['feature']} — Business Value: {f['business_value']}"):
                    st.write(f"Frequency: {f['frequency']}")

            # What users love
            st.markdown("#### 💚 What Users Love")
            for item in r.get('what_users_love', []):
                st.write(f"✅ {item}")

            st.markdown("---")

            # Prioritised Backlog
            st.markdown("#### 📋 Prioritised Product Backlog")
            for b in r.get('prioritised_backlog', []):
                with st.expander(f"#{b['rank']} — {b['item']} [{b['type']}] | Effort: {b['effort']} | Impact: {b['impact']}"):
                    st.write(b.get('rationale', ''))

            st.markdown("---")
            st.markdown("#### 📝 Executive Summary")
            st.info(r.get('executive_summary', ''))

# ─── TAB 2: COMPETITOR INTELLIGENCE ───
with tab2:
    st.subheader("Competitor Analysis")

    your_product = st.text_input("Your Product Name", placeholder="e.g. MyApp", key="comp_product")

    st.markdown("#### Add Competitors (up to 3)")
    comp_cols = st.columns(3)
    competitors = []
    for i, col in enumerate(comp_cols):
        with col:
            name = st.text_input(f"Competitor {i+1} Name", placeholder=f"e.g. Competitor {i+1}", key=f"comp_name_{i}")
            url = st.text_input(f"Competitor {i+1} URL", placeholder="https://...", key=f"comp_url_{i}")
            if name and url:
                competitors.append({"name": name, "url": url})

    if st.button("Analyse Competitors", type="primary"):
        if not your_product:
            st.error("Please enter your product name")
        elif not competitors:
            st.error("Please add at least one competitor")
        else:
            results = []
            for comp in competitors:
                with st.spinner(f"Analysing {comp['name']}..."):
                    content = scrape_competitor(comp['url'])
                    analysis = analyse_competitor(comp['name'], comp['url'], content, your_product)
                    results.append(analysis)

            st.session_state['competitor_analyses'] = results
            st.session_state['your_product'] = your_product

    if 'competitor_analyses' in st.session_state:
        analyses = st.session_state['competitor_analyses']

        # Individual competitor cards
        for c in analyses:
            st.markdown(f"### {c.get('company')}")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Positioning**")
                st.write(c.get('positioning', ''))
                st.markdown("**Target Audience**")
                st.write(c.get('target_audience', ''))
                st.markdown("**Pricing**")
                st.write(c.get('pricing', 'Unknown'))
                st.markdown("**Key Features**")
                for f in c.get('key_features', []):
                    st.write(f"• {f}")

            with col2:
                st.markdown("**✅ Strengths**")
                for s in c.get('strengths', []):
                    st.write(f"• {s}")
                st.markdown("**❌ Weaknesses**")
                for w in c.get('weaknesses', []):
                    st.write(f"• {w}")
                st.markdown("**🎯 Opportunities for You**")
                for o in c.get('opportunities_for_you', []):
                    st.write(f"• {o}")

            st.markdown("---")

        # Comparison Table
        st.markdown("### 📊 Feature Comparison Table")
        with st.spinner("Generating comparison table..."):
            try:
                table_data = generate_competitive_table(
                    st.session_state['your_product'],
                    analyses
                )
                features = table_data.get('features', [])
                comparison = table_data.get('comparison', {})

                header = "| Feature | " + " | ".join(comparison.keys()) + " |"
                divider = "|---------|" + "---------|" * len(comparison)
                rows = []
                for i, feature in enumerate(features):
                    row = f"| {feature} |"
                    for product, values in comparison.items():
                        val = values[i] if i < len(values) else False
                        row += " ✅ |" if val else " ❌ |"
                    rows.append(row)

                table_md = "\n".join([header, divider] + rows)
                st.markdown(table_md)
            except Exception as e:
                st.warning(f"Could not generate table: {e}")

# ─── TAB 3: STRATEGIC SYNTHESIS ───
with tab3:
    st.subheader("Strategic Synthesis")
    st.caption("Combines your review analysis + competitor data into one strategic recommendation")

    has_reviews = 'review_analysis' in st.session_state
    has_competitors = 'competitor_analyses' in st.session_state

    col1, col2 = st.columns(2)
    col1.metric("Voice of Customer", "✅ Ready" if has_reviews else "❌ Not done", 
                delta="Go to Tab 1" if not has_reviews else None)
    col2.metric("Competitor Analysis", "✅ Ready" if has_competitors else "❌ Not done",
                delta="Go to Tab 2" if not has_competitors else None)

    if st.button("Generate Strategic Report", type="primary"):
        if not has_reviews or not has_competitors:
            st.error("Please complete both Voice of Customer and Competitor Intelligence first")
        else:
            with st.spinner("Generating your strategic report... this may take 30 seconds..."):
                report = generate_strategy(
                    st.session_state.get('product_name', st.session_state.get('your_product', 'Your Product')),
                    st.session_state['review_analysis'],
                    st.session_state['competitor_analyses']
                )
                st.session_state['strategy_report'] = report

    if 'strategy_report' in st.session_state:
        st.markdown("### 📄 Strategic Recommendation Report")
        st.markdown(st.session_state['strategy_report'])

        st.download_button(
            label="Download Report",
            data=st.session_state['strategy_report'],
            file_name=f"strategy_report_{st.session_state.get('product_name','product')}.txt",
            mime="text/plain"
        )
