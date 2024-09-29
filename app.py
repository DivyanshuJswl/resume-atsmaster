import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini Pro Response
def get_gemini_response(input):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input)
    return response.text

# Extract and concatenate text from all pages of the given PDF file
def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

with open(".streamlit/config.toml", "rb") as f:
    content = f.read()
content = content.decode('utf-8-sig')
with open(".streamlit/config.toml", "w", encoding='utf-8') as f:
    f.write(content)

input_prompt = """
Hey, act like a skilled ATS (Applicant Tracking System) with a deep understanding of the tech field, including software engineering, data science, data analysis, and big data engineering. Your task is to evaluate the resume based on the given job description. 
The job market is very competitive, so you should provide the best guidance for improving the resume.

Evaluate based on these factors:
1. Relevance to job description.
2. Matching skills/keywords from the resume against the job description.
3. Provide suggestions for missing or weak areas.

Assign the percentage match based on the job description and highlight the missing keywords with high accuracy. Also, provide a brief profile summary.

The response should be formatted as a JSON-like string with the following structure:

{{
    "JD_Match_Percentage": "XX%",
    "Missing_Keywords": ["keyword1", "keyword2", ...],
    "Profile_Summary": "Brief summary of the candidate's qualifications and fit for the role.",
    "Evaluation_Explanation": "A short explanation of how the match percentage was derived and the key areas for improvement."
}}

resume: {text}
job description: {jd}
"""

## streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")

# if submit:
#     if uploaded_file is not None:
#         text=input_pdf_text(uploaded_file)
#         response=get_gemini_response(input_prompt)
#         st.subheader(response)

if submit:
    if uploaded_file:
        text = input_pdf_text(uploaded_file)
        # Get the response from Gemini Pro
        response_text = get_gemini_response(input_prompt)
        # Parse the response text to JSON
        try:
            response_json = json.loads(response_text)
            # Display each component in a structured manner
            st.subheader("ATS Evaluation Results")
            # Display the match percentage
            st.metric(label="Job Description Match", value=f"{response_json['JD_Match_Percentage']}")
            # Show the missing keywords
            st.subheader("Missing Keywords")
            st.write(", ".join(response_json["Missing_Keywords"]))
            # Show profile summary
            st.subheader("Profile Summary")
            st.write(response_json["Profile_Summary"])
            # Show evaluation explanation
            st.subheader("Evaluation Explanation")
            st.write(response_json["Evaluation_Explanation"])

        except json.JSONDecodeError:
            st.error("Error: Could not parse the ATS response. Please try again.")