import streamlit as st
import pandas as pd
import base64
import os

# Function to encode image as base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Path to your background image
background_image_path = 'D:/lic/bag.jpg'
background_image = get_base64_of_bin_file(background_image_path)

# Inject CSS for background image, white text, and button styling
st.markdown(
    f"""
    <style>
    body {{
        background-image: url("data:image/jpeg;base64,{background_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #FFFFFF;
    }}
    .stApp {{
        background-color: rgba(0, 0, 0, 0.6); /* Dark overlay for readability */
    }}
    h1, h2, h3, h4, h5, h6, p, label {{
        color: #FFFFFF;
    }}
    .section-header {{
        color: #FF4B4B;
        font-size: 32px;
        font-weight: bold;
        margin-top: 10px;
    }}
    .stButton > button {{
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar navigation
page = st.sidebar.selectbox("Select a page", ["Home", "Select Symptoms", "Confused Drug", "If You Want to Buy"])

# Function to load dataset
@st.cache_data
def load_data():
    try:
        data = pd.read_excel("D:/lic/medlist.xlsx")
        return data
    except FileNotFoundError:
        st.error("Dataset not found. Please check the file path and try again.")
        return None

# Load symptoms data for matching synonyms
@st.cache_data
def load_symptoms_data():
    try:
        symptoms_data = pd.read_csv("D:/lic/symtoms_df.csv")
        return symptoms_data
    except FileNotFoundError:
        st.error("Symptoms dataset not found. Please check the file path and try again.")
        return None

# Function to get probable disease from synonyms
def get_disease_from_synonyms(synonyms, symptoms_df):
    synonym_terms = [syn.strip() for syn in synonyms.split(",")]
    disease_counts = {}

    # Check each synonym term in symptom columns
    for term in synonym_terms:
        for col in ['Symptom_1', 'Symptom_2', 'Symptom_3']:
            matched_diseases = symptoms_df[symptoms_df[col].str.contains(term, case=False, na=False)]['Disease']
            for disease in matched_diseases:
                if disease in disease_counts:
                    disease_counts[disease] += 1
                else:
                    disease_counts[disease] = 1

    # Find disease with highest count
    if disease_counts:
        probable_disease = max(disease_counts, key=disease_counts.get)
        return probable_disease
    return None

# Home Page
if page == "Home":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                <img src="lic/images/medicine-image.jpg" style="width: 100%; max-width: 200px; border-radius: 10px;" />
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.title("AI-Driven Boolean Query Generator for Healthcare")
        st.write("""
            Craft precise search queries for medical literature, patient records, and clinical trials with this tool 
            designed to assist healthcare professionals.
        """)

    st.markdown('<p class="section-header">Why Use Boolean Queries?</p>', unsafe_allow_html=True)
    st.write("""
        Boolean queries enhance search accuracy, save time, and ensure you receive relevant information. 
        This tool lets you build complex queries for healthcare research quickly and effectively.
    """)

    with st.expander("How to Use the Boolean Query Generator"):
        st.write("""
            - **Keywords**: Enter main topics (e.g., 'diabetes').
            - **Synonyms**: Add related terms to widen your search.
            - **Filters**: Narrow down your search scope to relevant areas.
        """)
        st.markdown("### Example Query:")
        st.code("('diabetes' OR 'hyperglycemia') AND 'patient records'")

    st.subheader("Build Your Query")
    keywords = st.text_area("Keywords (e.g., 'diabetes', 'hypertension')")
    synonyms = st.text_area("Synonyms/Related Terms (e.g., 'hyperglycemia' for 'diabetes')")
    operator = st.selectbox("Boolean Operator", ["AND", "OR", "NOT"])

    st.header("Context Filters")
    filter_1 = st.checkbox("Research Articles")
    filter_2 = st.checkbox("Patient Records")
    filter_3 = st.checkbox("Clinical Trials")

    if st.button("Generate Boolean Query"):
        boolean_query = ""
        
        if keywords:
            keyword_terms = keywords.split(",")
            keyword_query = f" {operator} ".join([term.strip() for term in keyword_terms])
            boolean_query += f"({keyword_query})"
        
        if synonyms:
            synonym_terms = synonyms.split(",")
            synonym_query = f" {operator} ".join([term.strip() for term in synonym_terms])
            boolean_query += f" AND ({synonym_query})" if boolean_query else f"({synonym_query})"

        if filter_1:
            boolean_query += " AND Research Articles"
        if filter_2:
            boolean_query += " AND Patient Records"
        if filter_3:
            boolean_query += " AND Clinical Trials"
        
        st.subheader("Generated Boolean Query")
        st.code(boolean_query)

    # Check symptoms from synonyms
    symptoms_df = load_symptoms_data()
    if synonyms and symptoms_df is not None:
        probable_disease = get_disease_from_synonyms(synonyms, symptoms_df)
        if probable_disease:
            st.write("Symptoms may be like:", probable_disease)
        else:
            st.write("No matching disease found.")

    st.write("Need help? Email us at support@example.com or visit our FAQ page.")

# Select Symptoms Page
elif page == "Select Symptoms":
    st.title("Select Symptoms")
    st.write("This section allows you to search for medications based on their use.")

    data = load_data()

    if data is not None:
        search_term = st.text_input("Enter a condition or use case (e.g., 'pain relief'):")
        
        if st.button("Search", key="search_button"):
            results = data[data['uses'].str.contains(search_term, case=False, na=False)]
            if not results.empty:
                unique_tablets = results[['Tablet', 'uses']].drop_duplicates()
                st.write("Matching Tablets for the given use:")
                for _, row in unique_tablets.iterrows():
                    st.markdown(
                        f"<p style='font-size:40px; font-weight:bold; color:#FF4B4B;'>{row['Tablet']}</p>"
                        f"<p style='font-size:20px; color:grey;'>{row['uses']}</p>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("No matching results found.")

# Confused Drug Page
elif page == "Confused Drug":
    st.title("Confused Drug")
    st.write("This section will help clarify commonly confused drugs in healthcare.")

    data = load_data()
    if data is not None:
        confused_drug = st.text_input("Enter a drug name to check for similar medications:")

        if st.button("Check", key="confused_drug_button"):
            match = data[data['othernames'].str.contains(confused_drug, case=False, na=False)]
            if not match.empty:
                for _, row in match.iterrows():
                    st.write(f"Hey, it's just like {row['Tablet']} ({row['othernames']})")
            else:
                st.write("No similar medications found.")

# If You Want to Buy Page
elif page == "If You Want to Buy":
    st.title("If You Want to Buy")
    st.write("Click the button below to run the purchasing application.")

    if st.button("Run Purchase App"):
        os.system("streamlit run D:/lic/app.py")
