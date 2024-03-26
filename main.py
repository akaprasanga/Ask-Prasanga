import os
from dotenv import load_dotenv
import langchain.document_loaders as document_loaders
import streamlit as st
from htmlTemplates import css, bot_template, user_template
from langchain_google_genai import ChatGoogleGenerativeAI


def handle_userinput(user_question, gemini_model, query):
    # response = gemini_model.generate_content(user_question).text
    response = gemini_model.invoke(user_question).content
    print(response)
    # response = "hello there!"

    # st.session_state.chat_history = response['chat_history']
    st.session_state.chat_history.append({'human':query, 'gemini':response})
    print("Chat history::",st.session_state.chat_history)

    for i, message in enumerate(list(reversed(st.session_state.chat_history))):

        st.write(user_template.replace(
                "{{MSG}}", message['human']), unsafe_allow_html=True)

        st.write(bot_template.replace(
                "{{MSG}}", message['gemini']), unsafe_allow_html=True)


def main():
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
    # gemini_model = genai.GenerativeModel(model_name = "gemini-pro")
    gemini_model = ChatGoogleGenerativeAI(model="gemini-pro")
    
    cv_document = document_loaders.Docx2txtLoader("Prasanga_CV_DE_3_24.docx")
    cv_document = cv_document.load()[0].page_content

    st.set_page_config(page_title="Ask-Prasanga",
                       page_icon=":desktop_computer:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    


    st.header("Ask any questions you would like to know about Prasanga's career.")
    user_question = st.text_input("Example question: Where is Prasanga currently working at?")

    with st.sidebar:
        st.header(r"$\textsf{\huge Ask-Prasanga}$")
        st.subheader('  :computer: Personal Chat Assistant :computer:')
        st.markdown("""---""")
        st.subheader("This is an AI-powered personalized chatbot developed by Prasanga Neupane, specifically curated to answer queries regarding Prasanga's professional career. This chatbot utilizes Google's Gemini-Pro LLM to generate responses.")
        st.write("  If you would like to verify the authenticity of the generated responses, please feel free to visit Prasanga's :linked_paperclips: [Linkedin](%s) profile." %"https://www.linkedin.com/in/prasanga-neupane/")
        st.write("---")
        st.write(":copyright: Developed by Prasanga Neupane, 2024")

    if user_question:

        prompt_parts = f"Here is the resume of Prasanga Neupane inside ticks.`{cv_document}`.Based on his resume, answer the following question inside ticks.`{user_question}`. Provide example(s) from resume when possible. Do not make your own answers outside of given resume.If you dont find answer wihtin the given resume, reply with 'Sorry. I do not have that information. Please try to keep your questions around Prasanga's career.'"

        handle_userinput(prompt_parts, gemini_model, user_question)
    


if __name__ == '__main__':
    main()