# University Summer Programs Scraper & Database

A web application that automatically scrapes university websites to find and extract information about computer science and programming summer programs, then stores them in a searchable database.

## Features

- **Web Scraping**: Automatically extracts content from university summer program pages
- **AI-Powered Extraction**: Uses OpenAI's GPT to intelligently identify and extract program information
- **Database Management**: Stores all programs in a JSON database with search and filtering capabilities
- **Export Functionality**: Download results as JSON or CSV files
- **User-Friendly Interface**: Streamlit-based web interface that's easy to use

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Web Scraping**: BeautifulSoup4, Requests
- **AI Processing**: OpenAI API (GPT-3.5-turbo)
- **Data Management**: JSON, Pandas
- **HTTP Requests**: Requests library

## Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)

### Step 1: Clone or Download the Files

Ensure you have these files in your working directory:
- `main.py` - Main application
- `database_handler.py` - Database management functions
- `requirements.txt` - Python dependencies
- `university_programs_database.json` - Sample database (will be created automatically if missing)

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up OpenAI API Key

You'll need an OpenAI API key to use the AI extraction functionality. You can get one from: https://platform.openai.com/api-keys

### Step 4: Run the Application

```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

### 1. Scraping University Programs

1. **Enter OpenAI API Key**: Input your API key in the sidebar
2. **Enter University URL**: Paste the URL of a university's summer programs page
3. **Click "Scrape and Extract Programs"**: The app will:
   - Scrape the website content
   - Use AI to extract program information
   - Save results to the database
   - Display extracted programs

### 2. Database Management

- **View All Programs**: Browse all programs in the database with search functionality
- **View Universities**: See which universities have been scraped and how many programs each has
- **Export Database**: Download the entire database as JSON or CSV
- **Database Stats**: View total programs, universities scraped, and last update time

### 3. Export Options

- **Current Results**: Download only the programs from your most recent scrape
- **Full Database**: Download all programs from all universities
- **Formats Available**: JSON (structured data) and CSV (spreadsheet-friendly)

## File Structure

```
├── main.py                 # Main Streamlit application
├── database_handler.py     # Database loading/saving functions
├── requirements.txt        # Python dependencies
├── university_programs_database.json  # Auto-generated database file
```

## Database Schema

The database uses a JSON structure with the following format:

```json
{
  "programs": [
    {
      "university": "University Name",
      "name": "Program Name",
      "description": "Program description",
      "eligibility": "Who can apply",
      "duration": "Program length",
      "pricing": "Cost information",
      "link": "Program URL",
      "source_url": "Where it was scraped from",
      "added_at": "Timestamp",
      "id": "Unique identifier"
    }
  ],
  "universities": [
    {
      "name": "University Name",
      "url": "University URL",
      "scraped_at": "Timestamp",
      "programs_count": 5
    }
  ],
  "last_updated": "Timestamp",
  "total_programs": 43
}
```

## Example URLs to Try

- https://www.bu.edu/summer/courses/computer-science/
- https://www.cmu.edu/pre-college/academic-programs/ai_scholars.html
- https://summer.georgetown.edu/programs/SHS31/artificial-intelligence-academy/
- https://summer.harvard.edu/high-school-programs/secondary-school-program/

## Tips for Best Results

1. **Use Specific URLs**: Instead of university homepages, use URLs that directly link to summer programs or computer science departments
2. **Check Program Pages**: Look for pages with "/summer-programs", "/computer-science", or "/camp" in the URL
3. **English Content**: The AI works best with English-language content
4. **Program Diversity**: The tool focuses on CS/programming-related programs but may find related STEM programs

## Customization

### Modifying Search Criteria

Edit the prompt in `extract_programs_with_openai()` function in `main.py` to change what types of programs are extracted.

### Adjusting Scraping Parameters

Modify the `simple_scrape()` function to change headers, timeouts, or content cleaning rules.

### Changing Database Location

Update the `DATABASE_FILE` path in `database_handler.py` to store the database in a different location.

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your OpenAI API key is valid and has credits
2. **Scraping Blocked**: Some websites may block automated scraping. Try different URLs or add delays
3. **JSON Parsing Errors**: If the AI returns malformed JSON, the app will show the raw response for debugging

### Getting Help

Check the console output for detailed error messages. Most issues will be displayed in the Streamlit interface.

## Privacy Note

This tool only scrapes publicly available information from university websites. Always respect robots.txt files and website terms of service.

## License

This project is intended for educational and research purposes. Please ensure you comply with the terms of service of any websites you scrape and the OpenAI API usage policies.

## Future Enhancements

- Add rate limiting to avoid overwhelming websites
- Implement caching to avoid re-scraping the same URLs
- Add more advanced filtering and search options
- Include program comparison features
- Add email notifications for new programs
- Implement user accounts to save preferences
