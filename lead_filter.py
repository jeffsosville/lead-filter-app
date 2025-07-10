import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "master_contacts"

st.set_page_config(page_title="🔎 Lead Filter", layout="wide")
st.title("🔎 Lead Filter by Location or Keyword")

# --- CONNECT TO SUPABASE ---
@st.cache_data(ttl=600)
def load_data():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table(TABLE_NAME).select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        return df
    else:
        return pd.DataFrame()

df = load_data()

# --- SAFETY CHECK ---
if df.empty:
    st.warning("⚠️ No data found in Supabase.")
    st.stop()

# --- SEARCH ---
search_term = st.text_input("Enter a location or keyword (e.g., 'Dallas', 'Texas')").strip().lower()

if search_term:
    # Only use columns that actually exist
    possible_cols = ['location', 'state', 'tags', 'message', 'source_url']
    existing_cols = [col for col in possible_cols if col in df.columns]

    if not existing_cols:
        st.error("❌ None of the expected search columns exist in the data.")
        st.write("Available columns in your table:", list(df.columns))
        st.stop()

    # Build OR filter
    filters = [df[col].astype(str).str.lower().str.contains(search_term, na=False) for col in existing_cols]
    combined_filter = filters[0]
    for f in filters[1:]:
        combined_filter |= f

    results = df[combined_filter]
    st.success(f"✅ {len(results)} match(es) found.")
    st.dataframe(results.sort_values(by="date", ascending=False), use_container_width=True)

else:
    st.info("ℹ️ Enter a search term above to begin filtering.")
    st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
