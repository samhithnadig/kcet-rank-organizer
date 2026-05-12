import streamlit as st
import pdfplumber
import pandas as pd
import re

# Page Setup
st.set_page_config(page_title="KCET Rank Organizer", layout="wide")

st.title("🎓 KCET Rank Organizer")
st.markdown("### College & Course Rankings in Ascending Order")

# Function to convert rank strings (like '1,234') to numbers
def clean_rank_to_int(val):
    if val is None or str(val).strip() == "" or "---" in str(val):
        return 999999
    num = re.sub(r'[^0-9]', '', str(val))
    return int(num) if num else 999999

@st.cache_data
def load_and_parse_pdf(file):
    all_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            # Use text-based strategy for cleaner KEA table extraction
            table = page.extract_table(table_settings={
                "vertical_strategy": "text", 
                "horizontal_strategy": "text"
            })
            if table:
                all_data.extend(table)
    return all_data

uploaded_file = st.file_uploader("📤 Upload KCET Cutoff PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing PDF and cleaning data..."):
        raw_data = load_and_parse_pdf(uploaded_file)
    
    if raw_data:
        df = pd.DataFrame(raw_data)

        # 1. Detect the Header Row (usually contains 'COURSE' or 'COLLEGE')
        header_idx = 0
        for i, row in df.iterrows():
            row_content = " ".join([str(x).upper() for x in row if x])
            if "COURSE" in row_content or "COLLEGE" in row_content:
                header_idx = i
                break
        
        # Set headers and clean the DataFrame
        df.columns = [str(c).strip() if c else f"Unnamed_{i}" for i, c in enumerate(df.iloc[header_idx])]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)

        # 2. DATA FIX: Convert empty strings to NaN and Forward Fill
        # KEA PDFs usually list the College Name once for a block of courses.
        # This copies the college name down to every course row.
        df = df.replace(r'^\s*$', pd.NA, regex=True)

        # 3. Identify Important Columns with robust matching
        college_col = next((c for c in df.columns if any(k in str(c).upper() for k in ["COLLEGE", "INSTITUTE", "NAME"])), None)
        course_col = next((c for c in df.columns if any(k in str(c).upper() for k in ["COURSE", "BRANCH"])), None)
        
        if college_col:
            df[college_col] = df[college_col].ffill()

        # Categories are the short column names (GM, SCG, STG, etc.)
        cat_cols = [str(c).strip() for c in df.columns if c and len(str(c)) <= 5 and str(c).upper() not in ["CODE", "SL NO", "S.NO"]]

        # 4. User Selection Sidebar
        st.sidebar.header("Filter Options")
        selected_cat = st.sidebar.selectbox("Choose Category to Sort By:", ["-- Select Category --"] + cat_cols)

        if selected_cat != "-- Select Category --":
            # Select ONLY College Name, Course Name, and the chosen rank
            cols_to_show = []
            if college_col: cols_to_show.append(college_col)
            if course_col: cols_to_show.append(course_col)
            cols_to_show.append(selected_cat)

            # Ensure we only try to show columns that actually exist
            valid_cols = [c for c in cols_to_show if c in df.columns]
            final_view = df[valid_cols].copy()

            # 5. Clean up Rank data and Sort
            final_view['sort_rank'] = final_view[selected_cat].apply(clean_rank_to_int)
            
            # Filter out entries with no ranks (---) and sort ascending
            final_view = final_view[final_view['sort_rank'] < 999999]
            final_view = final_view.sort_values(by='sort_rank', ascending=True)

            # Drop the hidden numeric rank column before showing the user
            display_df = final_view.drop(columns=['sort_rank'])

            st.write(f"### Showing results for **{selected_cat}**")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Download CSV option
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Sorted List",
                data=csv_data,
                file_name=f"KCET_{selected_cat}_Sorted.csv",
                mime="text/csv"
            )
    else:
        st.error("Could not find any tables in the uploaded PDF.")
