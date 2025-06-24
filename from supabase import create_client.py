from supabase import create_client

SUPABASE_URL = "https://jrplwchamgzjmjmmkpoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpycGx3Y2hhbWd6am1qbW1rcG9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDYwMTgzOSwiZXhwIjoyMDY2MTc3ODM5fQ.jWQMWrd1TAqmfT9vKqKzNdapdFblxW_t5Yp25E3LyZ0"

print("URL OK:", SUPABASE_URL.startswith("https://") and SUPABASE_URL.endswith(".co"))
print("Key length:", len(SUPABASE_KEY))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected!    (if this prints, key is fine)")
