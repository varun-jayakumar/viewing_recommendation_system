from langchain.prompts import PromptTemplate
from langchain.chat_models.ollama import ChatOllama

llm = ChatOllama(model="llama3")
# response = llm.invoke("What are the 7 wonders of the world?")
# print(f"Response: {response}")


prompt_template = PromptTemplate.from_template(
    "List {n} cooking/meal titles for {cuisine} cuisine"
)

prompt = prompt_template.format(n=3, cuisine="italian")
response = llm.invoke(prompt)
print(response)
