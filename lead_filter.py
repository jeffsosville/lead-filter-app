import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://jrplwchamgzjmjmmkpoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpycGx3Y2hhbWd6am1qbW1rcG9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDYwMTgzOSwiZXhwIjoyMDY2MTc3ODM5fQ.jWQMWrd1TAqmfT9vKqKzNdapdFblxW_t5Yp25E3LyZ0"  # Use anon key for frontend
TABLE_NAME = "master_contacts"

@st.cache_data(ttl=60)  # Re-fetch every 60 seconds
@st.cache_data(show_spinner="Loading full dataset...")
def load_data():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    all_rows = []
    batch_size = 1000
    offset = 0

    while True:
        response = supabase.table(TABLE_NAME)\
            .select("*")\
            .range(offset, offset + batch_size - 1)\
            .execute()

        if not response.data:
            break

        all_rows.extend(response.data)
        offset += batch_size

    return pd.DataFrame(all_rows)


st.title("🔎 ATM Lead Search")
search_term = st.text_input("Search by keyword, location, or route").strip().lower()
df = load_data()

if search_term:
    df_filtered = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)]
    st.write(f"✅ Found {len(df_filtered)} results")
    st.dataframe(df_filtered)
    st.download_button("📥 Download", df_filtered.to_csv(index=False), "filtered_leads.csv")
else:
    st.write("Enter a keyword to search.")
