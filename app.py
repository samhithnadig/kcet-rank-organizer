import streamlit as st
import pdfplumber
import pandas as pd
import re

# Page config
st.set_page_config(page_title="KCET Rank Organizer", layout="wide")

st.title("🎓 KCET Cutoff Rank Organizer")
st.markdown("Upload the official KEA Cutoff PDF to sort colleges by rank.")

# Helper function to clean rank strings
def clean_rank_value(val):
    if val is None or str(val).strip() == "" or "---" in str(val):
        return 999999
    # Remove any non-numeric characters like commas
    num_str = re.sub(r'[^0-9]', '', str(val))
    return int(num_str) if num_str else 999999

# Cache the PDF processing so it doesn't re-run every time you change a filter
@st.cache_data
def process_pdf(file):
    all_rows = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    return all_rows

uploaded_file = st.file_uploader("Upload KCET Cutoff PDF", type="pdf")

if uploaded_file:
    raw_data = process_pdf(uploaded_file)
    
    if raw_data:
        # Create DataFrame
        df = pd.DataFrame(raw_data)
        
        # KEA PDFs usually have headers in the first few rows. 
        # We search for the row containing 'COURSE'
        header_idx = 0
        for i, row in df.iterrows():
            if any("COURSE" in str(cell).upper() for cell in row if cell):
                header_idx = i
                break
        
        # Set headers and clean data
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        
        # Drop rows that are likely empty or just page footers
        df = df.dropna(subset=[df.columns[1]]) 
        
        # Identify Category Columns (short headers like GM, SCG, 2AG etc)
        cat_cols = [str(c).strip() for c in df.columns if c and len(str(c)) <= 5]
        
        st.sidebar.header("Sorting Options")
        selected_cat = st.sidebar.selectbox("Select Category (e.g. GM, 1G, SCG):", cat_cols)

        if selected_cat:
            # Create a numeric column for sorting
            df['sort_key'] = df[selected_cat].apply(clean_rank_value)
            
            # Sort Ascending
            df_sorted = df.sort_values(by='sort_key', ascending=True)
            
            # Remove the helper column before displaying
            display_df = df_sorted.drop(columns=['sort_key'])
            
            st.write(f"### Showing results for Category: **{selected_cat}** (Lowest Rank to Highest)")
            st.dataframe(display_df, use_container_width=True)
            
            # Download button
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Sorted CSV",
                data=csv,
                file_name=f"kcet_sorted_{selected_cat}.csv",
                mime="text/csv",
            )
    else:
        st.error("Could not extract tables from this PDF.")
