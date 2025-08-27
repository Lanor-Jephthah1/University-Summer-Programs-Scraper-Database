import streamlit as st
from datetime import datetime
import json
import os

# database path
DATABASE_FILE = os.path.join(os.getcwd(), "university_programs_database.json")


def load_database():
    """Load existing database or create empty one"""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.sidebar.success(f"Database loaded from: {DATABASE_FILE}")
                return data
        except Exception as e:
            st.sidebar.error(f"Error loading database: {str(e)}")
            return {"programs": [],
                    "universities": [],
                    "last_updated": None,
                    "total_programs": 0}
    else:
        st.sidebar.info(f"New database will be created at: {DATABASE_FILE}")
        return {"programs": [],
                "universities": [],
                "last_updated": None,
                "total_programs": 0}


def save_database(database):
    """Save database to file in current directory"""
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        st.success(f" Database saved to: {DATABASE_FILE}")
        return True
    except Exception as e:
        st.error(f"Failed to save database to {DATABASE_FILE}: {str(e)}")
        return False


def add_programs_to_database(programs, university_url):
    """Add new programs to the database"""
    database = load_database()

    # Extract university name from URL
    university_name = university_url.replace('https://', '').replace('http://', '').split('/')[0]

    # Check if university already exists
    existing_urls = [uni.get('url', '') for uni in database.get('universities', [])]

    if university_url not in existing_urls:
        # Add university info
        university_info = {
            "name": university_name,
            "url": university_url,
            "scraped_at": datetime.now().isoformat(),
            "programs_count": len(programs)
        }
        database['universities'].append(university_info)
    else:
        # Update existing university
        for uni in database['universities']:
            if uni.get('url') == university_url:
                uni['scraped_at'] = datetime.now().isoformat()
                uni['programs_count'] = uni.get('programs_count', 0) + len(programs)

    # add programs with university info
    for program in programs:
        program_with_meta = program.copy()
        program_with_meta['university'] = university_name
        program_with_meta['source_url'] = university_url
        program_with_meta['added_at'] = datetime.now().isoformat()
        program_with_meta['id'] = f"{university_name}_{program.get('name', 'unknown')}_{len(database['programs'])}"

        database['programs'].append(program_with_meta)

    # update metadata
    database['last_updated'] = datetime.now().isoformat()
    database['total_programs'] = len(database['programs'])

    return database
