import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import json
import pandas as pd
from datetime import datetime
from database_handler import DATABASE_FILE, load_database, save_database, add_programs_to_database

# page setup
st.set_page_config(page_title="University Scraper", page_icon="🎓")
st.title("University Summer Programs Database")
st.markdown("Extracts & build database of CS/Programming summer programs")

# Load and display database stats
database = load_database()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Programs", database.get('total_programs', 0))
with col2:
    st.metric("Universities Scraped", len(database.get('universities', [])))
with col3:
    last_updated = database.get('last_updated')
    if last_updated:
        update_date = datetime.fromisoformat(last_updated).strftime("%Y-%m-%d")
        st.metric("Last Updated", update_date)
    else:
        st.metric("Last Updated", "Never")

# API key input
api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")

# URL input
url = st.text_input("Enter University Website URL",
                    placeholder="https://university.edu/summer-programs",
                    help="Paste the URL of the university summer programs page")


# scraper
def simple_scrape(url):
    """Scraping with beautiful soup"""
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36 '
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # bs4 setup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text content
        text_content = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)

        return clean_text[:15000]  # Limit to 15k characters

    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None


def extract_programs_with_openai(content, url):
    """Using OpenAI to extract program information"""
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
        return None

    prompt = f"""
Extract computer science and programming summer programs from this university website content.

Website URL: {url}
Content: {content}

Extract ONLY programs related to:
- Computer Science
- Programming/Coding
- Software Engineering  
- Data Science
- AI/Machine Learning
- Web Development
- Game Development

For each program found, return a JSON object with these exact fields (Compulsory to do):
- "university": Name of University/Summer School/College
- "name": Program title
- "description": What students learn (max 150 words)
- "eligibility": Who can apply (age, education level, requirements)
- "duration": Program length and dates
- "pricing": Free (if not clearly stated, else state cost of enrolling on this summer school/bootcamp program"),
- "link": Program URL (use the base URL if specific link not found)

Return ONLY a valid JSON array. If no programs found, return [].

Example format:
[
  {{
    "university": "University of Energy and Natural Resources - Sunyani, Ghana",
    "name": "Python Summer Bootcamp",
    "description": "6-week intensive program teaching Python programming, web development with Django, and data analysis",
    "eligibility": "High school students ages 16-18",
    "duration": "6 weeks, June-July 2024",
    "pricing
    "link": "{url}"
  }}
]
"""

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()

        if result.startswith('```json'):
            result = result[7:-3]
        elif result.startswith('```'):
            result = result[3:-3]

        # Try to parse JSON
        try:
            programs = json.loads(result)
            return programs if isinstance(programs, list) else []
        except json.JSONDecodeError:
            st.error("Failed to parse AI response as JSON")
            st.code(result)
            return []

    except Exception as e:
        st.error(f"OpenAI API Error: {str(e)}")
        return None


# main app logic
if st.button("Scrape and Extract Programs", disabled=not url or not api_key):
    if url and api_key:
        with st.spinner("Scraping website..."):
            content = simple_scrape(url)

        if content:
            st.success("Website scraped successfully!")

            with st.expander("View Scraped Content (Preview)"):
                st.text_area("Content Preview", content[:1000] + "...", height=200)

            with st.spinner("Extracting programs with AI..."):
                programs = extract_programs_with_openai(content, url)

            if programs:
                st.success(f"Found {len(programs)} programs!")

                # auto-save to database
                with st.spinner("Saving to database..."):
                    updated_database = add_programs_to_database(programs, url)
                    if save_database(updated_database):
                        st.success(f"Added {len(programs)} programs to database!")
                        st.info(
                            f"Database now contains {updated_database['total_programs']} total programs from {len(updated_database['universities'])} universities")
                        st.info(f"Saved to: `{DATABASE_FILE}`")
                    else:
                        st.error("Failed to save to database")

                # Display programs
                st.subheader("Newly Extracted Programs")

                for i, program in enumerate(programs, 1):
                    with st.expander(f"Program {i}: {program.get('name', 'Unknown')}"):
                        st.write(f"**Name:** {program.get('name', 'Not specified')}")
                        st.write(f"**Description:** {program.get('description', 'Not specified')}")
                        st.write(f"**Eligibility:** {program.get('eligibility', 'Not specified')}")
                        st.write(f"**Duration:** {program.get('duration', 'Not specified')}")
                        st.write(f"**Link:** {program.get('link', url)}")

                # Download options for current scrape
                st.subheader("Download Current Results")
                col1, col2 = st.columns(2)

                with col1:
                    # JSON download
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_data = {
                        "scraped_from": url,
                        "scraped_at": datetime.now().isoformat(),
                        "total_programs": len(programs),
                        "programs": programs
                    }

                    st.download_button(
                        label="Download JSON (Current)",
                        data=json.dumps(json_data, indent=2),
                        file_name=f"summer_programs_{timestamp}.json",
                        mime="application/json"
                    )

                with col2:
                    # CSV download
                    if programs:
                        df = pd.DataFrame(programs)
                        csv_data = df.to_csv(index=False)

                        st.download_button(
                            label="-->Download CSV (Current)",
                            data=csv_data,
                            file_name=f"summer_programs_{timestamp}.csv",
                            mime="text/csv"
                        )

            elif programs == []:
                st.warning("No computer science/programming programs found on this page. Try a more specific URL.")
            else:
                st.error("Failed to extract programs. Check your API key and try again.")
    else:
        st.warning("Please enter both a URL and OpenAI API key")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### Tips")
