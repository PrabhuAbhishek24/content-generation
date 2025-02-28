import streamlit as st
import requests
from fpdf import FPDF
from docx import Document
import openai
import PyPDF2
from docx.shared import Inches
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import zipfile
import os
from pathlib import Path
import csv


# Access keys from Streamlit Secrets
openai.api_key = st.secrets["api"]["OPENAI_API_KEY"]
google_api_key = st.secrets["api"]["GOOGLE_API_KEY"]
custom_search_engine_id = st.secrets["api"]["CUSTOM_SEARCH_ENGINE_ID"]



# Research-related keywords
RESEARCH_KEYWORDS = [
"research", "article", "study", "paper", "journal", "report", "document", "thesis", "dissertation",
    "review", "literature", "source", "abstract", "manuscript", "publication", "findings", "results",
    "investigation", "survey", "exploration", "clinical trial", "experiment", "data analysis",
    "methodology", "results", "hypothesis", "sample study", "case study", "data set", "research method",
    "peer-reviewed", "academic paper", "research paper", "study report", "research proposal", "field study",
    "systematic review", "experimental study", "observational study", "control group", "clinical research",
    "medical research", "pharmaceutical research", "biotech research", "drug development", "drug discovery",
    "experimental design", "epidemiological study", "randomized control trial", "meta-analysis", "biostatistics",
    "computational study", "therapeutic research", "molecular research", "genetic research", "biomedical research",
    "cancer research", "immunology study", "pathophysiology", "translational research", "treatment protocol",
    "medical innovation", "medical device study", "medical trial", "disease research", "pharmacology",
    "pharmacovigilance", "clinical development", "clinical study protocol", "patient safety", "pharmaceutical study",
    "pharmacokinetics", "therapeutic efficacy", "pharmacodynamics", "evidence-based medicine", "drug toxicology",
    "preclinical study", "clinical outcomes", "regulatory affairs", "patent study", "artificial intelligence research",
    "machine learning algorithms", "predictive modeling", "computational biology", "quantum computing research",
    "robotics in medicine", "data mining", "neural networks in pharma", "digital health", "telemedicine research",
    "precision medicine", "genomic research", "biotechnology innovation", "CRISPR technology",
    "wearable health technology",
    "peer-reviewed articles", "research journal", "scientific journal", "academic journal", "medical journal",
    "pharmaceutical journal", "research article", "review article", "open access", "editorial", "article abstract",
    "case report", "journal impact factor", "citation analysis", "scopus indexed", "elsevier", "springer",
    "wiley online library", "doi", "pubmed indexed", "neuroscience research", "cardiology research",
    "oncology research",
    "infectious disease study", "pediatrics research", "geriatrics study", "regenerative medicine",
    "stem cell research",
    "mental health studies", "HIV/AIDS research", "diabetes research", "rare diseases study",
    "autoimmune diseases research",
    "cardiovascular diseases study", "hepatology research", "dermatology study", "orthopedics research",
    "rheumatology research",
    "patent research", "patent application", "patent literature", "patent filing", "intellectual property",
    "patent search",
    "patent documentation", "pharmaceutical patent", "drug patent", "biotechnology patent", "data-driven research",
    "systematic review", "research data", "open science", "data visualization", "collaborative research",
    "research collaboration",
    "research network", "research findings", "literature review", "trial report", "cohort study",
    "cross-sectional study",
    "research grants", "clinical evaluation", "research ethics", "scientific method", "study design",
    "research funding",
    "research institutions", "research organizations", "health policy research", "epidemiology research"

]

# Function to check if a query contains research-related keywords
def is_query_research_related(query):
    for keyword in RESEARCH_KEYWORDS:
        if keyword.lower() in query.lower():
            return True
    return False

# Function to search using Google Custom Search API
def google_custom_search(query):
    url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?q={query}&key={google_api_key}&cx={custom_search_engine_id}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Error fetching data from Google Custom Search"}

