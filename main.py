import sys
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

# --- Ultra-Minimalist UI ---
st.set_page_config(page_title="Translator", layout="centered")

st.markdown("""
    <style>
    /* အောက်ဆွဲစရာမလိုအောင် Fixed Height လုပ်ခြင်း */
    .stApp { background-color: #ffffff; max-height: 100vh; overflow: hidden; }
    .main-container {
        border: 1px solid #eee; padding: 25px; border-radius: 12px;
        background: #ffffff; margin-top: 20px;
    }
    div.stButton > button {
        border-radius: 8px; height: 3em; width: 100%; font-size: 14px;
    }
    .metric-box { text-align: center; padding: 10px; }
    /* မလိုအပ်တဲ့ Streamlit Header/Footer ဖြုတ်ခြင်း */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = []
if 'run' not in st.session_state: st.session_state.run = False

translator = Translator()

# --- Content ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # ဖိုင်တင်ရန် (အကျဉ်းချုပ်)
    file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    
    if file:
        reader = PyPDF2.PdfReader(file)
        total = len(reader.pages)
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Pages", total)
        m2.metric("Done", st.session_state.idx)
        m3.metric("Status", f"{int((st.session_state.idx/total)*100)}%")
        
        st.progress(st.session_state.idx / total)
        st.write("")
        
        # Control Buttons
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶ Start"): st.session_state.run = True
        with c2:
            if st.button("⏸ Pause"): st.session_state.run = False
        with c3:
            if st.session_state.data:
                doc = Document()
                for p, t in st.session_state.data:
                    doc.add_heading(p, level=2); doc.add_paragraph(t)
                out = BytesIO()
                doc.save(out)
                st.download_button("📥 Word", out.getvalue(), "file.docx")
            else:
                st.button("📥 Word", disabled=True)

        # Logic
        if st.session_state.run and st.session_state.idx < total:
            with st.spinner("Processing..."):
                for i in range(st.session_state.idx, total):
                    if not st.session_state.run: break
                    txt = reader.pages[i].extract_text()
                    if txt:
                        lines = [translator.translate(l, src='en', dest='my').text for l in txt.split('\n') if l.strip()]
                        time.sleep(0.4) # Safety delay
                        st.session_state.data.append((f"Page {i+1}", "\n".join(lines)))
                    st.session_state.idx = i + 1
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
