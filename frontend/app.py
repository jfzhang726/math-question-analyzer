import streamlit as st
from pages.upload import render_upload_page
from pages.knowledge_graph import render_knowledge_graph_page

def main():
    st.set_page_config(
        page_title="Math Question Analyzer",
        page_icon="➗",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Navigation in sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Question", "Knowledge Graph"])

    # Page routing
    if page == "Upload Question":
        render_upload_page()
    else:
        render_knowledge_graph_page()

if __name__ == "__main__":
    main()