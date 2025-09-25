from fastapi import FastAPI
from langserve import add_routes
import uvicorn

from models.deberta_model import DebertaConversationAgent
from models.mistral_model import MistralConversationAgent
# from models.qwen_phishme_model import inference_qwen3_phishme

from io_models.deberta import DebertaRequest, DebertaResponse, DebertaResetResponse

app = FastAPI(
    title="Scam Detection API Server",
    version="1.0",
    description="Main application with health checks."
)

# Create a separate app for the LangServe routes
langserve_app = FastAPI(title="LangServe Endpoints")

## DeBerta Routes
@app.post("/deberta/process", response_model=DebertaResponse)
async def process_deberta_message(request: DebertaRequest):
    """
    Processes a new message in a conversation using the DebertaConversationAgent.
    """
    # Create a new agent instance for each request to keep it stateless
    deberta_agent = DebertaConversationAgent()
    
    # Load the conversation history into the agent
    deberta_agent.chat = [msg.model_dump() for msg in request.history]
    
    # Process the new message
    display, df_scores, elapsed = deberta_agent.process_message(request.message, request.role)
    
    # Format the response using our Pydantic model
    response = DebertaResponse(
        display_html=display,
        scores=df_scores.to_dict(orient="records"),
        inference_time=elapsed,
        updated_history=deberta_agent.chat # Return the new, updated history
    )
    
    return response

@app.post("/deberta/reset", response_model=DebertaResetResponse)
async def reset_deberta_conversation():
    """
    Signals that the conversation history should be cleared.
    The client is responsible for clearing its stored history.
    """
    # On the server, there's no persistent state to clear per user.
    # This endpoint confirms the reset action for the client.
    return DebertaResetResponse(
        status="ok",
        message="Conversation reset. Please start a new conversation with an empty history."
    )

# LLM Routes
mistral_model = MistralConversationAgent()
add_routes(langserve_app, mistral_model.inference_mistral(), path="/mistral")
# add_routes(langserve_app, inference_qwen3_phishme(), path="/qwen3_phishme")

# Mount the langserve app into the main app under the /api prefix
app.mount("/api", langserve_app)

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "ok",
        "message": "API is running. Access model playgrounds under the /api path.",
        "main_docs": "/docs",
        "langserve_docs": "/api/docs",
        "mistral_playground": "/api/mistral/playground/",
        "qwen_playground": "/api/qwen3_phishme/playground/"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)