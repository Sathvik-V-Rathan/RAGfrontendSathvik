import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage


KB_PATH = "faiss_index"
MODEL_NAME = "llama3.2"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)

embeddings = OllamaEmbeddings(model=MODEL_NAME)

def load_kb():
    if os.path.exists(KB_PATH):
        return FAISS.load_local(KB_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        initial_text = ["To reset your password, visit settings > security.",
                        "If the screen is flickering, check the HDMI cable connection."]
        vectorstore = FAISS.from_texts(initial_text, embeddings)
        vectorstore.save_local(KB_PATH)
        return vectorstore

vectorstore = load_kb()


@tool
def lookup_poicy(query: str) -> str:
    """Useful for looking up existing policies, troubleshooting steps, or known issues in the Knowledge Base."""
    docs = vectorstore.similarity_search(query, k=3)
    if not docs:
        return "No relevant information found in the knowledge base."
    return "\n\n".join([doc.page_content for doc in docs])

search = DuckDuckGoSearchRun()

@tool
def search_web(query: str) -> str:
    """Useful for searching the internet for solutions when the knowledge base is insufficient."""
    return search.invoke(query)

@tool
def update_kb(text: str) -> str:
    """Useful for adding new, verified information to the Knowledge Base for future use. 
    Call this after finding a solution from the web."""
    global vectorstore
    vectorstore.add_texts([text])
    vectorstore.save_local(KB_PATH)
    return "Knowledge Base updated successfully with new information."

tools = [lookup_poicy, search_web, update_kb]

system_prompt = (
    "You are a helpful L1 Support Assistant. Your goal is to solve user computer issues.\n"
    "Follow this workflow strictly:\n"
    "1. CHECK the Knowledge Base using `lookup_poicy` first.\n"
    "2. If the answer is found, output it.\n"
    "3. If NOT found, SEARCH the web using `search_web`.\n"
    "4. If a solution is found on the web, UPDATE the Knowledge Base using `update_kb` so it is available next time.\n"
    "5. Finally, answer the user."
)

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

if __name__ == "__main__":
    print("--- L1 Support Agent Started ---")
    print("Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            initial_state = {"messages": [HumanMessage(content=user_input)]}
            
            result = agent.invoke(initial_state)

            if "messages" in result and len(result["messages"]) > 0:
                last_message = result["messages"][-1]
                print(f"Agent: {last_message.content}")
            else:
                print("Agent: (No response generated)")
                
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

