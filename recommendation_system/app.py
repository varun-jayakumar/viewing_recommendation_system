from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os
from langchain.output_parsers import PydanticOutputParser
from typing import Optional
from queryServie import queryVectorDB
from embeddingService import get_embeddings
from rankingService import rerank_documents
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import streamlit as st
import re

load_dotenv()
open_api_key = os.environ["OPEN_API_KEY"]

llm = ChatOpenAI(model="gpt-3.5-turbo-16k", api_key=open_api_key)
chat_history = []

def add_to_chat_history(role, message):
   
    chat_history.append((role, message))

def get_contextualized_query(query):
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question - first person \
    which can be understood without the chat history - do not loose details mentioned in the user question - question must be in first person. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is. (i.e User query question like hi can left as it is) keep imdb and year if mentione din the question"""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{query}"),
        ]
    )
    
    context_question_prompt = contextualize_q_prompt.format(
        chat_history=[(role, msg) for role, msg in chat_history],
        query=query
    )
    
    context_query = llm.invoke(context_question_prompt).content
    return context_query

def extract_plot(context_query):
    prompt_template_text = """query: from the below text, extract essence, a essence of the movie idea is a description of what the movie is about it can also be genre - be direct, leave out meta data of the moive in text while responding (i.e "I want to wantch a adventorus movie with imdb > 7" expected outputed is "adventorus ) into the essence,\n
     if no essence is found respond with any movie plot
       \n text: {text}"""

    class Plot(BaseModel):
        essence: str = Field(description="The essence of the movie")
    
    parser = PydanticOutputParser(pydantic_object=Plot)
    format_instructions = parser.get_format_instructions()
    
    prompt_template = PromptTemplate(
        template=prompt_template_text,
        input_variables=["text"],
        partial_variables={"format_instructions": format_instructions},
    )
    
    prompt = prompt_template.format(text=context_query)
    response = llm.invoke(prompt)
    extracted_plot = response.content.removeprefix("Essence: ")
    return extracted_plot

def extract_metadata(context_query):
    prompt_template_text = """query: from the "text",
    \n \n Guidelines: 
    \n - output must be a valid JSON (no extra spaces or epecial characters)
    \n - imdb is a "float" value - noextra spaces - format is correctly
    \n - if imdb is specified in the text below set the value (can be anyhting greater than, less than or equal) but be mentioned - imdb is a "float" value that is a rating for the movie, if imdb is not present set value to "-1" (i.e imdb greater than 7 means imdb is specified and its 7)
    \n - extract release year of the movie and set the value for key "year" from text: the release year specifies release date of movie (see if the text specifies a relese date if not then set to -1)
    \n - the year must four_digit_integer or -1 not 10's or 20's or 10 or 30 or similar format
    \n - mark imdb_greaterthan, imdb_lessthan,imdb_equal: True if the text mentions IMDB rating equal to a number else False, if not specified set all to False in output JSON
    \n  - year_equal if text says the eay to be equal to then set to True else False
    \n - year_greaterthan to True (i.e released after 2000) else Flase
    \n - year_lessthan to  True (i.e released before 2000) else False
    \n - format of year should be fount_digit_integer or -1 nothing else is allowed
    \n "Text": {text}
    \n
    \n
    """
    
    class Metadata(BaseModel):
        imdb: float = Field(description="The rating of the movie")
        year: int = Field(description="The year the movie is released should be integer four digit")
        imdb_greaterthan: bool = Field(description="True if the text requests IMDB rating greater than specified in text, if not specified False")
        imdb_lessthan: bool = Field(description="True if the text requests IMDB rating less than specified in text, if not specified False")
        year_greaterthan: bool = Field(description="True if the text requests year greater than specified in text, if not specified False")
        year_lessthan: bool = Field(description="True if the text requests year less than specified in text, if not specified False")
        year_equal: bool = Field(description="True if the text requests year equal to specified in text, if not specified False")
        imdb_equal: bool = Field(description="True if the text mentions IMDB rating equal to a number else False")
    
    parser = PydanticOutputParser(pydantic_object=Metadata)
    format_instructions = parser.get_format_instructions()
    
    prompt_template = PromptTemplate(
        template=prompt_template_text,
        input_variables=["text"],
        partial_variables={"format_instructions": format_instructions},
    )
    
    prompt = prompt_template.format(text=context_query)
    response = llm.invoke(prompt)
    answer = response.content
    parsed_output = parser.parse(answer)
    print(parsed_output)
    return parsed_output

def fetch_movies(extracted_plot, parsed_output):
    extracted_plot_vector = get_embeddings(extracted_plot)
    query_response = queryVectorDB(extracted_plot_vector, parsed_output, 3)
    query_result = query_response["matches"]
    actual_result = []
    for item in query_result:
       if(item["score"] > 0.8):
            actual_result.append(item)
    if len(actual_result) != 0:
        ranked_result = rerank_documents(query_result, extracted_plot)
    else:
        ranked_result = actual_result
        
    return ranked_result

def generate_response(query, ranked_result, chat_history):
    # prompt_template = PromptTemplate.from_template("""
    # if query is a greeting of any sort, respond with "Hello! I'm your personal movie recommendation assistant. What kind of movie are you in the mood for today?"                                               
    # Answer the query based on Data Provided in context and chat_history below without mentioning about the presence context in answer, if not able to find answer from context - say I am not able to find answer for the quesiton. If asked anything outside of movies say I am a movie assistant, I can only help you with movie suggestions.\n
    # Answer question in format of movie title, year, imdb rating,  small plot of the movie, cast\n
    # check how many suggestions are requested by user in query and provide appropriate
                                                   
    # Query: {query}\n
    # Context: {data}\n\n
    # chat_history: {chat_history}                                                                                      
    # """)
    prompt_template = PromptTemplate.from_template("""
    
    Answer the query based on Data Provided in only context and chat_history below without mentioning about the presence context in answer, if not able to find answer from context - say "I am not able to find answer for the quesiton". If asked anything outside of movies say I am a movie assistant, I can only help you with movie suggestions.
if query is a greeting of any sort, respond with "Hello! I'm your personal movie recommendation assistant. What kind of movie are you in the mood for today?"
   if able to find relavent correct answer:
    \n Answer question in format of (if you are able to find anything if not say "I am not able to find answer for the quesiton"):
                                                   
    ### title (year)

    **IMDb Rating:** imdb rating

    **Plot:**
    fullplot

    **Cast:**
    - cast_1
    - cast_2
    - cast_3
    - cast_4
     \n
    else:
        if IMDB rating or year is not match the criteria in query):
        Answer format: "I am not able to find answer for the quesiton"
    
    Check how many suggestions are requested by user in query and provide appropriate suggestions.

    Query: {query}
    Context: {data}

    chat_history: {chat_history}
                                                   
    """)


    response = llm.invoke(prompt_template.format(query=query, data=ranked_result, chat_history=chat_history))
    add_to_chat_history("system", response.content)
    return response.content

def main():
    st.set_page_config(
    page_title="MovieMate",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"),
    menu_items={
        'Get Help': 'jayakumar.va@northeastern.edu',
        'Report a bug': "jayakumar.va@northeastern.edu",
        }
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()
    st.title("MovieMate: Movie Recommendation Assistant")

    body ="""
    Hey there! I'm here to help you find the perfect movie to watch. With my dataset of movies up until 2015, I can recommend films based on various factors. Just let me know what you're looking for, and I'll provide you with some great suggestions! Here are the ways I can help:

        📖 Plot Type: Tell me the kind of story you're in the mood for (e.g., adventure, romance, mystery), and I'll find a movie that matches.
        ⭐ IMDB Rating: Looking for highly-rated movies? I can suggest films with the best ratings.
        📅 Year of Release: If you have a specific year or range of years in mind, I can find movies from that time period.

    Just share your preferences, and I'll get started on finding the perfect movie for you! 🍿🎬
"""
    st.caption(body)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message[0] == "user":
            with st.chat_message(message[0], avatar="🧑‍💻"):
                st.markdown(message[1])
        else:
            with st.chat_message(message[0],avatar="🤖"):
                st.markdown(message[1])


    # User input
    if user_query := st.chat_input("Recommend me a Action movie with imdb rating above 7"):
        
        # Display user message in chat message container
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_query)
        
        # Append user message to chat history
        st.session_state.chat_history.append(("user", user_query))
        with st.status("Transformning Query with context...", expanded=True) as status:
            # Process the user query (dummy functions for demonstration)
            context_query = get_contextualized_query(user_query)
            st.write("Extracting plot from query...")
            extracted_plot = extract_plot(context_query)
            st.write("Extracting metadata from query...")
            parsed_output = extract_metadata(context_query)
            st.write("Performing semantic search on data source...")
            ranked_result = fetch_movies(extracted_plot, parsed_output)
            st.write("Rerankng results...")
            status.update(label="Process Complete!", state="complete", expanded=False)
        
        # Generate assistant's response
        if len(ranked_result) == 0:
            ranked_result = "No movies found"
        response = generate_response(context_query, ranked_result, st.session_state.chat_history)
        
        st.session_state.chat_history.append(("assistant", response))
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
    




if __name__ == "__main__":
    main()
