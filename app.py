import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="KCET Rank Finder", layout="wide")

# App Header
st.title("KCET Rank Organizer")
st.markdown("### Upload KEA Cutoff PDF to see College & Course rankings")

def clean_rank(val):
    if val is None or str(val).strip() == "" or "---" in str(val):
        return 999999
    num = re.sub(r'[^0-9]', '', str(val))
    return int(num) if num else 999999

@st.cache_data
def process_pdf(file):
    all_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_data.extend(table)
    return all_data

uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

if uploaded_file:
    with st.spinner("Processing PDF..."):
        data = process_pdf(uploaded_file)
    
    if data:
        df = pd.DataFrame(data)
        
        # Finding the Header Row
        header_idx = 0
        for i, row in df.iterrows():
            row_str = " ".join([str(x).upper() for x in row if x])
            if "COURSE" in row_str or "COLLEGE" in row_str:
                header_idx = i
                break
        
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)

        # Identify Column Names automatically
        college_col = next((c for c in df.columns if any(k in str(c).upper() for k in ["COLLEGE", "INSTITUTE"])), None)
        course_col = next((c for c in df.columns if any(k in str(c).upper() for k in ["COURSE", "BRANCH"])), None)
        
        # Categories are usually the columns with short names (GM, SCG, etc.)
        cat_cols = [str(c).strip() for c in df.columns if c and len(str(c)) <= 5 and str(c).upper() not in ["CODE", "SL NO"]]

        st.sidebar.header("Filter Settings")
        selected_cat = st.sidebar.selectbox("Select Category", ["Choose Category"] + cat_cols)

        if selected_cat != "Choose Category":
            # Select only needed columns
            display_cols = []
            if college_col: display_cols.append(college_col)
            if course_col: display_cols.append(course_col)
            display_cols.append(selected_cat)

            # Create the filtered DataFrame
            final_df = df[display_cols].copy()
            
            # Clean and Sort by Rank
            final_df['sort_val'] = final_df[selected_cat].apply(clean_rank)
            final_df = final_df[final_df['sort_val'] < 999999] # Remove empty ranks
            final_df = final_df.sort_values(by='sort_val', ascending=True)
            
            # Drop the hidden sort column
            final_df = final_df.drop(columns=['sort_val'])

            st.subheader(f"📊 Ranking for {selected_cat} (Ascending)")
            st.dataframe(final_df, use_container_width=True, hide_index=True)
            
            # Download link
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download This List", csv, f"KCET_{selected_cat}_Sorted.csv", "text/csv")
    else:
        st.error("Could not read any tables from this PDF.")
