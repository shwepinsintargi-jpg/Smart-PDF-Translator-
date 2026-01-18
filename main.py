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

# --- Mobile Optimized UI ---
st.set_page_config(page_title="Translator", layout="centered")

st.markdown("""
    <style>
    /* Screen အပြည့်သုံးပြီး Scroll မလိုအောင်လုပ်ခြင်း */
    .stApp { background-color: #ffffff; }
    header, footer {visibility: hidden;}
    
    /* ကွက်လပ်များ လျှော့ချခြင်း */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* ခလုတ်များအား ဘေးတိုက် စုစည်းခြင်း */
    div.stButton > button {
        border-radius: 8px; height: 3.5em; width: 100%; 
        font-weight: bold; font-size: 14px;
    }
    .metric-container { margin-bottom: -20px; }
    </style>
    """, unsafe_allow_html=True)

if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = []
if 'run' not in st.session_state: st.session_state.run = False

translator = Translator()

# --- Main Layout ---
# ဖိုင်တင်ခြင်း (နေရာအနည်းဆုံးယူရန်)
file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if file:
    reader = PyPDF2.PdfReader(file)
    total = len(reader.pages)
    
    # ခလုတ်များကို အပေါ်ဆုံးသို့ တင်လိုက်ခြင်း
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

    # Metrics နှင့် Progress ကို ခလုတ်အောက်မှာ ကပ်ထားခြင်း
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.caption(f"Total: {total}")
    m2.caption(f"Done: {st.session_state.idx}")
    m3.caption(f"Status: {int((st.session_state.idx/total)*100)}%")
    st.progress(st.session_state.idx / total)
    st.markdown('</div>', unsafe_allow_html=True)

    # Processing Logic
    if st.session_state.run and st.session_state.idx < total:
        with st.spinner("Translating..."):
            for i in range(st.session_state.idx, total):
                if not st.session_state.run: break
                txt = reader.pages[i].extract_text()
                if txt:
                    lines = [translator.translate(l, src='en', dest='my').text for l in txt.split('\n') if l.strip()]
                    time.sleep(0.4)
                    st.session_state.data.append((f"Page {i+1}", "\n".join(lines)))
                st.session_state.idx = i + 1
                st.rerun()