# Function to fetch response from GPT
def fetch_gpt_response(query):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in the pharmaceutical and medical domain only. Only answer those questions and don't answer any other questions. Dont analyze and summarize pdf if the pdf is not related to medical and pharmaceutical domain."},
                {"role": "user", "content": query},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text


def save_as_scorm_pdf(content, output_folder="scorm_package", scorm_zip_name="scorm_package.zip"):
    # Step 1: Create the SCORM folder structure
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the PDF
    pdf_file_path = os.path.join(output_folder, "content.pdf")
    save_as_pdf(content, pdf_file_path)

    # Step 2: Create the HTML file
    html_file_path = os.path.join(output_folder, "index.html")
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SCORM Content</title>
        </head>
        <body>
            <h1>Research Content Response</h1>
            <iframe src="content.pdf" width="100%" height="600px"></iframe>
        </body>
        </html>
        """)

    # Step 3: Create the imsmanifest.xml file
    manifest_file_path = os.path.join(output_folder, "imsmanifest.xml")
    with open(manifest_file_path, "w", encoding="utf-8") as manifest_file:
        manifest_file.write(f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
                  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1
                                      http://www.imsglobal.org/xsd/imscp_v1p1.xsd
                                      http://www.adlnet.org/xsd/adlcp_v1p3
                                      http://www.adlnet.org/xsd/adlcp_v1p3.xsd">
            <metadata>
                <schema>ADL SCORM</schema>
                <schemaversion>1.2</schemaversion>
            </metadata>
            <organizations>
                <organization identifier="ORG-1">
                    <title>Research Content</title>
                    <item identifier="ITEM-1" identifierref="RES-1">
                        <title>Research Content Response</title>
                    </item>
                </organization>
            </organizations>
            <resources>
                <resource identifier="RES-1" type="webcontent" href="index.html">
                    <file href="index.html"/>
                    <file href="content.pdf"/>
                </resource>
            </resources>
        </manifest>
        """)

    # Step 4: Zip the SCORM package
    with zipfile.ZipFile(scorm_zip_name, 'w', zipfile.ZIP_DEFLATED) as scorm_zip:
        for foldername, subfolders, filenames in os.walk(output_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, output_folder)
                scorm_zip.write(file_path, arcname)

    # Provide the download button for the SCORM package
    with open(scorm_zip_name, "rb") as scorm_file:
        st.download_button("Download SCORM Package", scorm_file, scorm_zip_name, "application/zip")


def save_as_pdf(content, file_name="response.pdf"):
    pdf = FPDF()
    pdf.add_page()

    # Add the logo
    pdf.image('assets/logo.jpeg', x=10, y=8, w=30)

    # Title of the document
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(30)
    pdf.cell(200, 10, txt="Research Content Response", ln=True, align='C')
    pdf.ln(10)

    # Add content
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, content)

    # Save the PDF
    pdf.output(file_name)


def save_as_scorm_word(content, file_name="scorm_package.zip"):
    # Create an in-memory zip file
    scorm_zip = io.BytesIO()

    with zipfile.ZipFile(scorm_zip, 'w') as zf:
        # Create and add manifest.xml
        manifest_content = """<manifest>
            <metadata>
                <schema>ADL SCORM</schema>
                <schemaversion>1.2</schemaversion>
            </metadata>
            <resources>
                <resource identifier="res1" type="webcontent" href="response.docx">
                    <file href="response.docx"/>
                    <file href="response.html"/>
                </resource>
            </resources>
        </manifest>"""
        zf.writestr("imanifest.xml", manifest_content)

        # Create DOCX file
        docx_buffer = io.BytesIO()
        doc = Document()
        # Add the logo to the Word document
        logo_path = "assets/logo.jpeg"
        if Path(logo_path).is_file():
            doc.add_picture(logo_path, width=Inches(1.5))
        doc.add_paragraph('\n')
        doc.add_paragraph("Research Content Response", style='Heading 1')
        doc.add_paragraph('\n')
        doc.add_paragraph(content)
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        zf.writestr("response.docx", docx_buffer.getvalue())

        # Create HTML file
        html_content = f"""
        <html>
        <head><title>Research Content Response</title></head>
        <body>
        <h1>Research Content Response</h1>
        <p>{content.replace('\n', '<br>')}</p>
        </body>
        </html>
        """
        zf.writestr("index.html", html_content)

    scorm_zip.seek(0)
    return scorm_zip.getvalue()


