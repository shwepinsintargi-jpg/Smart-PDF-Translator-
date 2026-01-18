import sys
try:
    import cgi
except ImportError:
    try:
        import legacy_cgi as cgi
        sys.modules['cgi'] = cgi
    except ImportError: pass

import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO
import time

# --- Mobile Optimized & Premium UI ---
st.set_page_config(page_title="Translator", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    header, footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    
    /* ရွှေရောင်ဖိုင်နာမည် Style */
    .file-name-gold {
        color: #D4AF37; font-weight: bold; font-size: 16px;
        text-align: center; margin-bottom: 10px;
    }
    
    /* Icon နှင့် Percentage Style */
    .status-icon { font-size: 18px; font-weight: bold; color: #1976d2; }
    
    div.stButton > button {
        border-radius: 8px; height: 3.5em; width: 100%; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = []
if 'run' not in st.session_state: st.session_state.run = False

translator = Translator()

# --- Main Layout ---
file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if file:
    # ရွှေရောင်ဖြင့် ဖိုင်နာမည်ပြခြင်း
    st.markdown(f'<div class="file-name-gold">📁 {file.name}</div>', unsafe_allow_html=True)
    
    reader = PyPDF2.PdfReader(file)
    total = len(reader.pages)
    
    # ခလုတ်များ (အပေါ်ဆုံးတွင် Fixed ပုံစံ)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶ START"): st.session_state.run = True
    with c2:
        if st.button("⏸ PAUSE"): st.session_state.run = False
    with c3:
        if st.session_state.data:
            doc = Document()
            for p, t in st.session_state.data:
                doc.add_heading(p, level=2); doc.add_paragraph(t)
            out = BytesIO()
            doc.save(out)
            st.download_button("📥 WORD", out.getvalue(), "file.docx")
        else:
            st.button("📥 WORD", disabled=True)

    # Status နှင့် Percentage (%) Icon
    done_pc = int((st.session_state.idx/total)*100) if total > 0 else 0
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.caption(f"Page: {st.session_state.idx} / {total}")
    with col_stat2:
        # Icon နှင့် % ကိုပြခြင်း
        st.markdown(f'<div style="text-align: right;" class="status-icon">✨ {done_pc}%</div>', unsafe_allow_html=True)
    
    st.progress(st.session_state.idx / total)

    # Processing Logic
    if st.session_state.run and st.session_state.idx < total:
        for i in range(st.session_state.idx, total):
            if not st.session_state.run: break
            txt = reader.pages[i].extract_text()
            if txt:
                lines = [translator.translate(l, src='en', dest='my').text for l in txt.split('\n') if l.strip()]
                time.sleep(0.4)
                st.session_state.data.append((f"Page {i+1}", "\n".join(lines)))
            st.session_state.idx = i + 1
            st.rerun()
