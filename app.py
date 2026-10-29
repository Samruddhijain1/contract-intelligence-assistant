import streamlit as st
from pathlib import Path
from retrieval import build_retriever

st.set_page_config(page_title="Contract Intelligence Assistant", page_icon="📄", layout="wide")
st.title("📄 Contract Intelligence Assistant")
st.caption("Evidence-first legal clause retrieval • TF-IDF baseline • Not legal advice")

@st.cache_resource
def get_engine():
    return build_retriever(Path("data/corpus/cuad"))

try:
    engine = get_engine()
    st.success(f"Index loaded: {len(engine.chunks):,} passages")
except Exception as exc:
    st.error(f"Could not load the contract corpus: {exc}")
    st.info("Download the CUAD corpus into data/corpus/cuad. See README.md.")
    st.stop()

question = st.text_input("Ask a question about the indexed contracts", placeholder="Does this agreement allow sublicensing?")
top_k = st.slider("Number of passages", 1, 10, 5)
threshold = st.slider("Minimum relevance score", 0.0, 0.5, 0.08, 0.01)

if st.button("Search clauses", type="primary") and question.strip():
    results = engine.search(question, top_k=top_k, min_score=threshold)
    if not results:
        st.warning("No passage met the relevance threshold. The system is abstaining rather than guessing.")
    else:
        for i, result in enumerate(results, 1):
            st.subheader(f"{i}. {Path(result['file_path']).name} · score {result['score']:.3f}")
            st.caption(f"Source: {result['file_path']} | character offsets: [{result['start']}:{result['end']}]")
            st.text(result["text"])
            st.code(f"document[start:end] = passage  |  start={result['start']}, end={result['end']}", language="text")
st.divider()
st.caption("Retrieval scores are relevance signals, not probabilities or legal conclusions.")
