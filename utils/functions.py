import streamlit as st
import base64
import tiktoken


def display_pdf(file_path: str):
    """
    Function to display PDF that exists on disk
    """
    with open(file_path,"rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width=100% height="550" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def ensure_token_limit(docs: list) -> tuple[list, int, int]:
    """
    Function to discard retrieved docs one by one if token limit is exceeded

    Args:
        docs (list): List of 4 retrieved chunks (langchain.schema.document.Document items)
    Returns:
        docs (list): List of the accepted docs (langchain.schema.document.Document items) after filtering to ensure that token limit is not exceeded
        retrieved_docs_len (int): Total num of the chars in the 4 initial docs
        docs_len (int): Total num of the chars in the returned accepted docs
    """

    # Calculate initial doc len in chars
    total_ch = ""
    for doc in docs:
        total_ch = total_ch + doc.page_content
        retrieved_docs_len = len(total_ch)

    # Do not exceed 13000 tokens (out of the 16k max)
    # leave 3000 for prompt (QP=550 + CQP=115 + user question + history = ~1000) 
    # and answer (length variable)
    docs_len = 60000
    while ((docs_len / 7.5) * 2) >= 13000:
        total_chars = ""
        for doc in docs:
            total_chars = total_chars + doc.page_content
        docs_len = len(total_chars)
        print(f"With {len(docs)} docs, the lenght is:", docs_len)
        print()
        # if tokens > 14000
        if ((docs_len / 7.5) * 2) >= 13000:
            # drop last doc:
            # docs.pop()

            # drop longest doc:

            # get the page_content string in a list
            doc_items = []
            for doc in docs:
                doc_items.append(doc.page_content)
            # map each string to its index in a dict
            doc_dict = {}
            for idx, string in enumerate(doc_items):
                doc_dict[string] = idx
            # sort the strings by length
            sorted_list = sorted(doc_items, key=len)
            # find the longest string (i.e. the last)
            longest = sorted_list[-1]
            # find index of this longest string from the doc_dict
            idx_to_pop = doc_dict[longest] 
            # pop the item and that index from docs
            docs.pop(idx_to_pop)

    return docs, retrieved_docs_len, docs_len


def get_variables_for_prompt(input_docs: list, category: str) -> tuple[list, list]:
    """
    Function to extract prompt variables (chunk texts and metadata) from retrieved/accepted docs
    
    Args:
        input_docs (list): List of the accepted docs (langchain.schema.document.Document items)
        category (str): "SmPC" or "leaflet" or "PDF
    Returns:
        docs (list): Each item of the list is the text (str) of one of the accepted docs
        metadata (list): Each item of the list is the corresponding metadata (Chatper or Page number)
    """

    docs = []
    metadata = []

    # SmPC docs split by chapter
    if category == "SmPC":

        # Fewer than 4 docs may be retrieved
        if len(input_docs) == 1:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["Chapter"])
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")

        elif len(input_docs) == 2:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["Chapter"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["Chapter"])
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")
        
        elif len(input_docs) == 3:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["Chapter"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["Chapter"])
            docs.append(input_docs[2].page_content)
            metadata.append(input_docs[2].metadata["Chapter"])
            docs.append("")
            metadata.append("")

        elif len(input_docs) == 4:

            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["Chapter"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["Chapter"])
            docs.append(input_docs[2].page_content)
            metadata.append(input_docs[2].metadata["Chapter"])
            docs.append(input_docs[3].page_content)
            metadata.append(input_docs[3].metadata["Chapter"])

    # if not smpc, then leaflet (split by page)
    elif category == "leaflet" or category == "PDF":

        # Fewer than 4 docs may be retrieved
        if len(input_docs) == 1:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["page"])
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")

        elif len(input_docs) == 2:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["page"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["page"])
            docs.append("")
            metadata.append("")
            docs.append("")
            metadata.append("")
        
        elif len(input_docs) == 3:
            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["page"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["page"])
            docs.append(input_docs[2].page_content)
            metadata.append(input_docs[2].metadata["page"])
            docs.append("")
            metadata.append("")

        elif len(input_docs) == 4:

            # Assign docs and metadata to variables
            docs.append(input_docs[0].page_content)
            metadata.append(input_docs[0].metadata["page"])
            docs.append(input_docs[1].page_content)
            metadata.append(input_docs[1].metadata["page"])
            docs.append(input_docs[2].page_content)
            metadata.append(input_docs[2].metadata["page"])
            docs.append(input_docs[3].page_content)
            metadata.append(input_docs[3].metadata["page"])

    return docs, metadata


def count_doc_tokens(docs: list, model_name: str) -> int:
    """
    Function to count the total num of tokens of the accepted docs (i.e. the remaining docs/chunks after filtering that will be passed to the prompt)

    Args:
        docs (list): List of the accepted doc texts (str), i.e. after get_variables_for_prompt() was run
        model_name (str): the LLM model name
    Returns:
        doc_token_count (int): the total num of tokens of the accepted docs
    """

    encoding = tiktoken.encoding_for_model(model_name)

    doc_token_count = 0
    for doc in docs:
        tokens = encoding.encode(doc)
        doc_token_count = doc_token_count + len(tokens)

    return doc_token_count