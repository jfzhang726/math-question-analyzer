import streamlit as st
import requests
import networkx as nx
import plotly.graph_objects as go
from typing import Dict, List

def render_knowledge_graph_page():
    st.title("Knowledge Graph Visualization")
    
    # Get concepts from backend
    try:
        response = requests.get("http://localhost:8000/api/v1/knowledge-graph/concepts")
        concepts = response.json()
    except Exception as e:
        st.error(f"Error fetching concepts: {str(e)}")
        return

    # Create sidebar for concept selection
    selected_concept = st.sidebar.selectbox(
        "Select a concept to explore",
        options=[c["name"] for c in concepts],
        index=0 if concepts else None
    )

    if selected_concept:
        display_concept_details(selected_concept)

def display_concept_details(concept: str):
    # Fetch related data
    try:
        related = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/related/{concept}").json()
        prereqs = requests.get(f"http://localhost:8000/api/v1/knowledge-graph/prerequisites/{concept}").json()
    except Exception as e:
        st.error(f"Error fetching concept details: {str(e)}")
        return

    # Create network graph
    G = nx.Graph()
    
    # Add central concept
    G.add_node(concept, node_type="main")
    
    # Add related concepts
    for rel in related:
        G.add_node(rel["name"], node_type="related")
        G.add_edge(concept, rel["name"], weight=rel["strength"])
    
    # Add prerequisites
    for prereq in prereqs:
        G.add_node(prereq["name"], node_type="prerequisite")
        G.add_edge(concept, prereq["name"], weight=prereq["count"])

    # Create visualization using plotly
    pos = nx.spring_layout(G)
    
    # Create edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Create nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        if G.nodes[node]["node_type"] == "main":
            node_color.append("red")
        elif G.nodes[node]["node_type"] == "related":
            node_color.append("blue")
        else:
            node_color.append("green")

    # Create the plot
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines"
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=20,
            color=node_color,
            line_width=2
        ),
        text=node_text,
        textposition="bottom center",
        hoverinfo="text"
    ))
    
    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    st.plotly_chart(fig, use_container_width=True)

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