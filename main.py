import sys
# Python 3.13 CGI Patch
try:
    import cgi
except ImportError:
    try:
        import legacy_cgi as cgi
        sys.modules['cgi'] = cgi
    except ImportError:
        pass

import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO
import time

# --- Premium Page Config ---
st.set_page_config(page_title="AI PDF Translator Pro", layout="wide", initial_sidebar_state="collapsed")

# --- Custom Styling (အဆင့်မြင့် App ပုံစံဖမ်းရန်) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-card {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .status-badge {
        padding: 5px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold;
        background-color: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb;
    }
    .stButton>button {
        border-radius: 10px; height: 3em; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- Logic & Session State ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = []
if 'running' not in st.session_state: st.session_state.running = False

translator = Translator()

# --- App UI Layout ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.title("🚀 AI PDF Translator Pro")
    with col_t2:
        st.markdown(f'<div style="text-align: right;"><span class="status-badge">Resume Support Enabled</span></div>', unsafe_allow_html=True)
    
    # File Uploader
    up_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if up_file:
    reader = PyPDF2.PdfReader(up_file)
    total = len(reader.pages)
    
    # Dashboard Grid
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Total Pages", total)
    with c2:
        st.metric("Processed", st.session_state.idx)
    with c3:
        percent = int((st.session_state.idx / total) * 100) if total > 0 else 0
        st.metric("Completion", f"{percent}%")

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    prog = st.progress(st.session_state.idx / total)
    
    # Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])
    with ctrl_col1:
        if st.button("▶️ Start / Resume"): st.session_state.running = True
    with ctrl_col2:
        if st.button("⏸️ Pause"): st.session_state.running = False
    with ctrl_col3:
        # Download Button (If data exists)
        if st.session_state.data:
            doc = Document()
            for p, t in st.session_state.data:
                doc.add_heading(p, level=2)
                doc.add_paragraph(t)
            out = BytesIO()
            doc.save(out)
            st.download_button("📥 Download Word", out.getvalue(), "translated.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    # Processor Logic
    if st.session_state.running and st.session_state.idx < total:
        with st.spinner("ဘာသာပြန်ဆိုနေသည်... ခေတ္တစောင့်ဆိုင်းပါ"):
            for i in range(st.session_state.idx, total):
                if not st.session_state.running: break
                
                txt = reader.pages[i].extract_text()
                if txt:
                    lines = [translator.translate(l, src='en', dest='my').text for l in txt.split('\n') if l.strip()]
                    time.sleep(0.4)
                    st.session_state.data.append((f"Page {i+1}", "\n".join(lines)))
                
                st.session_state.idx = i + 1
                st.rerun() # UI ကို ချက်ချင်း Update ဖြစ်စေရန်
    st.markdown('</div>', unsafe_allow_html=True)
