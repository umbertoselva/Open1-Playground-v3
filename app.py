import streamlit as st

import datetime
import random
import string

# Patch for the "AttributeError: module 'langchain' has no attribute 'verbose'" issue
import langchain
langchain.verbose = False

from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain import FAISS
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

from utils.prompt_templates import condense_template, smpc_qa_template, leaflet_qa_template, new_pdf_qa_template
from utils.functions import display_pdf, ensure_token_limit, get_variables_for_prompt, count_doc_tokens
from utils.chains import chain


# STREAMLIT APP

# SETUP

# Hide Streamlit upper right menu and "Made with Streamlit" bottom label
hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
<style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

unix_timestamp = str(datetime.datetime.now()) # str(time.time()) # Used for ChatID
model_name = 'gpt-3.5-turbo-16k'
temperature = 0.0

# Initialize session objects
if "previous_pdf" not in st.session_state:
    st.session_state["previous_pdf"] = "anapen_smpc"
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []
if "cb" not in st.session_state:
    st.session_state["cb"] = None

# Session states for buttons
if "thumbs_down" not in st.session_state:
    st.session_state.thumbs_down = 0
if "chat" not in st.session_state:
    st.session_state.chat = ""
if "download" not in st.session_state:
    st.session_state.download = False

# Functions for buttons 
def thumbs_down():
    st.session_state.thumbs_down = 1
def download():
    st.session_state.download = True


# DISPLAY STREAMLIT APP

# st.write(st.session_state)

# SIDEBAR - Select and display PDF
with st.sidebar:

    st.image(
        image="img/large-Logo-pharmazie-com.png",
        width=250
    )

    pdf = st.selectbox(
        label="Select PDF file:",
        options=["anapen_smpc", "atacand_smpc", "inhixa_smpc", "roctavian_smpc",
                    "anapen_leaflet", "atacand_leaflet", "inhixa_leaflet", "roctavian_leaflet",
                    "4878975 BPZ Vitamin D Test", "4879012 BPZ Eisenmangel Test", 
                    "4879029 BPZ Lebensmittelreaktions Test", "4879035 BPZ Vitamin B12 Test", "4879035 Vitamin B12 Test",
                    "docViewer_blaueHandArzt", "docViewer_blaueHandPatient", 
                    "docViewer_blaueHandPatientenKarte"],
        index=0,
        key="pdf",
        label_visibility="visible"
    )
        
