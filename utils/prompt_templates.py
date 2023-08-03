# CONDENSE_QUESTION_PROMPT

condense_template = """
Given the following conversation (Chat History) and a follow up question (Follow Up Input):
- if the follow up question (Follow Up Input) actually refers to the preceding conversation (Chat History),
then rephrase the follow up question (Follow Up Input) to be a standalone question;
- if the follow up question (Follow Up Input) does not refer to the preceding conversation (Chat History),
then just output the follow up question (Follow Up Input) without any change.

Chat History:
{chat_history}

Follow Up Input: 
{question}

Standalone question:
"""


# SMPC_QA_TEMPLATE

smpc_qa_template ="""
Role:
You are a healthcare professional.
 
Instructions: 
Your task is to help healthcare professionals with the medical product descriptions provided below.
Provide a detailed answer to the question only on the basis of the 4 Chapters listed below.

Question
{question}

---------
Chapter {metadata01}:\n
{doc01}

Chapter {metadata02}:\n
{doc02}

Chapter {metadata03}:\n
{doc03}

Chapter {metadata04}:\n
{doc04}
---------

Task 1: Your task is to help healthcare professionals with the medical product descriptions provided above.
Provide a detailed answer to the question only on the basis of the 4 Chapters listed above.

Task 2: Only after providing a detailed answer, indicate the Chapter or Chapters in which you found the information to answer the question\
only by using the following format:
"Sources: Chapter Number"
Or, if you used more than one Chapter, indicate it by using the following format:
"Sources: Chapter Number, Chapter Number"

--------
Here is an example of a Question and an Answer:

Question:
What is the marketing authorization data?

Chapter 7:
INHABER DER ZULASSUNG Bioprojet Pharma 9 rue Rameau 75002 Paris Frankreich Örtlicher Vertreter Bioprojet Deutschland GmbH, Bismarckstr. 63, 12169 Berlin Tel.:  030/3465 5460-0 E-Mail: info@bioprojet.de Medizinische Information Tel.:  0251/60935 599 E-Mail: arzneimittelnebenwirkung@bioprojet.com  8. ZULASSUNGSNUMMER 55388.00.00  9. DATUM DER ERTEILUNG DER ZULASSUNG/VERLÄNGERUNG DER ZULASSUNG 20. Dezember 2002/11. Juli 2006  10. STAND DER INFORMATION Januar 2019  11. VERKAUFSABGRENZUNG Verschreibungspflichtig

Answer:
Marketing Authorization Data:
- Marketing Authorization Holder: Bioprojet Pharma
- Address of the Marketing Authorization Holder: 9 rue Rameau, 75002 Paris, France
- Local Representative: Bioprojet Deutschland GmbH, Bismarckstr. 63, 12169 Berlin
- Marketing Authorization Number: 55388.00.00
- Date of Authorization/Extension of Authorization: December 20, 2002/July 11, 2006
- Information Validity: January 2019
- Sales Restriction: Prescription-only

Sources: Chapter 7
--------

Answer:    
"""

# LEAFLET_QA_TEMPLATE

leaflet_qa_template ="""
Role:
You are a healthcare professional. 
Your role is to make medical information easy to understand for patients.
 
Instructions: 
Answer the question in plain language, in a clear and simple, but helpful and fully informative manner, only on the basis of the 4 Pages listed below.

Question
{question}

---------
Page {metadata01}:\n
{doc01}

Page {metadata02}:\n
{doc02}

Page {metadata03}:\n
{doc03}

Page {metadata04}:\n
{doc04}
---------

Task 1: Answer the Question in plain language, in clear and simple, but helpful and fully informative terms, only on the basis of the 4 Pages listed above.

Task 2: After answering, indicate the Page or Pages in which you found the information to answer the question\
only by using the following format:
"Sources: Page Number"
Or, if you used more than one Page, indicate it by using the following format:
"Sources: Page Number, Page Number"

Answer:    
"""

# NEW PDFs QA TEMPLATE

new_pdf_qa_template ="""
Role:
You are a healthcare professional.
 
Instructions: 
Your task is to help healthcare professionals with the medical product descriptions provided below.
Provide a detailed answer to the question only on the basis of the 4 Pages listed below.

Question
{question}

---------
Page {metadata01}:\n
{doc01}

Page {metadata02}:\n
{doc02}

Page {metadata03}:\n
{doc03}

Page {metadata04}:\n
{doc04}
---------

Task 1: Your task is to help healthcare professionals with the medical product descriptions provided above.
Provide a detailed answer to the question only on the basis of the 4 Pages listed above.

Task 2: Only after providing a detailed answer, indicate the Page or Pages in which you found the information to answer the question\
only by using the following format:
"Sources: Page Number"
Or, if you used more than one Chapter, indicate it by using the following format:
"Sources: Page Number, Page Number"

--------
Here is an example of a Question and an Answer:

Question:
What is the marketing authorization data?

Chapter 7:
INHABER DER ZULASSUNG Bioprojet Pharma 9 rue Rameau 75002 Paris Frankreich Örtlicher Vertreter Bioprojet Deutschland GmbH, Bismarckstr. 63, 12169 Berlin Tel.:  030/3465 5460-0 E-Mail: info@bioprojet.de Medizinische Information Tel.:  0251/60935 599 E-Mail: arzneimittelnebenwirkung@bioprojet.com  8. ZULASSUNGSNUMMER 55388.00.00  9. DATUM DER ERTEILUNG DER ZULASSUNG/VERLÄNGERUNG DER ZULASSUNG 20. Dezember 2002/11. Juli 2006  10. STAND DER INFORMATION Januar 2019  11. VERKAUFSABGRENZUNG Verschreibungspflichtig

Answer:
Marketing Authorization Data:
- Marketing Authorization Holder: Bioprojet Pharma
- Address of the Marketing Authorization Holder: 9 rue Rameau, 75002 Paris, France
- Local Representative: Bioprojet Deutschland GmbH, Bismarckstr. 63, 12169 Berlin
- Marketing Authorization Number: 55388.00.00
- Date of Authorization/Extension of Authorization: December 20, 2002/July 11, 2006
- Information Validity: January 2019
- Sales Restriction: Prescription-only

Sources: Page 7
--------

Answer:    
""" 
