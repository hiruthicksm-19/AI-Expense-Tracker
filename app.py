"""
Streamlit Web UI for Invoice Extraction.

A modern web interface for uploading invoices, extracting data,
and managing them in MongoDB.

Usage:
    streamlit run app.py
"""

import streamlit as st
from pathlib import Path

from config import OUTPUT_DIR
from modules import (
    extract_pdf_text_from_upload,
    InvoiceExtractor,
    InvoiceValidator,
    FileHandler,
)
from mongodb_handler import MongoDBHandler


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Invoice Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# Session State Initialization
# ============================================================

if "extracted_invoices" not in st.session_state:
    st.session_state.extracted_invoices = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ============================================================
# Helper Functions
# ============================================================

def save_to_mongodb(invoices: list) -> dict:
    """Save invoices to MongoDB with duplicate detection."""
    results = {
        "inserted": [],
        "duplicates": [],
        "errors": []
    }
    
    try:
        mongodb = MongoDBHandler()
        
        for invoice in invoices:
            invoice_number = invoice.get("invoice_number")
            
            if mongodb.invoice_exists(invoice_number):
                results["duplicates"].append(invoice_number)
            else:
                try:
                    mongodb.insert_invoice(invoice)
                    results["inserted"].append({
                        "invoice_number": invoice_number,
                    })
                except Exception as e:
                    results["errors"].append({
                        "invoice_number": invoice_number,
                        "error": str(e)
                    })
        
        mongodb.close()
    
    except Exception as e:
        results["errors"].append({
            "invoice_number": "connection",
            "error": f"MongoDB connection error: {str(e)}"
        })
    
    return results


def get_mongodb_status() -> tuple:
    """Get MongoDB connection status and invoice count."""
    try:
        mongodb = MongoDBHandler()
        total = mongodb.collection.count_documents({})
        mongodb.close()
        return True, total
    except Exception as e:
        return False, str(e)


# ============================================================
# UI Layout
# ============================================================

