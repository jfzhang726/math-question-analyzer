import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Math Question Analyzer", layout="wide")

def main():
    st.title("Math Question Analysis System")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Question", "Knowledge Graph"])
    
    if page == "Upload Question":
        show_upload_page()
    else:
        show_knowledge_graph()

def show_upload_page():
    st.header("Upload Math Question")
    
    # Input methods
    input_method = st.radio("Input Method", ["Text", "Image"])
    
    if input_method == "Text":
        question_text = st.text_area("Enter your math question:")
        if st.button("Analyze") and question_text:
            analyze_text_question(question_text)
    else:
        uploaded_file = st.file_uploader("Upload an image of your math question", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Question", use_column_width=True)
            if st.button("Analyze"):
                analyze_image_question(uploaded_file)

def analyze_text_question(text: str):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/questions/",
            params={"text": text}
        )
        if response.status_code == 200:
            display_analysis_results(response.json())
        else:
            st.error("Error analyzing question")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def analyze_image_question(image_file):
    try:
        files = {"image": image_file}
        response = requests.post(
            "http://localhost:8000/api/v1/questions/",
            files=files
        )
        if response.status_code == 200:
            display_analysis_results(response.json())
        else:
            st.error("Error analyzing question")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def display_analysis_results(results):
    st.subheader("Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Main Concepts:**")
        for concept in results["concepts"]:
            st.write(f"- {concept}")
        
        st.write("**Prerequisites:**")
        for prereq in results["prerequisites"]:
            st.write(f"- {prereq}")
    
    with col2:
        st.write("**Problem-Solving Techniques:**")
        for technique in results["techniques"]:
            st.write(f"- {technique}")
        
        st.write("**Concept Extensions:**")
        for extension in results["extensions"]:
            st.write(f"- {extension}")

def show_knowledge_graph():
    st.header("Knowledge Graph Visualization")
    st.write("Coming soon in Phase 2...")

if __name__ == "__main__":
    main()