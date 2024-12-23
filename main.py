import os
from dotenv import load_dotenv
import langchain.document_loaders as document_loaders
import streamlit as st
from htmlTemplates import css, bot_template, user_template
from langchain_google_genai import ChatGoogleGenerativeAI
import boto3
from datetime import datetime, timezone

def write_to_s3(response, user_question):
    s3 = boto3.resource(
    's3',
    region_name='us-east-1',
    aws_access_key_id=os.environ["S3_KEY"],
    aws_secret_access_key=os.environ["S3_ACCESS_KEY"]
    )
    local_time_now = datetime.now(timezone.utc).astimezone().strftime("%m_%d_%Y_%H_%M_%S")
    content= "Human:: " + user_question + "\nBot:: " + response
    s3.Object('ask-prasanga-stream', f'qna-logs/{local_time_now}.txt').put(Body=content)


def handle_userinput(prompt, gemini_model, query):
    # response = gemini_model.generate_content(user_question).text
    try:
        response = gemini_model.invoke(prompt).content
    except Exception as error:
        response = """
        Sorry, I am unable to connect to the Gemini server right now!!! <br><br>
        I will let Prasanga know about this issue ASAP.
        Please feel free to contact him with your queries at 'akaprasanganeupane@gmail.com'.
        """
        print("Error::", error)
    # print(response)
    # response = "hello there!"
    try:
        write_to_s3(response, query)
    except Exception as error:
        print("Failed to write in S3.", error)    

    st.session_state.chat_history.append({'human':query, 'gemini':response})
    # print("Chat history::",st.session_state.chat_history)


def clear_conversation():
    st.session_state["text_input_box"] = ""
    st.session_state.clear()

def create_prompt(cv_document, user_question):
    prompt_parts = f"""
    You are an expert on Prasanga Neupane's carrrer and here is his resume inside triple # signs.

    ### RESUME START ###
    {cv_document}
    ### RESUME END ###

    Based on his resume above, answer the following question inside ticks `{user_question}`.
    ### INSTRUCTIONS FOR ANSWERING QUESTIONS ### 
    1) Always provide relevant exmaples and details from resume while providing response but avoid using terms like based on his resume.
    2) If user asks question using the 'You' pronoun, answer on behalf of Prasanga. For example:
        Q: Do you have any LLM experience?
        A: Yes, Prasanga has LLM experience and <fill in the details from resume here>
    3) Do not use "I" as a first person noun while replying, always use "Prasanga".
    4) While answering questions always include relevant experiences or example from resume in the response. For example:
        Q: Does Prasanga has any LLM experience?
        A: Yes. He implemented <relevant LLM project(s) from resume here>
    5) Do not make your own answers outside of given resume.If you dont find answer within the given resume,
    reply with this exact statement "Sorry. I do not have that information. Please try to keep your questions around Prasanga's career. \n If you need to reach out to Prasanga with this question feel free to reach out to him at 'akaprasanganeupane@gmail.com'."
    6) Do not wrap your responses with ticks(`) or quotes(', ").
    7) Try to respond back in natural language so that its pleasing for the user to read. Please use <br> instead of new line in response.
    """
    return prompt_parts

def main():
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
    # gemini_model = genai.GenerativeModel(model_name = "gemini-pro")
    gemini_model = ChatGoogleGenerativeAI(model="gemini-pro")
    cv_document = document_loaders.Docx2txtLoader("Prasanga_CV_DE_8_19.docx")
    cv_document = cv_document.load()[0].page_content

    st.set_page_config(page_title="Ask-Prasanga",
                       page_icon=":desktop_computer:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    


    st.header("Ask any questions you would like to know about Prasanga's career.")

    with st.form('chat_input_form'):
        col1, col2 = st.columns([7, 1], vertical_alignment="bottom", border=False)
        with col1:
            user_question = st.text_input("Example question: Where is Prasanga currently working at?", value="", key="text_input_box", label_visibility="visible")
            if st.session_state.chat_history and user_question == st.session_state.chat_history[-1]["human"]: # checking duplicate questions
                user_question = None
        with col2:
            submitted  = st.form_submit_button('Send')
        if user_question and submitted:
            prompt = create_prompt(cv_document=cv_document, user_question=user_question)
            handle_userinput(prompt=prompt, gemini_model=gemini_model, query=user_question)

    st.button("Clear Conversation", key="click_button_1", on_click=clear_conversation)

    with st.sidebar:
        st.header(r"$\textsf{\huge Ask-Prasanga}$")
        st.subheader('  :computer: Personal Chat Assistant :computer:')
        st.markdown("""---""")
        st.subheader("This is an AI-powered personalized chatbot developed by Prasanga Neupane, specifically curated to answer queries regarding Prasanga's professional career. This chatbot utilizes Google's Gemini-Pro LLM to generate responses.")
        st.write("  If you would like to verify the authenticity of the generated responses, please feel free to visit Prasanga's :linked_paperclips: [Linkedin](%s) profile." %"https://www.linkedin.com/in/prasanga-neupane/")
        st.write("---")
        st.write(":copyright: Developed by Prasanga Neupane, 2024")
    
    for i, message in enumerate(list(reversed(st.session_state.chat_history))):

        st.write(user_template.replace(
                "{{MSG}}", message['human']), unsafe_allow_html=True)

        st.write(bot_template.replace(
                "{{MSG}}", message['gemini']), unsafe_allow_html=True)
    
if __name__ == '__main__':
    main()