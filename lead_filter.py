import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIG ---
SUPABASE_URL = "https://jrplwchamgzjmjmmkpoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpycGx3Y2hhbWd6am1qbW1rcG9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDYwMTgzOSwiZXhwIjoyMDY2MTc3ODM5fQ.jWQMWrd1TAqmfT9vKqKzNdapdFblxW_t5Yp25E3LyZ0"
TABLE_NAME = "master_contacts"

# --- CONNECT + LOAD ---
@st.cache_data(show_spinner="Loading full dataset...")
def load_data():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    all_rows = []
    batch_size = 1000
    offset = 0

    while True:
        response = supabase.table(TABLE_NAME).select("*").range(offset, offset + batch_size - 1).execute()
        batch = response.data

        if not batch:
            break

        all_rows.extend(batch)
        offset += batch_size

    return pd.DataFrame(all_rows)

# --- UI ---
st.title("🔎 Lead Filter by Location or Keyword")

search_term = st.text_input("Enter a location or keyword (e.g., 'Dallas', 'Texas')").strip().lower()
df = load_data()

if search_term:
    filtered_df = df[
        df['location'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['route_inquired'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['tags'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['state'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['state1'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['state2'].astype(str).str.lower().str.contains(search_term, na=False)
    ]
    st.write(f"### ✅ Found {len(filtered_df)} matching contacts")
    st.dataframe(filtered_df)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered CSV", data=csv, file_name="filtered_leads.csv", mime="text/csv")
else:
    st.write("Enter a keyword to begin filtering the lead database.")
