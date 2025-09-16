from dotenv import load_dotenv, find_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

_ = load_dotenv(find_dotenv())

## ArXiv, Wikipedia and Search Tools
arxiv_wrapper = ArxivAPIWrapper()
arxiv = ArxivQueryRun(api_wrapper = arxiv_wrapper)

api_wrapper = WikipediaAPIWrapper()
wiki = WikipediaQueryRun(api_wrapper = api_wrapper)

search = DuckDuckGoSearchRun()

st.title("🔎 Binati Multi-Agents Research")
st.markdown(":blue[**Ask questions and get answers with search and arxiv tools**]")

## Sidebar for settings
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key:", type="password")

if api_key:
    llm = ChatGroq(groq_api_key = api_key, model_name = "llama-3.1-8b-instant", streaming = True)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role":"assisstant","content":"Hi, I'm a chatbot who can search the web. How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg['content'])

    if prompt:= st.chat_input(placeholder="What is machine learning?"):
        st.session_state.messages.append({"role":"user","content":prompt})
        st.chat_message("user").write(prompt)

        llm = llm 
        tools = [search, arxiv, wiki]

        search_agent = initialize_agent(tools, llm, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, handling_parsing_errors=True)

        # using `StreamlitCallbackHandler` to display the thoughts and actions of an agent in an interactive Streamlit app
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({'role':'assistant',"content":response})
            st.write(response)
else:
    st.warning("Please enter the Groq API Key")