st.markdown("<h1 class='main-header'>📄 Invoice Data Extractor</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.write("### Database Status")
    
    is_connected, status = get_mongodb_status()
    if is_connected:
        st.success(f"✓ Connected to MongoDB\n**Total Invoices:** {status}")
    else:
        st.error(f"✗ MongoDB Error: {status}")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Invoice(s)")
    
    uploaded_files = st.file_uploader(
        "Choose PDF file(s) to extract invoice data",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF invoices"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected**")
        
        if st.button("🔍 Extract & Process", use_container_width=True, type="primary"):
            st.session_state.extracted_invoices = []
            st.session_state.processing_complete = False
            
            # Initialize components
            extractor = InvoiceExtractor()
            validator = InvoiceValidator()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    # Extract PDF text
                    invoice_text = extract_pdf_text_from_upload(uploaded_file)
                    
                    if not invoice_text:
                        st.warning(f"⚠️ No extractable text in {uploaded_file.name}")
                        continue
                    
                    # Extract with LLM
                    extracted_data = extractor.extract(invoice_text)
                    
                    # Validate invoice
                    invoice = validator.validate(extracted_data)
                    
                    st.session_state.extracted_invoices.append({
                        "filename": uploaded_file.name,
                        "data": invoice
                    })
                
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.empty()
            progress_bar.empty()
            st.session_state.processing_complete = True

with col2:
    st.subheader("📊 Extracted Data")
    
    if st.session_state.processing_complete and st.session_state.extracted_invoices:
        st.success(f"✓ Successfully extracted {len(st.session_state.extracted_invoices)} invoice(s)")
        
        # Display extracted invoices
        for idx, invoice_item in enumerate(st.session_state.extracted_invoices):
            with st.expander(f"Invoice {idx + 1}: {invoice_item['filename']}", expanded=idx == 0):
                invoice_data = invoice_item["data"]
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write(f"**Invoice Number:** {invoice_data.get('invoice_number') or 'N/A'}")
                    st.write(f"**Invoice Date:** {invoice_data.get('invoice_date') or 'N/A'}")
                    st.write(f"**Month:** {invoice_data.get('month') or 'N/A'}")
                    st.write(f"**Year:** {invoice_data.get('year') or 'N/A'}")
                    st.write(f"**Seller:** {invoice_data.get('seller_name') or 'N/A'}")
                
                with col_b:
                    st.write(f"**Quantity:** {invoice_data.get('quantity') or 'N/A'}")
                    st.write(f"**Total Amount:** ₹{invoice_data.get('total_amount') or 'N/A'}")
                    st.write(f"**Payment Method:** {invoice_data.get('payment_details') or 'N/A'}")
                
                st.write(f"**Description:** {invoice_data.get('description') or 'N/A'}")
                st.write(f"**Address:** {invoice_data.get('seller_address') or 'N/A'}")
                
                # Show raw JSON
                with st.expander("📋 Raw JSON"):
                    st.json(invoice_data)

# Database Operations
st.divider()
st.subheader("Save to Database")

col_save1, col_save2, col_save3 = st.columns(3)

with col_save1:
    if st.button("Save to MongoDB", use_container_width=True, type="primary"):
        if st.session_state.extracted_invoices:
            with st.spinner("Saving to MongoDB..."):
                invoices_data = [item["data"] for item in st.session_state.extracted_invoices]
                results = save_to_mongodb(invoices_data)
                
                if results["inserted"]:
                    st.success(f"Success: {len(results['inserted'])} invoice(s) saved!")
                    for item in results["inserted"]:
                        st.write(f"  - {item['invoice_number']}")
                
                if results["duplicates"]:
                    st.warning(f"Warning: {len(results['duplicates'])} duplicate(s) skipped:")
                    for inv_num in results["duplicates"]:
                        st.write(f"  - {inv_num}")
                
                if results["errors"]:
                    st.error(f"Error: {len(results['errors'])} error(s) occurred:")
                    for error in results["errors"]:
                        st.write(f"  - {error['invoice_number']}: {error['error']}")
        else:
            st.warning("No invoices to save. Please extract invoices first.")

with col_save2:
    if st.button("Export to JSON", use_container_width=True):
        if st.session_state.extracted_invoices:
            invoices_data = [item["data"] for item in st.session_state.extracted_invoices]
            json_str = FileHandler.export_to_json_string(invoices_data)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="invoices.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.warning("No invoices to export.")

with col_save3:
    if st.button("Clear All", use_container_width=True):
        st.session_state.extracted_invoices = []
        st.session_state.processing_complete = False
        st.rerun()

# Query Assistant Section
st.divider()
st.subheader("Query Assistant - Ask Questions About Your Expenses")

try:
    from modules import LLMQueryPipeline, transcribe_audio
    
    mongodb_query = MongoDBHandler()
    query_pipeline = LLMQueryPipeline(mongodb_query.collection)
    
    # Initialize session state for transcribed text
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    
    # Query input layout with audio recording
    col_q1, col_q2 = st.columns([4, 1])
    
    with col_q1:
        question = st.text_input(
            "Ask a question about your expenses:",
            placeholder="e.g., What is the total spent? Show top 5 invoices",
            key="query_input",
            value=st.session_state.transcribed_text
        )
    
    with col_q2:
        query_submit = st.button("Search", use_container_width=True, type="primary")
    
    # Audio recording section with microphone
    st.markdown("**📱 Voice Input:**")
    
    col_audio1, col_audio2 = st.columns([1, 4])
    
    with col_audio1:
        st.markdown("🎤")
    
    with col_audio2:
        audio_data = st.audio_input("Record your question")
        
        if audio_data is not None:
            try:
                with st.spinner("Transcribing audio..."):
                    # Get audio bytes
                    audio_bytes = audio_data.getvalue()
                    
                    # Transcribe
                    transcribed = transcribe_audio(audio_bytes)
                    
                    # Update session state with transcribed text
                    st.session_state.transcribed_text = transcribed
                    
                    st.success(f"✓ Transcribed: {transcribed}")
                    
                    # Update the text input with transcribed text
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error transcribing audio: {str(e)}")
    
    # Process query
    if query_submit and question:
        with st.spinner("Analyzing your question with AI..."):
            answer, metadata = query_pipeline.process_question(question)
            
            # Display answer
            st.info(answer)
            
            # Show query details
            with st.expander("Query Details"):
                col_qa, col_qb, col_qc = st.columns(3)
                
                with col_qa:
                    st.write(f"**Documents Found:** {metadata.get('result_count', 0)}")
                
                with col_qb:
                    pipeline = metadata.get('pipeline', [])
                    st.write(f"**Pipeline Stages:** {len(pipeline)}")
                
                with col_qc:
                    if metadata.get('error'):
                        st.write(f"**Error:** {metadata['error'][:30]}...")
                    else:
                        st.write("**Status:** Success")
                
                # Show generated pipeline
                if metadata.get('pipeline'):
                    st.write("**MongoDB Pipeline:**")
                    st.json(metadata['pipeline'])
                
                # Show raw results
                if metadata.get('raw_results'):
                    st.write("**Raw Results:**")
                    st.json(metadata['raw_results'])
            
            # Clear transcribed text after submission
            st.session_state.transcribed_text = ""
    
    mongodb_query.close()

except ImportError as e:
    st.warning(f"Required module not available: {str(e)}")
except Exception as e:
    st.error(f"Query interface error: {str(e)}")

# View Database Section
st.divider()
st.subheader("View Database")

if st.button("🔄 Refresh Database View", use_container_width=True):
    try:
        mongodb = MongoDBHandler()
        all_invoices = list(mongodb.collection.find({}))
        mongodb.close()
        
        if all_invoices:
            st.success(f"**Total Invoices in Database:** {len(all_invoices)}")
            
            # Create a table view
            table_data = []
            for inv in all_invoices:
                table_data.append({
                    "Invoice Number": inv.get("invoice_number", "N/A"),
                    "Date": inv.get("invoice_date", "N/A"),
                    "Seller": inv.get("seller_name", "N/A"),
                    "Amount": f"₹{inv.get('total_amount', 'N/A')}",
                    "MongoDB ID": str(inv.get("_id", "N/A"))[:8] + "..."
                })
            
            st.dataframe(table_data, use_container_width=True)
        else:
            st.info("📭 No invoices in database yet.")
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

# Power BI Dashboard Section
st.divider()
st.subheader("Analytics Dashboard")

st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 1rem;'>
    View detailed analytics and insights from your invoice data
    </p>
""", unsafe_allow_html=True)

# Embed Power BI dashboard
st.components.v1.html("""
<iframe 
    title="invoice-final" 
    width="100%" 
    height="600" 
    src="https://app.powerbi.com/reportEmbed?reportId=03adf8b8-4dc7-4584-a870-98b78dc6883e&autoAuth=true&ctid=d4963ce2-af94-4122-95a9-644e8b01624d" 
    frameborder="0" 
    allowFullScreen="true">
</iframe>
""", height=620)

st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #999;'>
    <small>Powered by Power BI | Invoice Expense Tracker v1.0</small>
    </div>
""", unsafe_allow_html=True)