st.sidebar.markdown("""
- Look for pages like `/summer-programs` or `/computer-science/camps (common among sites I gathered with Gemini Pro)`
- Try specific department pages rather than general university homepages
- This scraper focuses on CS/programming programs only
- Results are automatically filtered for relevance
""")

# Show current directory info in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### File Location")
current_dir = os.getcwd()
st.sidebar.markdown(f"**Working Directory:** `{current_dir}`")
st.sidebar.markdown(f"**Database File:** `{DATABASE_FILE}`")

if os.path.exists(DATABASE_FILE):
    file_size = os.path.getsize(DATABASE_FILE)
    file_size_kb = file_size / 1024
    st.sidebar.markdown(f"**File Size:** {file_size_kb:.1f} KB")
else:
    st.sidebar.markdown("**Status:** Database file doesn't exist yet")

# Example URLs
st.sidebar.markdown("### Example URLs")
st.sidebar.markdown("""
-Oxford University Programs
- MIT Summer Programs
- Stanford Pre-College
- Carnegie Mellon Summer Programs
- UC Berkeley Summer Sessions
""")

# dm section
st.markdown("---")
st.subheader("Database Management")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View All Programs"):
        database = load_database()
        if database['programs']:
            st.subheader(f"All Programs in Database ({len(database['programs'])})")

            # Add search/filter
            search_term = st.text_input("Search programs:", placeholder="Enter keyword to filter programs")

            programs_to_show = database['programs']
            if search_term:
                programs_to_show = [p for p in database['programs']
                                    if search_term.lower() in p.get('name', '').lower()
                                    or search_term.lower() in p.get('description', '').lower()
                                    or search_term.lower() in p.get('university', '').lower()
                                    or search_term.lower() in p.get("pricing", " ").lower()]
                st.info(f"Found {len(programs_to_show)} programs matching '{search_term}'")

            for i, program in enumerate(programs_to_show, 1):
                with st.expander(f"{program.get('university', 'Unknown')} - {program.get('name', 'Unknown')}"):
                    st.write(f"**University:** {program.get('university', 'Not specified')}")
                    st.write(f"**Name:** {program.get('name', 'Not specified')}")
                    st.write(f"**Description:** {program.get('description', 'Not specified')}")
                    st.write(f"**Eligibility:** {program.get('eligibility', 'Not specified')}")
                    st.write(f"**Duration:** {program.get('duration', 'Not specified')}")
                    st.write(f"**Pricing** {program.get('pricing', 'Not specified')}")
                    st.write(f"**Link:** {program.get('link', 'Not specified')}")
                    st.write(
                        f"**Added:** {datetime.fromisoformat(program.get('added_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No programs in database yet. Start scraping some universities!")

with col2:
    if st.button("View Universities"):
        database = load_database()
        if database.get('universities'):
            st.subheader("Scraped Universities")
            for uni in database['universities']:
                with st.expander(f"{uni.get('name', 'Unknown')} ({uni.get('programs_count', 0)} programs)"):
                    st.write(f"**URL:** {uni.get('url', 'Unknown')}")
                    st.write(f"**Programs Count:** {uni.get('programs_count', 0)}")
                    st.write(
                        f"**Last Scraped:** {datetime.fromisoformat(uni.get('scraped_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No universities scraped yet!")

with col3:
    if st.button("Export Database"):
        database = load_database()
        if database['programs']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Full database JSON
            st.download_button(
                label="Full Database (JSON)",
                data=json.dumps(database, indent=2, ensure_ascii=False),
                file_name=f"full_database_{timestamp}.json",
                mime="application/json"
            )

            # programs only CSV
            df = pd.DataFrame(database['programs'])
            csv_data = df.to_csv(index=False)

            st.download_button(
                label="All Programs (CSV)",
                data=csv_data,
                file_name=f"all_programs_{timestamp}.csv",
                mime="text/csv"
            )
        else:
            st.info("Database is empty!")

# clear database option (with warning)
st.markdown("---")
with st.expander("⚠ Attempt to terminate database"):
    st.warning("**Careful!** These actions cannot be undone.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Database", type="secondary"):
            if st.checkbox("I understand this will delete all data"):
                empty_db = {"programs": [],
                            "universities": [],
                            "last_updated": None,
                            "total_programs": 0}
                if save_database(empty_db):
                    st.success("Database cleared!")
                    st.rerun()

    with col2:
        if st.button("Reset & Start Fresh", type="secondary"):
            if st.checkbox("I want to start completely fresh"):
                if os.path.exists(DATABASE_FILE):
                    os.remove(DATABASE_FILE)
                    st.success(f"Database file deleted from: {DATABASE_FILE}")
                    st.info("Refresh the page to start fresh.")
                    st.rerun()
                else:
                    st.info("No database file to delete.")

# footer
st.markdown("---")
st.markdown(
    "*This is a University Summer Programs Scraper \nExtract your CS related programs easily for more insights*")