# Usage in Streamlit
def save_as_scorm_button(content):
    scorm_data = save_as_scorm_word(content)
    st.download_button(
        label="Download SCORM Package",
        data=scorm_data,
        file_name="scorm_package.zip",
        mime="application/zip"
    )


# Function to get response from OpenAI using chat completions (for medical and pharma queries)
def get_response(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


# Function to fetch medical and pharma-related data from GPT-3
def fetch_medical_pharma_data(query):
    prompt = f"""
    You are an expert in the pharmaceutical and medical domain only. Only answer those questions and don't answer any other questions.
    Please provide reliable and accurate medical and pharmaceutical data related to the following query.
    The data should include at least 15 to 20 entries and be formatted as a CSV for the medical and pharmaceutical domain only.Dont provide csv data of any other domain.
    The data must be accurate and trustworthy.

    Query: {query}

    The result should be in CSV format with headers and rows.
    """
    response = get_response(prompt)
    return response


# Function to create SCORM package
def create_scorm_package(csv_content):
    # Create an in-memory binary stream for the zip file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add the CSV content to the zip file
        zip_file.writestr("medical_pharma_data.csv", csv_content)

        # Add imsmanifest.xml to the zip file
        imsmanifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="scorm_2004" version="1.0">
    <organizations>
        <organization identifier="org_1">
            <title>Medical and Pharma SCORM Package</title>
        </organization>
    </organizations>
    <resources>
        <resource identifier="res_1" type="webcontent" href="index.html">
            <file href="medical_pharma_data.csv"/>
            <file href="index.html"/>
        </resource>
    </resources>
</manifest>"""
        zip_file.writestr("imsmanifest.xml", imsmanifest_content)

        # Add index.html to the zip file
        index_html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Medical and Pharma Data</title>
</head>
<body>
    <h1>Welcome to the Medical and Pharma SCORM Package</h1>
    <p>This package contains reliable medical and pharmaceutical data.</p>
</body>
</html>
"""
        zip_file.writestr("index.html", index_html_content)

    # Rewind the buffer to the beginning
    zip_buffer.seek(0)
    return zip_buffer


def generate_detailed_ppt_content(topic):
    """Generate detailed content for a presentation using GPT."""
    prompt = (
        f"You are an expert in the pharmaceutical and medical domain.Only generate ppt for those queries and dont answer any other queries "
        f"Generate a professional, formal PowerPoint presentation on the topic: '{topic}'. "
        f"1. Include detailed content for each slide, with a proper introduction, key points, examples, and conclusion. "
        f"-. All the slides must contain atleast 4 points and not paragraph (Detailed points)."
        f"2. Ensure all key points are elaborated and written in a formal and organized format. "
        f"3. Use appropriate headings, subpoints, and examples relevant to the medical or pharmaceutical domain. "
        f"4. The structure should include: "
        f"- Title Slide (topic, subtitle, author name placeholder) "
        f"- Introduction Slide (definition and importance of the topic) "
        f"- 4-6 Key Point Slides (elaborated details for each key point) "
        f"- Case Studies/Examples Slide (real-world examples or clinical applications) "
        f"- Conclusion Slide (future implications or summary). "
        f"Output the content for each slide in detail. Do not use vague terms. Be specific and thorough."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical and pharmaceutical domain expert."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def create_professional_ppt(content, topic, file_name="presentation.pptx"):
    """Create a well-formatted professional PowerPoint presentation."""
    ppt = Presentation()

    # Set consistent font styles
    def set_textbox_style(text_frame):
        """Style the textbox content."""
        for paragraph in text_frame.paragraphs:
            paragraph.font.name = "Calibri (Body)"
            paragraph.font.size = Pt(20)
            paragraph.alignment = PP_ALIGN.LEFT

    # Title Slide
    title_slide_layout = ppt.slide_layouts[0]
    slide = ppt.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = topic
    subtitle.text = "A Comprehensive Overview in the Medical and Pharmaceutical Domain"

    # Process GPT content into slides
    sections = content.split("\n\n")
    for section in sections:
        if ":" in section:  # Detect title: content structure
            slide_title, slide_content = section.split(":", 1)

            # Add a new slide for each section
            slide = ppt.slides.add_slide(ppt.slide_layouts[1])
            title = slide.shapes.title
            title.text = slide_title.strip()

            # Add content to the slide
            content_box = slide.placeholders[1]
            content_box.text = slide_content.strip()
            set_textbox_style(content_box.text_frame)

    # Save the presentation
    ppt.save(file_name)
    return file_name

# Streamlit UI
st.set_page_config(page_title="Content and Research Analysis", layout="wide")
st.title("📚 Content Generation And Analysis System")

# Sidebar Navigation
sections = ["About", "Content Generation", "PDF Analysis","CSV Content Generation", "Research Search","PPT Development", "Instructions", "Credits"]
selected_section = st.sidebar.selectbox("Navigation", sections)

if selected_section == "About":
    st.header("📖 About")

    st.info("### 1. What is this application about?")
    st.success(
        "This application integrates OpenAI's GPT-3.5 and Google Custom Search API to provide a seamless platform for "
        "content generation, PDF analysis, CSV data creation, research exploration, and PowerPoint presentation development. "
        "It is specifically designed for the pharmaceutical and medical domains."
    )

    st.info("### 2. What does the Content Generation section offer?")
    st.success(
        "Users can input queries related to pharmaceuticals and medicine to generate detailed content using GPT-3.5. "
        "The content can be downloaded as SCORM packages in PDF or Word formats."
    )

    st.info("### 3. How does the PDF Analysis section work?")
    st.success(
        "Upload a PDF document, extract text from it, and ask questions based on the content. Responses are generated using "
        "GPT-3.5 and can be downloaded as SCORM-compatible files."
    )

    st.info("### 4. What can I do in the CSV Content Generation section?")
    st.success(
        "Generate CSV data for medical and pharmaceutical queries. The CSV files can be packaged and downloaded as SCORM-compatible files."
    )

    st.info("### 5. What features are available in the Research Search section?")
    st.success(
        "Input a research query to fetch results from trusted sources using the Google Custom Search API. Only medically relevant results are displayed for efficiency."
    )

    st.info("### 6. How does the PPT Development section help?")
    st.success(
        "Enter a topic to generate a professionally crafted PowerPoint presentation. Download the PPT directly after content generation."
    )

    st.info("### 7. Who should use this application?")
    st.success(
        "This tool is ideal for medical and pharmaceutical professionals, researchers, and educators who require tailored content generation, "
        "research insights, and analysis tools in their domain."
    )


elif selected_section == "Content Generation":
    st.header("🔍 Content Generation")

    # Input query
    query = st.text_area("Enter your query:", height=200)

    if query:
        # Fetch response
        response = fetch_gpt_response(query)

        # Display response
        st.subheader("Response")
        st.write(response)

        # Display download options
        st.subheader("Download Options")

        # Button to download as SCORM package
        if st.button("Generate the PDF as SCORM Package"):
            save_as_scorm_pdf(response)
            st.success("SCORM package generated. Click the 'Download SCORM Package' button above.")

        if st.button("Generate the Word File as SCORM Package"):
            # Generate the SCORM package for the Word document
            scorm_word = save_as_scorm_word(response, file_name="response.docx")

            if scorm_word:
                # Display success message
                st.success("SCORM package generated. Click the 'Download SCORM Package' button below.")

                # Display the download button
                st.download_button(
                    label="Download SCORM Word Package",
                    data=scorm_word,
                    file_name="scorm_word_package.zip",
                    mime="application/zip"
                )
            else:
                st.error("Failed to generate SCORM Word package.")

elif selected_section == "PDF Analysis":
    st.header("📄 PDF Analysis")

    # Upload PDF
    pdf_file = st.file_uploader("Upload a PDF", type="pdf")
    if pdf_file:
        # Extract text from the uploaded PDF
        with io.BytesIO(pdf_file.read()) as pdf_stream:
            extracted_text = extract_text_from_pdf(pdf_stream)

        # Display extracted text
        st.write("Extracted Text:")
        st.text_area("PDF Content", extracted_text, height=200)

        # Input field to ask a question
        query = st.text_input("Ask a question based on the PDF:")
        if query:
            # Generate GPT response based on the PDF content
            response = fetch_gpt_response(f"Context: {extracted_text}\nQuestion: {query}")

            # Display the generated response
            st.subheader("Response")
            st.write(response)

            # Display download options
            st.subheader("Download Options")

            # Button to download the PDF content and response as a SCORM package
            scorm_button = st.button("Generate the Response as PDF SCORM Package")
            if scorm_button:
                # Only save the response in the SCORM package
                save_as_scorm_pdf(response)  # Save only the response in PDF
                st.success("SCORM package generated. Check the 'Download SCORM Package' button.")

            if st.button("Generate the Response as SCORM Word Package"):
                # Generate the SCORM package for the Word document with only the response
                scorm_word = save_as_scorm_word(response, file_name="response.docx")

                if scorm_word:
                    # Display success message
                    st.success("SCORM package generated. Click the 'Download SCORM Package' button below.")

                    # Display the download button
                    st.download_button(
                        label="Download SCORM Word Package",
                        data=scorm_word,
                        file_name="scorm_word_package.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("Failed to generate SCORM Word package.")


# Streamlit Section to Handle User Input and SCORM Package Generation
elif selected_section == "CSV Content Generation":
    st.title("CSV Content Generation")

    # Text area for the user to enter the query
    query = st.text_area(
        "Enter your medical or pharmaceutical query:",
        height=200
    )

    # Check if the user has entered a query
    if query:
        # Fetch the response using a function to generate data
        response = fetch_medical_pharma_data(query)

        # Display the generated data in a text area
        st.subheader("Generated Medical & Pharma Data (CSV format)")
        st.text_area(
            "Generated Data",
            value=response,
            height=300
        )

        # Button to generate and download the CSV as a SCORM package
        if st.button("Generate CSV File"):
            # Generate the SCORM package from the response
            scorm_package = create_scorm_package(response)

            # Provide a download button for the SCORM package
            st.download_button(
                label="Download CSV File as SCORM Package",
                data=scorm_package,
                file_name="medical_pharma_scorm.zip",
                mime="application/zip"
            )



# Research Search Section
elif selected_section == "Research Search":
    st.header("🔬 Research Search")
    query = st.text_area("Enter a research query:", height=200)
    if query:
        search_results = google_custom_search(query)
        relevant_content = []
        for item in search_results.get("items", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if any(keyword in title.lower() or keyword in snippet.lower() for keyword in RESEARCH_KEYWORDS):
                relevant_content.append({"title": title, "link": item.get("link", ""), "snippet": snippet})
        if relevant_content:
            st.write("**Research Results:**")
            for content in relevant_content:
                st.write(f"- **[{content['title']}]({content['link']})**")
                st.write(content["snippet"])
        else:
            st.write("No relevant research-related content found.")

# Streamlit Integration for PPT Generation
elif selected_section == "PPT Development":
    st.header("📊 Professional PPT Development")
    topic = st.text_input("Enter the topic for your presentation:")
    if st.button("Generate PPT"):
        if topic:
            st.info("Generating detailed content for your presentation. Please wait...")
            detailed_content = generate_detailed_ppt_content(topic)
            if "Error" not in detailed_content:
                ppt_file_name = create_professional_ppt(detailed_content, topic)
                st.success("Your PowerPoint presentation has been successfully generated!")
                with open(ppt_file_name, "rb") as file:
                    st.download_button(
                        "Download Your PPT",
                        file,
                        file_name=ppt_file_name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    )
            else:
                st.error(detailed_content)
        else:
            st.error("Please enter a valid topic.")


elif selected_section == "Instructions":
    st.header("📝 Instructions")
    st.info("Follow the steps below to effectively use each feature in the application.")

    # General Information
    with st.expander("📋 General Usage Guidelines"):
        st.markdown("""
        - This application is developed for **medical** and **pharmaceutical** domain-related tasks.
        - Ensure that queries are clear and concise for better accuracy.
        - Uploaded files (PDFs, CSVs) must adhere to the specified formats.
        - Always review the generated outputs before downloading.
        """)

    st.subheader("🔍 Feature-specific Instructions")

    # Content Generation Instructions
    with st.expander("1️⃣ **Content Generation**"):
        st.markdown("""
        - Use this module to generate content for **pharmaceutical** and **medical** queries.
        - **Steps**:
          1. Enter your query in the text area provided.
          2. Click the **Submit** button to receive a detailed response.
          3. Download the response in **PDF** or **Word SCORM Package** format.
        """)

    # PDF Analysis Instructions
    with st.expander("2️⃣ **PDF Analysis**"):
        st.markdown("""
        - Analyze and extract content from uploaded PDFs.
        - **Steps**:
          1. Upload a **PDF** file using the file uploader.
          2. The content of the PDF will be extracted and displayed.
          3. Ask a query related to the PDF to get context-based answers.
          4. Download the response in **SCORM-compliant** formats.
        """)

    # CSV Content Generation Instructions
    with st.expander("3️⃣ **CSV Content Generation**"):
        st.markdown("""
        - Generate CSV data related to medical or pharmaceutical queries.
        - **Steps**:
          1. Enter your query in the text area provided.
          2. Click the **Generate CSV File** button to generate data.
          3. Download the generated data as a **CSV SCORM Package**.
        """)

    # Research Search Instructions
    with st.expander("4️⃣ **Research Search**"):
        st.markdown("""
        - Search for research articles, papers, or journals in the medical and pharmaceutical domains.
        - **Steps**:
          1. Enter your research query in the text area.
          2. View a list of relevant results with titles, snippets, and links.
          3. Click on a title to navigate to the full content.
        """)

    # PPT Development Instructions
    with st.expander("5️⃣ **PPT Development**"):
        st.markdown("""
        - Create professional PowerPoint presentations based on medical and pharmaceutical topics.
        - **Steps**:
          1. Enter a valid topic in the input field.
          2. Click the **Generate PPT** button to create a detailed presentation.
          3. Download the PPT file using the download button provided.
        """)

    # Footer Success Message
    st.success("Refer to these instructions for smooth navigation and utilization of features!")

elif selected_section == "Credits":
    st.header("👨‍💻 Credits")

    # Highlight the developer information
    st.subheader("🌟 Developed By")
    st.markdown("""
    **Corbin Technology Solutions**  
    Bringing innovative solutions for the pharmaceutical and medical domains.
    """)

    # Technologies used
    st.subheader("🛠️ Technologies Used")
    st.markdown("""
    - **OpenAI GPT**: For intelligent and context-aware content generation.
    - **Google Custom Search API**: For fetching trusted research content.
    - **Streamlit**: For building a modern and interactive web interface.
    """)

    # Acknowledgment
    st.subheader("🙏 Acknowledgment")
    st.info("""
    Special thanks to the team at **Corbin Technology Solutions** for their dedication and expertise in creating this application.
    """)

    # Footer Message
    st.success("We appreciate your support and feedback to enhance this application!")
