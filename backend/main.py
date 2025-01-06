from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.endpoints import questions, knowledge_graph

app = FastAPI(title="Math Question Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(knowledge_graph.router, prefix="/api/v1/knowledge-graph", tags=["knowledge-graph"])
