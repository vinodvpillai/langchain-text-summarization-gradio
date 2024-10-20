from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader

import gradio as gr

import os
from os.path import join, dirname
from dotenv import load_dotenv



# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# LLM
llm = ChatOpenAI(temperature=0, model=os.environ.get('OPENAI_MODEL'), api_key=os.environ.get('OPENAI_API_KEY'))  # type: ignore

# Define the prompt template for summarization
prompt_template = """You are an expert at summarizing complex documents. I will provide you with a document and a summary length preference. Your task is to generate a coherent and contextually accurate summary based on the provided length type. The summary length can be either Short, Medium, or Long. Here is how you should handle each type:
- Short: Provide a concise overview in 1-2 sentences focusing on the most essential points.
- Medium: Create a summary in 3-5 sentences covering the key aspects while maintaining brevity.
- Long: Write a comprehensive summary in 1-2 paragraphs, ensuring all important details are included.

### Inputs:
1. Document: {document}
2. Summary Type: {summary_type}

Please generate the summary accordingly.
"""
prompt = PromptTemplate(
    input_variables=["document", "summary_type"],
    template=prompt_template,
)

# Output Parser
output_parser=StrOutputParser()

# Chain to handle the model and prompt
summarization_chain = prompt | llm | output_parser

# Function to handle file uploads or text summarization
def summarize_text(document, summary_type, text_input=None):
    # If a file is uploaded, process it
    if document:
        # Using PyPDFLoader for PDF, can extend to other document formats
        loader = PyPDFLoader(document.name)
        pages = loader.load_and_split()

        # Concatenate all pages' content into one string
        full_text = " ".join([page.page_content for page in pages])
    elif text_input:
        # If text is input directly
        full_text = text_input
    else:
        return "Please provide either a document or text for summarization."
    
    # Pass the document to the summarization chain with the selected summary type
    summary = summarization_chain.invoke(input={'document': full_text, 'summary_type': summary_type})
    
    return summary

# Gradio UI
def main():
    with gr.Blocks() as app:
        gr.Markdown("## Document Summarization Application")
        
        # Let users select whether they want to upload a document or input text
        with gr.Row():
            with gr.Column():
                document = gr.File(label="Upload Document")
                text_input = gr.Textbox(label="Or Enter Text Manually")
        
        # Let users select the summary type (short, medium, long)
        summary_type = gr.Radio(
            choices=["short", "medium", "long"], 
            label="Select Summary Type",
            value="short"
        )
        
        # Output section
        output = gr.Textbox(label="Summarized Output", interactive=False)
        
        # Button to trigger summarization
        summarize_button = gr.Button("Summarize")

        # Define button action to call the `summarize_text` function
        summarize_button.click(
            fn=summarize_text, 
            inputs=[document, summary_type, text_input], 
            outputs=output
        )
        
    # Launch the Gradio app
    app.launch()

# Run the application
if __name__ == "__main__":
    main()