# If the user selects a PDF (default = anapen_smpc)
if pdf:

    # If the user has selects a different pdf
    if pdf != st.session_state.previous_pdf:
        # Set newly selected pdf in session state
        st.session_state.previous_pdf = pdf
        # Reset chat
        st.session_state["generated"] = []
        st.session_state["past"] = []
        st.session_state["history"] = []
        st.session_state["cb"] = []
        st.session_state["thumbs_down"] = 0
        st.session_state["chat"] = ""
        st.session_state["download"] = False

    with st.sidebar:

        # Set category

        if pdf[-4:] == "smpc":
            category = "SmPC"
            type = "Fachinformation"
            name = pdf[:-5].capitalize()
        elif pdf[-7:] == "leaflet":
            category = "leaflet"
            type = "Packungsbeilage"
            name = pdf[:-8].capitalize()
        else:
            category = "PDF"
            type = "Information"
            name = pdf

        # Load PDF to display
        
        # Display PDF from appropriate category
        display_pdf(f"pdf/{category}/{pdf}.pdf") # https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/pdf/{category}/{pdf}.pdf

        # Load vectorstore corresponding to pdf
        vectorstore = FAISS.load_local(
                folder_path=f"db/{category}",
                embeddings=embeddings,
                index_name=pdf
            )


    # MAIN CHATBOT

    if vectorstore:

        st.markdown("### :blue[Willkommen beim neuen KI-basierten Co-Piloten von Pharmazie.com]")

        # Initial info message (displayed in a blue bar)
        # intro_info = f"You are chatting with the {category} documentation for {name}"
        intro_info = f"Sie sind im Chat mit der {type} für {name}"
        st.info(intro_info)

        # Display chatbot in main area
        user_input = st.chat_input(
            # placeholder="Please type your question here.",
            placeholder="Fragen Sie mich etwas....",
            key="user_input"
        ) # N.B. st.chat_input can only be used in the main area of the screen (not in cols etc.)

        # Welcome message
        if category == "SmPC":
            st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png")
            welcome_msg.write(f"Wie kann ich Ihnen helfen?\n\
                              \n- Was sind die Nebenwirkungen dieses Produkts?\
                              \n- Wie lauten die Zulassungsinformationen für dieses Produkt?\
                              \n- Was sind die Anwendungsgebiete dieses Arzneimittels?\
                              \n- Wie wird es dosiert?")
            # welcome_msg.write(f"Hello, I am Pharmazie.com's AI assistant, I am here to assist you with {name}'s {category} documentation.\
            #         How can I help you?\
            #         \nPlease state your question clearly and provide detailed instructions.\
            #         \nIf I fail to provide a satisfactory answer, please rephrase your question and try again.\n\
            #         \nSuggested questions:\n- What are the side effects of this product?\n- What is the marketing authorisation information for this product?")
        elif category == "leaflet":
            st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png")
            welcome_msg.write(f"Wie kann ich Ihnen helfen?\n\
                              \n- Wie und wann soll ich das Produkt einnehmen?\
                              \n- Darf ich es mit Alkohol einnehmen?\
                              \n- Darf ich damit Autofahren?\
                              \n- Was soll ich tun, wenn ich die Einnahme vergessen habe?")
            # welcome_msg.write(f"Hello, I am Pharmazie.com's AI assistant, I am here to assist you with {name}'s {category} documentation.\
            #         How can I help you?\
            #         \nPlease state your question clearly and provide detailed instructions.\
            #         \nIf I fail to provide a satisfactory answer, please rephrase your question and try again.\n\
            #         \nSuggested questions:\n- What are the side effects of this product?\n- How and when should I take this product?")
        elif category == "PDF":
            st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png")
            welcome_msg.write(f"Wie kann ich Ihnen helfen?\n\
                              \n- Wie soll ich das Produkt anwenden?\
                              \n- Was ist das?\
                              \n- Wie hilft es mir?")
            # welcome_msg.write(f"Hello, I am Pharmazie.com's AI assistant, I am here to assist you with {name}'s {category} documentation.\
            #         How can I help you?\
            #         \nPlease state your question clearly and provide detailed instructions.\
            #         \nIf I fail to provide a satisfactory answer, please rephrase your question and try again.")        

        # BUTTON CODE ----------------------------------------------------------------------------------------------------
        # Whenever a button is pressed on Streamlit, the whole app re-runs
        # So all the displayed chat message would dissapear.
        # The following code is meant to re-display the chat, after a button is pressed, and the app is re-run.

        # If thumbs down button was pressed during the previous run     
        if st.session_state.thumbs_down == 1:
            
            # Display chat messages again
            if st.session_state["generated"]:

                for i in range(len(st.session_state["generated"])):

                    # display user question
                    with st.chat_message("user"):
                        st.write(st.session_state["past"][i])                            

                    # display the output generated by the chatbot
                    with st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png"):
                        st.write(st.session_state["generated"][i])
                
                # reset rating to 0
                st.session_state.thumbs_down = 0

                # Set columns to display buttons after the chat messages
                col1, col2, col3 = st.columns([1, 0.3, 0.1])

                # Display buttons
                with col2:
                        st.download_button('Download Chat', 
                                        data=intro_info + "\n\n" + unix_timestamp[:-7] + "\n\n" + st.session_state.chat,
                                        file_name=f"{unix_timestamp[:-7]} chat.txt",
                                        on_click=download,
                                        key=random.choices(string.ascii_uppercase, k=8))

                with col3:
                        st.button("👎", on_click=thumbs_down, key=random.choices(string.ascii_uppercase, k=8))
                
                # Display message to confirm that feedback was sent
                # st.info("Thank you for you feedback.")
                st.info("Vielen Dank für Ihr Feedback")

        # If download button was pressed during previous run
        if st.session_state.download == True:
            
            # Display chat messages again
            if st.session_state["generated"]:

                for i in range(len(st.session_state["generated"])):

                    # display user question
                    with st.chat_message("user"):
                        st.write(st.session_state["past"][i])                            

                    # display the output generated by the chatbot
                    with st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png"):
                        st.write(st.session_state["generated"][i])

                # reset "download" variable to False
                st.session_state.download = False

                # Set columns to display buttons
                col1, col2, col3 = st.columns([1, 0.3, 0.1])

                # Display buttons
                with col2:
                        st.download_button('Download Chat', 
                                        data=intro_info + "\n\n" + unix_timestamp[:-7] + "\n\n" + st.session_state.chat,
                                        file_name=f"{unix_timestamp[:-7]} chat.txt", 
                                        on_click=download,
                                        key=random.choices(string.ascii_uppercase, k=8))

                with col3:
                        st.button("👎", on_click=thumbs_down, key=random.choices(string.ascii_uppercase, k=8))

        # END of BUTTON CODE -------------------------------------------------------------------------------------------


        # Generate output upon user input
        if user_input:

            # with st.sidebar:
            #     # Display PDF from appropriate category
            #     display_pdf(f"pdf/{category}/{pdf}.pdf")

            # Store user question in session state for logging in case the thumbs-down button is pressed
            st.session_state.question = user_input

            # Display spinner and then chat
            with st.spinner("Generating response..."):

                # Set prompt
                if category == "SmPC":
                    qa_template = smpc_qa_template
                elif category == "leaflet":
                    qa_template = leaflet_qa_template
                elif category == "PDF":
                    qa_template = new_pdf_qa_template

                # Debug
                print("PDF:", pdf)
                print()
                print("File category / Prompt type:", category)
                print()
                print("User question:", user_input)
                print()
                print("Vectorstore:", vectorstore)
                print()

                # Retrieve docs
                docs = vectorstore.similarity_search(
                    query=user_input, 
                    k=4
                )  

                # Fewer than 4 docs might actually be retrieved
                retrieved_docs = len(docs)

                print("Number of retrieved docs:", len(docs))
                print()

                # Do not exceed 13000 tokens (leave 3000 for prompt (~550) and answer) 
                # Drop longest doc (one by one) if this limit is exceeded 
                docs, retrieved_docs_len, accepted_docs_len = ensure_token_limit(docs)

                # Number of accepted docs
                num_accepted_docs = len(docs)

                # Debug
                print("Retrieved docs len:", retrieved_docs_len)
                print()
                print("Number of accepted docs:", len(docs))
                print()
                print("Accepted docs len:", accepted_docs_len)
                print()
                
                # Save retrieved docs in variables for the prompts
                docs, metadata = get_variables_for_prompt(docs, category)

                # Calculate docs tokens
                doc_token_count = count_doc_tokens(docs, model_name)
                print("Doc token count:", doc_token_count)
                print()

                # Build prompts 
                QA_PROMPT = PromptTemplate(template=qa_template, 
                                        input_variables=["question", \
                                                            "doc01", "doc02", "doc03", "doc04", \
                                                            "metadata01", "metadata02", "metadata03", "metadata04"])
                CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_template)

                # Generate output

                # Track tokens and costs
                with get_openai_callback() as cb:
                    
                    # run chain
                    answer, condensed_question = chain(
                        model_name=model_name,
                        temperature=temperature,
                        QA_PROMPT=QA_PROMPT,
                        CONDENSE_QUESTION_PROMPT=CONDENSE_QUESTION_PROMPT,
                        chat_history=st.session_state['history'],
                        question=user_input,
                        docs=docs,
                        metadata=metadata
                    )

                # Debug output
                print()
                print("Model output:", answer)
                print()
                print("Condensed question:", condensed_question)
                print()

                # Debug retrieved documents
                if category == "SmPC":
                    print(f"Document 01, Chapter {metadata[0]}:", docs[0])
                    print()
                    print(f"Document 02, Chapter {metadata[1]}:", docs[1])
                    print()
                    print(f"Document 03, Chapter {metadata[2]}:", docs[2])
                    print()
                    print(f"Document 04, Chapter {metadata[3]}:", docs[3])
                    print()
                elif category == "leaflet" or category == "PDF":
                    print(f"Document 01 at page {metadata[0]}:", docs[0])
                    print()
                    print(f"Document 02 at page {metadata[1]}:", docs[1])
                    print()
                    print(f"Document 03 at page {metadata[2]}:", docs[2])
                    print()
                    print(f"Document 04 at page {metadata[3]}:", docs[3])
                    print()
        
                # Debug token count and costs
                print(cb)
                print()

                # Update session states
                st.session_state.past.append(user_input)
                st.session_state.generated.append(answer)
                st.session_state.history.append((user_input, answer))
                st.session_state.cb = cb
                # st.session_state.msg_counter += 1
                st.session_state.chat = str(st.session_state.history).strip('[]')

                # Display chat
                if st.session_state["generated"]:

                    for i in range(len(st.session_state["generated"])):

                        # display user question
                        with st.chat_message("user"):
                            st.write(st.session_state["past"][i])                            

                        # display the output generated by the chatbot
                        with st.chat_message("assistant", avatar="https://raw.githubusercontent.com/umbertoselva/Open1-Playground-v3/main/img/logo-icon.png"):
                            st.write(st.session_state["generated"][i])

                    # Set columns to display buttons
                    col1, col2, col3 = st.columns([1, 0.3, 0.1])

                    # Display buttons
                    with col2:
                        st.download_button('Download Chat', 
                                        data=intro_info + "\n\n" + unix_timestamp[:-7] + "\n\n" + st.session_state.chat,
                                        file_name=f"{unix_timestamp[:-7]} chat.txt",
                                        on_click=download,
                                        key=random.choices(string.ascii_uppercase, k=8))
                    with col3:
                        st.button("👎", on_click=thumbs_down, key=random.choices(string.ascii_uppercase, k=8))
                    

                
