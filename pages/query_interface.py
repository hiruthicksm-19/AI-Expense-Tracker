"""
Streamlit page for natural language expense queries.

Allows users to ask questions in natural language and get instant answers
from the invoice database.
"""

import streamlit as st
from mongodb_handler import MongoDBHandler
from modules import NaturalLanguageQueryInterface


st.set_page_config(
    page_title="Query Assistant",
    page_icon="🔍",
    layout="wide"
)

st.markdown("<h1>🔍 Expense Query Assistant</h1>", unsafe_allow_html=True)
st.markdown("Ask questions about your expenses in natural language")

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Connect to MongoDB
try:
    mongodb = MongoDBHandler()
    collection = mongodb.collection
    mongodb.close()
    
    # Initialize query interface
    mongodb_fresh = MongoDBHandler()
    query_interface = NaturalLanguageQueryInterface(mongodb_fresh.collection)
    
except Exception as e:
    st.error(f"Database connection error: {str(e)}")
    st.stop()

# Sidebar with examples
with st.sidebar:
    st.subheader("Supported Questions")
    examples = query_interface.get_supported_questions()
    
    for query_type, questions in examples.items():
        with st.expander(f"📝 {query_type.replace('_', ' ').title()}"):
            for q in questions:
                if st.button(q, key=q):
                    st.session_state.question = q

# Main query input
col1, col2 = st.columns([4, 1])

with col1:
    question = st.text_input(
        "Ask a question about your expenses:",
        placeholder="e.g., What's the total spent? Show top 5 invoices",
        key="main_question"
    )

with col2:
    submit = st.button("🔍 Search", use_container_width=True)

# Process query
if submit and question:
    with st.spinner("Analyzing your question..."):
        answer, metadata = query_interface.query(question)
        
        # Add to history
        st.session_state.query_history.append({
            "question": question,
            "answer": answer,
            "query_type": metadata.get("query_type")
        })
        
        # Display answer
        st.subheader("Answer")
        
        # Color code by query type
        if "error" in metadata:
            st.error(answer)
        else:
            st.info(answer)
        
        # Show query details in expander
        with st.expander("📊 Query Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Query Type:** {metadata.get('query_type', 'Unknown')}")
                st.write(f"**Original Question:** {question}")
            
            with col2:
                if metadata.get("spec", {}).get("filters"):
                    st.write(f"**Filters Applied:** {len(metadata['spec']['filters'])} filter(s)")
                if metadata.get("spec", {}).get("limit"):
                    st.write(f"**Limit:** {metadata['spec']['limit']} results")

# Display query history
if st.session_state.query_history:
    st.divider()
    st.subheader("📜 Query History")
    
    cols = st.columns([1, 4, 1])
    cols[0].write("**Type**")
    cols[1].write("**Question**")
    cols[2].write("**Action**")
    
    st.divider()
    
    for idx, item in enumerate(reversed(st.session_state.query_history[-10:])):
        cols = st.columns([1, 4, 1])
        
        cols[0].write(item.get("query_type", "unknown")[:15])
        cols[1].write(item["question"])
        
        if cols[2].button("↻", key=f"rerun_{idx}"):
            st.session_state.main_question = item["question"]
            st.rerun()

# Quick stats section
st.divider()
st.subheader("📈 Quick Stats")

try:
    mongodb = MongoDBHandler()
    total_invoices = mongodb.collection.count_documents({})
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total count
    col1.metric("Total Invoices", total_invoices)
    
    # Total amount
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}]
    result = list(mongodb.collection.aggregate(pipeline))
    total_amount = result[0]["total"] if result else 0
    col2.metric("Total Amount", f"₹{total_amount:,.2f}")
    
    # Average
    avg = total_amount / total_invoices if total_invoices > 0 else 0
    col3.metric("Average Invoice", f"₹{avg:,.2f}")
    
    # Unique sellers
    sellers = mongodb.collection.distinct("seller_name")
    col4.metric("Unique Sellers", len(sellers))
    
    mongodb.close()
    
except Exception as e:
    st.warning(f"Could not load statistics: {str(e)}")

# Footer
st.divider()
st.caption(
    "💡 Tip: Try asking questions like 'Show top 5 invoices', "
    "'What's the average?', or 'Group by seller'"
)
