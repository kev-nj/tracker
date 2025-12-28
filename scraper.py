"""
UK Finance Tracker Scraper
Scrapes graduate role data from the-trackr.com and saves directly to Supabase
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role key for admin operations
supabase_url = os.getenv('SUPABASE_URL')
supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_service_key)


def scrape_tracker():
    """Scrape the UK Finance graduate programmes tracker"""
    
    url = "https://app.the-trackr.com/uk-finance/graduate-programmes"
    
    print(f"Fetching data from {url}...")
    print("Opening browser...")
    
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(5)  # Wait for JavaScript to load
        
        # Get page source after JavaScript has loaded
        page_source = driver.page_source
        
        print("Parsing HTML...")
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all table rows
        rows = soup.find_all('tr')
        
        data = []
        current_category = "Uncategorized"
        
        print(f"Found {len(rows)} rows. Extracting data...")
        
        for row in rows:
            cells = row.find_all('td')
            
            # Skip header rows and empty rows
            if len(cells) < 5:
                # Check if this is a category header
                text = row.get_text(strip=True)
                if text and len(cells) <= 2:
                    # Potential category marker
                    if any(keyword in text for keyword in ['Bulge Bracket', 'Elite Boutique', 'Middle Market', 
                                                            'Buy-Side', 'Asset Management', 'Big 4', 'Consulting',
                                                            'Trading', 'Quant', 'Pensions', 'Insurance', 'Accounting',
                                                            'Audit', 'Miscellaneous', 'Sponsors']):
                        current_category = text
                continue
            
            try:
                # Extract data from cells
                status = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                company = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                role = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                app_opens = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                app_closes = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                last_year = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                stages = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                platform = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                online_app = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                cv = cells[9].get_text(strip=True) if len(cells) > 9 else ""
                cover_letter = cells[10].get_text(strip=True) if len(cells) > 10 else ""
                test = cells[11].get_text(strip=True) if len(cells) > 11 else ""
                notes = cells[12].get_text(strip=True) if len(cells) > 12 else ""
                
                # Extract hyperlinks and convert to absolute URLs
                company_link = ""
                role_link = ""
                base_url = url  # Use the tracker page URL as base
                
                if len(cells) > 1:
                    company_a = cells[1].find('a')
                    if company_a and company_a.get('href'):
                        href = company_a.get('href')
                        # Convert relative URL to absolute URL
                        company_link = urljoin(base_url, href) if href else ""
                
                if len(cells) > 2:
                    role_a = cells[2].find('a')
                    if role_a and role_a.get('href'):
                        href = role_a.get('href')
                        # Convert relative URL to absolute URL
                        role_link = urljoin(base_url, href) if href else ""
                
                # Skip rows without company name
                if not company or company in ["Sponsors", "Trackr Exclusive"]:
                    continue
                
                data.append({
                    'Category': current_category,
                    'Status': status,
                    'Company': company,
                    'Company_Link': company_link,
                    'Role': role,
                    'Role_Link': role_link,
                    'Application Opens': app_opens,
                    'Application Closes': app_closes,
                    'Last Year Opened': last_year,
                    'Interview Stages': stages,
                    'Assessment Platform': platform,
                    'Online Application': online_app,
                    'CV Required': cv,
                    'Cover Letter': cover_letter,
                    'Test Required': test,
                    'Notes': notes
                })
                
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        return data
        
    finally:
        driver.quit()
        print("Browser closed.")


def parse_date_for_db(date_str):
    """Parse date string in format 'DD Mon YY' to ISO format for database"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        dt = datetime.strptime(date_str.strip(), '%d %b %y')
        return dt.date().isoformat()
    except:
        return None


def save_to_supabase(data):
    """Save scraped data directly to Supabase"""
    
    if not data:
        print("No data to save!")
        return
    
    try:
        # Convert data to database format
        roles = []
        for row in data:
            role_data = {
                'category': row.get('Category', ''),
                'company_name': row.get('Company', ''),
                'company_link': row.get('Company_Link', ''),
                'role_title': row.get('Role', ''),
                'role_link': row.get('Role_Link', ''),
                'application_opens': parse_date_for_db(row.get('Application Opens', '')),
                'application_closes': parse_date_for_db(row.get('Application Closes', '')),
                'last_year_opened': parse_date_for_db(row.get('Last Year Opened', '')),
                'interview_stages': row.get('Interview Stages', ''),
                'assessment_platform': row.get('Assessment Platform', ''),
                'online_application': row.get('Online Application', ''),
                'cv_required': row.get('CV Required', ''),
                'cover_letter': row.get('Cover Letter', ''),
                'test_required': row.get('Test Required', ''),
                'notes': row.get('Notes', '')
            }
            roles.append(role_data)
        
        # Delete existing roles and insert new ones
        print("Clearing old data from database...")
        supabase.table('graduate_roles').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        # Insert in batches
        print(f"Inserting {len(roles)} roles into database...")
        batch_size = 100
        for i in range(0, len(roles), batch_size):
            batch = roles[i:i+batch_size]
            supabase.table('graduate_roles').insert(batch).execute()
        
        print(f"\n✓ Successfully saved {len(roles)} records to Supabase")
        
        # Count unique categories and companies
        categories = set(row['Category'] for row in data)
        companies = set(row['Company'] for row in data)
        print(f"\nCategories found: {list(categories)}")
        print(f"Total companies: {len(companies)}")
        
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        import traceback
        traceback.print_exc()


def save_to_csv(data, filename='uk_finance_tracker.csv'):
    """Save scraped data to CSV file"""
    
    if not data:
        print("No data to save!")
        return
    
    # Get field names from first record
    fieldnames = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"\n✓ Successfully saved {len(data)} records to {filename}")
    
    # Count unique categories and companies
    categories = set(row['Category'] for row in data)
    companies = set(row['Company'] for row in data)
    print(f"\nCategories found: {list(categories)}")
    print(f"Total companies: {len(companies)}")


def main():
    """Main execution function"""
    
    print("="*60)
    print("UK Finance Graduate Tracker Scraper")
    print("="*60)
    print()
    
    try:
        data = scrape_tracker()
        
        if data:
            # Save directly to Supabase (primary method)
            save_to_supabase(data)
            
            # Optionally still save CSV as backup
            # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # filename = f'uk_finance_tracker_{timestamp}.csv'
            # save_to_csv(data, filename)
        else:
            print("No data was extracted. The page structure may have changed.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
