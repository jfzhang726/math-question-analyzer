import streamlit as st
import requests
import json
import os

def render_knowledge_graph_page():
    st.title("Knowledge Graph Visualization")

    # Initialize session state
    if "static_dir" not in st.session_state:
        st.session_state.static_dir = os.path.join(os.getcwd(), "static")
        os.makedirs(st.session_state.static_dir, exist_ok=True)

    try:
        response = requests.get("http://localhost:8000/api/v1/knowledge-graph/concepts")
        response.raise_for_status()
        concepts = response.json()
        
        questions_response = requests.get("http://localhost:8000/api/v1/knowledge-graph/questions")
        questions_response.raise_for_status()
        questions = questions_response.json()
        
        techniques_response = requests.get("http://localhost:8000/api/v1/knowledge-graph/techniques")
        techniques_response.raise_for_status()
        techniques = techniques_response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

    selected_item_type = st.sidebar.radio(
        "Select item type to explore",
        options=["Concept", "Question", "Technique"]
    )

    if selected_item_type == "Concept":
        selected_item = st.sidebar.selectbox(
            "Select a concept to explore",
            options=[c["name"] for c in concepts],
            index=0 if concepts else None
        )
        if selected_item:
            display_item_details(selected_item, "concept")

    elif selected_item_type == "Question":
        selected_item = st.sidebar.selectbox(
            "Select a question to explore",
            options=[q["text"] for q in questions],
            index=0 if questions else None
        )
        if selected_item:
            display_item_details(selected_item, "question")

    elif selected_item_type == "Technique":
        selected_item = st.sidebar.selectbox(
            "Select a technique to explore",
            options=[t["name"] for t in techniques],
            index=0 if techniques else None
        )
        if selected_item:
            display_item_details(selected_item, "technique")


