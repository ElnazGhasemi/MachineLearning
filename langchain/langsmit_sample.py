import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langsmith import traceable

# Load environment variables
load_dotenv()

# Set LangSmith configuration
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "xxxxxxxxxxxxxxxxxxxx"
os.environ["LANGSMITH_PROJECT"] = "pr-downright-technician-69"

def initialize_llm():
    """Initialize the LLM with error handling."""
    try:
        return ChatOpenAI(
            temperature=0,
            model="o1",
            api_key="xxxxxxxxxxxxxxxxxxxxxx",
            base_url="https://litellm.deriv.ai/v1",
            streaming=True
        )
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

# Wrap with LangSmith tracing
@traceable(name="pr-downright-technician-69")
def run_llm(prompt: str):
    """Run LLM with the given prompt and handle errors."""
    try:
        # Initialize LLM
        llm = initialize_llm()
        if not llm:
            return "Error: Could not initialize LLM"
        
        # Create chat message
        message = HumanMessage(content=prompt)
        
        # Get response
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"Error during LLM invocation: {str(e)}"

def main():
    """Main function to run the LLM test."""
    try:
        # Test prompt
        prompt = "What is LangChain?"
        print("Sending prompt:", prompt)
        
        # Get and print response
        response = run_llm(prompt)
        print("\nAI Response:", response)
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main()
