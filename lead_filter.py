import streamlit as st
import pandas as pd
from supabase import create_client, Client
from streamlit_authenticator import Authenticate
import copy

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
TABLE_NAME = "master_contacts"

# --- AUTH ---
users = copy.deepcopy(st.secrets["credentials"])
authenticator = Authenticate(
    users,
    "cookie_name",
    "signature_key",
    cookie_expiry_days=1
)
name, auth_status, username = authenticator.login("Login", "main")

# --- MAIN APP ---
if auth_status:
    st.sidebar.success(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")

    @st.cache_data(show_spinner="Loading...")
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

    st.title("🔎 Lead Filter")
    search = st.text_input("Search location or keyword").strip().lower()
    df = load_data()

    if search:
        filtered = df[
            df['location'].astype(str).str.lower().str.contains(search, na=False) |
            df['route_inquired'].astype(str).str.lower().str.contains(search, na=False) |
            df['tags'].astype(str).str.lower().str.contains(search, na=False) |
            df['state'].astype(str).str.lower().str.contains(search, na=False) |
            df['state1'].astype(str).str.lower().str.contains(search, na=False) |
            df['state2'].astype(str).str.lower().str.contains(search, na=False)
        ]
        st.write(f"### ✅ {len(filtered)} matching contacts")
        st.dataframe(filtered)
        st.download_button("📥 Download CSV", data=filtered.to_csv(index=False), file_name="filtered_leads.csv", mime="text/csv")
    else:
        st.info("Enter a keyword to filter the database.")

elif auth_status is False:
    st.error("Login failed. Check your username or password.")
elif auth_status is None:
    st.warning("Please enter your credentials.")
