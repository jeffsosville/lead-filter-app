import streamlit as st
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://jrplwchamgzjmjmmkpoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpycGx3Y2hhbWd6am1qbW1rcG9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA2MDE4MzksImV4cCI6MjA2NjE3NzgzOX0.2cDqlLvZmcCNsd4-o01fXQd3f5wNZWy6lhDKLx82mtg"  # Use anon key for frontend
TABLE_NAME = "master_contacts"

@st.cache_data(ttl=60)  # Re-fetch every 60 seconds
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table(TABLE_NAME).select("*").limit(10000).execute()
    return pd.DataFrame(response.data)

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
