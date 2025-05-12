import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain.tools import tool
from backend.core.logging_config import logger
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get collection name and model from environment variables with defaults
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "golf_shot_vectors")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "thenlper/gte-small")

# Initialize the model and client lazily
def get_model():
    return SentenceTransformer(EMBEDDING_MODEL)

def get_qdrant_client():
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_api_key:
        raise ValueError("QDRANT_API_KEY environment variable is not set")
        
    return QdrantClient(
        url="https://6f592f43-f667-4234-ad3a-4f15ed5882ef.us-west-2-0.aws.cloud.qdrant.io:6333",
        api_key=qdrant_api_key
    )


def preprocess_query_with_llm(query: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_msg = (
        "You are a golf shot planner assistant. "
        "Given a golfer's query, extract the structured intent behind the shot.\n\n"
        "Respond in JSON with:\n"
        "- distance (number or 'unknown')\n"
        "- intent ('avoid' or 'achieve')\n"
        "- shape (or 'unknown')\n"
        "- club (or 'unknown')"
    )

    user_msg = f"Query: {query}"
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
        return (
            f"The golfer is planning a {parsed['distance']}-yard shot and wants to "
            f"{parsed['intent']} a {parsed['shape']} using {parsed['club']}."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")

@tool
def get_shot_recommendations(query: str) -> str:
    """
    Retrieves relevant golf shot recommendations based on the query using semantic search.
    Useful for questions about club selection, shot technique, or avoiding certain shot patterns.
    """
    logger.debug(f"[TOOL CALLED] get_shot_recommendations: {query}")
    
    # structure the query to more closely align with the embedded data.
    preprocessed_query = preprocess_query_with_llm(query)

    # Get embeddings for the query
    model = get_model()
    query_vector = model.encode(preprocessed_query)
    
    # Search Qdrant
    client = get_qdrant_client()
    try:
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5,
            with_payload=True
        )
    except UnexpectedResponse as e:
        if "Vector dimension error" in str(e):
            raise ValueError(
                f"Vector dimension mismatch! The current embedding model ({EMBEDDING_MODEL}) "
                f"produces vectors of a different dimension than what's expected by the Qdrant collection. "
                f"Please check your EMBEDDING_MODEL environment variable and ensure it matches the model "
                f"used to create the vectors in your Qdrant collection."
            ) from e
        raise  # Re-raise other UnexpectedResponse errors
    
    # Format the results
    recommendations = []
    for point in search_result.points:
        recommendations.append(f"Score: {point.score:.4f} | {point.payload['text']}")
    
    if not recommendations:
        return "No relevant shot recommendations found."
    
    return "\n".join(recommendations) 