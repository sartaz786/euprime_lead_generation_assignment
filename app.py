import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Lead Gen AI Dashboard", layout="wide")

st.title("🧬 AI Lead Generation & Ranking Dashboard")
st.markdown("""
**Objective:** Identify and rank high-probability buyers for 3D in-vitro liver toxicity models.
*Prototype Assignment for Euprime Internship*
""")

# --- 1. DUMMY DATA CREATION ---
# Since we cannot scrape live LinkedIn data in this demo safely, we simulate the "Enriched Data"
# This represents the data AFTER the agent has searched the web.
data = [
    {
        "Name": "Dr. Sarah Chen",
        "Title": "Director of Toxicology",
        "Company": "BioSafe Therapeutics",
        "Location": "Cambridge, MA", # Hub
        "HQ_Location": "Cambridge, MA",
        "Funding_Series": "Series B", # High Intent (+20)
        "Tech_Stack": "Uses in-vitro models", # (+15)
        "Published_Paper": True, # (+25)
        "Email": "sarah.c@biosafe.com",
        "LinkedIn": "linkedin.com/in/sarahchen"
    },
    {
        "Name": "Michael Ross",
        "Title": "Head of Safety Assessment",
        "Company": "NovaPharma",
        "Location": "San Francisco, CA", # Hub
        "HQ_Location": "San Francisco, CA",
        "Funding_Series": "Series A", # High Intent (+20)
        "Tech_Stack": "Unknown",
        "Published_Paper": False,
        "Email": "mross@novapharma.com",
        "LinkedIn": "linkedin.com/in/mross"
    },
    {
        "Name": "Jessica Smith",
        "Title": "Junior Scientist",
        "Company": "OldSchool Meds",
        "Location": "Austin, TX", # Not a Hub
        "HQ_Location": "New York, NY",
        "Funding_Series": "Public", # Low Intent
        "Tech_Stack": "None",
        "Published_Paper": False,
        "Email": "jessica@oldschool.com",
        "LinkedIn": "linkedin.com/in/jsmith"
    },
    {
        "Name": "David Kim",
        "Title": "VP Preclinical",
        "Company": "HepatoLogic",
        "Location": "Remote (CO)",
        "HQ_Location": "Boston, MA", # Hub
        "Funding_Series": "Series B",
        "Tech_Stack": "Uses in-vitro models",
        "Published_Paper": True,
        "Email": "d.kim@hepatologic.io",
        "LinkedIn": "linkedin.com/in/dkim"
    },
     {
        "Name": "Emily White",
        "Title": "Lab Technician",
        "Company": "Generic Labs",
        "Location": "Chicago, IL",
        "HQ_Location": "Chicago, IL",
        "Funding_Series": "Seed",
        "Tech_Stack": "None",
        "Published_Paper": False,
        "Email": "emily@genericlabs.com",
        "LinkedIn": "linkedin.com/in/ewhite"
    }
]

df = pd.DataFrame(data)

# --- 2. THE PROBABILITY ENGINE (LOGIC) ---
# This function applies the specific scoring rules requested in the assignment screenshots.

def calculate_propensity_score(row):
    score = 0
    reasons = []

    # RULE 1: Role Fit (+30 points)
    # Looking for: Toxicology, Safety, Hepatic, 3D
    target_roles = ['toxicology', 'safety', 'hepatic', '3d', 'preclinical', 'vp', 'director', 'head']
    if any(keyword in row['Title'].lower() for keyword in target_roles):
        score += 30
        reasons.append("High Fit Role (+30)")
    
    # RULE 2: Company Intent / Funding (+20 points)
    # Looking for: Series A or Series B (Cash to spend)
    if row['Funding_Series'] in ['Series A', 'Series B']:
        score += 20
        reasons.append("Recent Funding Series A/B (+20)")

    # RULE 3: Technographic (+15 points)
    # Looking for: Already uses similar tech
    if "in-vitro" in row['Tech_Stack']:
        score += 15
        reasons.append("Uses Similar Tech (+15)")

    # RULE 4: Location (+10 points)
    # Looking for Hubs: Boston, Cambridge, Bay Area, etc.
    hubs = ['Boston', 'Cambridge', 'San Francisco', 'Bay Area', 'Basel', 'London']
    # Check both Person Location and HQ
    if any(hub in row['Location'] for hub in hubs) or any(hub in row['HQ_Location'] for hub in hubs):
        score += 10
        reasons.append("Located in BioHub (+10)")

    # RULE 5: Scientific Intent (+25 points)
    # Looking for: Published papers on "Drug-Induced Liver Injury"
    if row['Published_Paper']:
        score += 25
        reasons.append("Published Relevant Paper (+25)")

    # Cap score at 100
    score = min(score, 100)
    
    return score, ", ".join(reasons)

# Apply the logic to our data
df[['Propensity_Score', 'Score_Breakdown']] = df.apply(lambda row: pd.Series(calculate_propensity_score(row)), axis=1)

# Sort data so the best leads are at the top
df = df.sort_values(by='Propensity_Score', ascending=False)

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("🎛 Filter Leads")

# Filter by Score
min_score = st.sidebar.slider("Minimum Score", 0, 100, 50)

# Filter by Location
location_search = st.sidebar.text_input("Search Location (e.g., Boston)")

# Apply filters
filtered_df = df[df['Propensity_Score'] >= min_score]
if location_search:
    filtered_df = filtered_df[
        filtered_df['Location'].str.contains(location_search, case=False) | 
        filtered_df['HQ_Location'].str.contains(location_search, case=False)
    ]

# --- 4. MAIN DASHBOARD DISPLAY ---

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Leads", len(df))
col2.metric("Hot Leads (>80 Score)", len(df[df['Propensity_Score'] > 80]))
col3.metric("Top Candidate", df.iloc[0]['Name'], f"{df.iloc[0]['Propensity_Score']} Points")

st.divider()

st.subheader("📋 Prioritized Lead List")
st.write("Leads ranked by the 'Propensity to Buy' logic defined in the assignment.")

# Display Dataframe with visual progress bar for Score
st.dataframe(
    filtered_df,
    column_config={
        "Propensity_Score": st.column_config.ProgressColumn(
            "Score",
            format="%d",
            min_value=0,
            max_value=100,
            help="Calculated based on Role, Funding, Location, and Publications."
        ),
        "LinkedIn": st.column_config.LinkColumn("Profile"),
        "Email": st.column_config.TextColumn("Contact")
    },
    hide_index=True,
    use_container_width=True
)

# --- 5. EXPLANATION SECTION (For the Demo Video) ---
st.divider()
st.subheader("🔍 Scoring Logic Transparency")
selected_lead = st.selectbox("Select a candidate to see why they were ranked this way:", filtered_df['Name'])

if selected_lead:
    lead_details = filtered_df[filtered_df['Name'] == selected_lead].iloc[0]
    st.info(f"**Score Breakdown for {lead_details['Name']}:**")
    st.write(f"**Total Score:** {lead_details['Propensity_Score']}/100")
    st.write(f"**Factors:** {lead_details['Score_Breakdown']}")
    
    if lead_details['Propensity_Score'] >= 80:
        st.success("Recommendation: **High Priority - Contact Immediately**")
    elif lead_details['Propensity_Score'] >= 50:
        st.warning("Recommendation: **Medium Priority - Nurture Campaign**")
    else:
        st.error("Recommendation: **Low Priority - Do Not Contact**")

# Export Button
st.download_button(
    label="📥 Download Ranked List (CSV)",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='ranked_leads.csv',
    mime='text/csv',
)