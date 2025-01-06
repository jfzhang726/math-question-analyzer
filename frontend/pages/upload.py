import streamlit as st
import requests
from typing import Dict, List

def render_upload_page():
    st.title("Math Question Analysis")
    st.write("Upload a math question for analysis")

    # Question input
    question_text = st.text_area("Enter your math question:", height=100)

    if st.button("Analyze"):
        if question_text.strip():
            analyze_question(question_text)
        else:
            st.warning("Please enter a question to analyze.")

def analyze_question(question_text: str):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/questions/",
            params={"text": question_text}
        )
        
        if response.status_code == 200:
            display_analysis_results(response.json())
        else:
            st.error(f"Error analyzing question: {response.text}")
            
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")

def display_analysis_results(results: Dict[str, List[str]]):
    st.success("Analysis completed!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Main Concepts")
        for concept in results["concepts"]:
            st.write(f"• {concept}")
            
        st.subheader("Prerequisites")
        for prereq in results["prerequisites"]:
            st.write(f"• {prereq}")
    
    with col2:
        st.subheader("Problem-Solving Techniques")
        for technique in results["techniques"]:
            st.write(f"• {technique}")
            
        st.subheader("Extensions")
        for extension in results["extensions"]:
            st.write(f"• {extension}")
    
    st.divider()
    
    # Add link to knowledge graph
    st.markdown("""
    ℹ️ View these concepts in the [Knowledge Graph](/?page=Knowledge+Graph) to see relationships and connections.
    """)