def display_item_details(item: str, item_type: str):
    try:
        if item_type == "concept":
            related_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/related/{item}")
            related_response.raise_for_status()
            related = related_response.json()

            prereqs_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/prerequisites/{item}")
            prereqs_response.raise_for_status()
            prereqs = prereqs_response.json()
        elif item_type == "question":
            related_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/related_question/{item}")
            related_response.raise_for_status()
            related = related_response.json()

            prereqs_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/prerequisites_question/{item}")
            prereqs_response.raise_for_status()
            prereqs = prereqs_response.json()
        elif item_type == "technique":
            related_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/related_technique/{item}")
            related_response.raise_for_status()
            related = related_response.json()

            prereqs_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/prerequisites_technique/{item}")
            prereqs_response.raise_for_status()
            prereqs = prereqs_response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching concept details: {str(e)}")
        return

    cytoscape_data = {"nodes": [], "edges": []}
    cytoscape_data["nodes"].append({"data": {"id": item, "label": item, "type": "main"}})

    if related:
        for rel in related:
            cytoscape_data["nodes"].append({"data": {"id": rel["name"], "label": rel["name"], "type": "related"}})
            cytoscape_data["edges"].append({"data": {"source": item, "target": rel["name"], "weight": rel["strength"]}})

    if prereqs:
        for prereq in prereqs:
            cytoscape_data["nodes"].append({"data": {"id": prereq["name"], "label": prereq["name"], "type": "prerequisite"}})
            cytoscape_data["edges"].append({"data": {"source": item, "target": prereq["name"], "weight": prereq["count"]}})

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.21.2/cytoscape.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.21.2/cytoscape-cose-bilkent.min.js"></script>
            <style>
                #cy {{
                    width: 100%;
                    height: 600px;
                    border: 1px solid black;
                }}
                .main {{
                    background-color: red;
                }}
                .related {{
                    background-color: blue;
                }}
                .prerequisite {{
                    background-color: green;
                }}
            </style>
            <script>
                let cytoscape_data = {json.dumps(cytoscape_data)};
                console.log("Cytoscape Data:", cytoscape_data);
                document.addEventListener('DOMContentLoaded', function() {{
                  if (cytoscape_data.nodes.length > 0) {{
                    let cy = cytoscape({{
                        container: document.getElementById('cy'),
                        elements: cytoscape_data,
                        style: [
                            {{
                                selector: 'node',
                                style: {{
                                    'label': 'data(label)'
                                }}
                            }},
                            {{
                                selector: '.main',
                                style: {{
                                    'background-color': 'red'
                                }}
                            }},
                            {{
                                selector: '.related',
                                style: {{
                                    'background-color': 'blue'
                                }}
                            }},
                            {{
                                selector: '.prerequisite',
                                style: {{
                                    'background-color': 'green'
                                }}
                            }},
                            {{
                                selector: 'edge',
                                style: {{
                                    'width': 'data(weight)',
                                    'line-color': '#888'
                                }}
                            }}
                        ],
                        layout: {{
                            name: 'cose'
                        }}
                    }});
                    cy.on('layoutstop', function(){{
                      console.log('Layout complete!');
                    }})
                  }} else {{
                    console.log("No data to display.");
                    document.getElementById('cy').innerText = "No data to display.";
                  }}
                }});
            </script>
        </head>
        <body>
            <div id="cy"></div>
        </body>
        </html>
    """
    st.components.v1.html(html_content, height=700)

    # Display additional information
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Related Concepts")
        for rel in related:
            st.write(f"- {rel['name']} (Strength: {rel['strength']})")
    with col2:
        st.subheader("Prerequisites")
        for prereq in prereqs:
            st.write(f"- {prereq['name']} (Count: {prereq['count']})")

def display_concept_details(concept: str):
    try:
        related_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/related/{concept}")
        related_response.raise_for_status()
        related = related_response.json()

        prereqs_response = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/prerequisites/{concept}")
        prereqs_response.raise_for_status()
        prereqs = prereqs_response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching concept details: {str(e)}")
        return

    cytoscape_data = {"nodes": [], "edges": []}
    cytoscape_data["nodes"].append({"data": {"id": concept, "label": concept, "type": "main"}})

    if related:
        for rel in related:
            cytoscape_data["nodes"].append({"data": {"id": rel["name"], "label": rel["name"], "type": "related"}})
            cytoscape_data["edges"].append({"data": {"source": concept, "target": rel["name"], "weight": rel["strength"]}})

    if prereqs:
        for prereq in prereqs:
            cytoscape_data["nodes"].append({"data": {"id": prereq["name"], "label": prereq["name"], "type": "prerequisite"}})
            cytoscape_data["edges"].append({"data": {"source": concept, "target": prereq["name"], "weight": prereq["count"]}})

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.21.2/cytoscape.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.21.2/cytoscape-cose-bilkent.min.js"></script>
            <style>
                #cy {{
                    width: 100%;
                    height: 600px;
                    border: 1px solid black;
                }}
                .main {{
                    background-color: red;
                }}
                .related {{
                    background-color: blue;
                }}
                .prerequisite {{
                    background-color: green;
                }}
            </style>
            <script>
                let cytoscape_data = {json.dumps(cytoscape_data)};
                console.log("Cytoscape Data:", cytoscape_data);
                document.addEventListener('DOMContentLoaded', function() {{
                  if (cytoscape_data.nodes.length > 0) {{
                    let cy = cytoscape({{
                        container: document.getElementById('cy'),
                        elements: cytoscape_data,
                        style: [
                            {{
                                selector: 'node',
                                style: {{
                                    'label': 'data(label)'
                                }}
                            }},
                            {{
                                selector: '.main',
                                style: {{
                                    'background-color': 'red'
                                }}
                            }},
                            {{
                                selector: '.related',
                                style: {{
                                    'background-color': 'blue'
                                }}
                            }},
                            {{
                                selector: '.prerequisite',
                                style: {{
                                    'background-color': 'green'
                                }}
                            }},
                            {{
                                selector: 'edge',
                                style: {{
                                    'width': 'data(weight)',
                                    'line-color': '#888'
                                }}
                            }}
                        ],
                        layout: {{
                            name: 'cose'
                        }}
                    }});
                    cy.on('layoutstop', function(){{
                      console.log('Layout complete!');
                    }})
                  }} else {{
                    console.log("No data to display.");
                    document.getElementById('cy').innerText = "No data to display.";
                  }}
                }});
            </script>
        </head>
        <body>
            <div id="cy"></div>
        </body>
        </html>
    """
    st.components.v1.html(html_content, height=700)

    # Display additional information
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Related Concepts")
        for rel in related:
            st.write(f"- {rel['name']} (Strength: {rel['strength']})")
    with col2:
        st.subheader("Prerequisites")
        for prereq in prereqs:
            st.write(f"- {prereq['name']} (Count: {prereq['count']})")
