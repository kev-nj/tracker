"""
UK Finance Tracker Web Application with Supabase
Flask backend with authentication and database storage
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import csv
from datetime import datetime
import openai
import requests
from bs4 import BeautifulSoup
import subprocess
import traceback
from supabase import create_client, Client
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())
CORS(app)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Initialize clients
openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No authorization token'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            # Verify token with Supabase
            user = supabase.auth.get_user(token)
            request.user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
    
    return decorated_function


def run_scraper():
    """Run the scraper script which now writes directly to Supabase"""
    try:
        print(f"[{datetime.now()}] Running scraper...")
        result = subprocess.run(
            ['python', 'scraper.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] Scraper completed successfully")
            print(result.stdout)
        else:
            print(f"[{datetime.now()}] Scraper failed: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] Error running scraper: {e}")
        traceback.print_exc()


def import_csv_to_supabase(csv_file):
    """Import CSV data to Supabase"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            roles = []
            
            for row in reader:
                # Parse dates
                app_opens = parse_date_for_db(row.get('Application Opens', ''))
                app_closes = parse_date_for_db(row.get('Application Closes', ''))
                last_year = parse_date_for_db(row.get('Last Year Opened', ''))
                
                role_data = {
                    'category': row.get('Category', ''),
                    'company_name': row.get('Company', ''),
                    'company_link': row.get('Company_Link', ''),
                    'role_title': row.get('Role', ''),
                    'role_link': row.get('Role_Link', ''),
                    'application_opens': app_opens,
                    'application_closes': app_closes,
                    'last_year_opened': last_year,
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
        supabase_admin.table('graduate_roles').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        # Insert in batches
        batch_size = 100
        for i in range(0, len(roles), batch_size):
            batch = roles[i:i+batch_size]
            supabase_admin.table('graduate_roles').insert(batch).execute()
        
        print(f"[{datetime.now()}] Successfully imported {len(roles)} roles to Supabase")
        
    except Exception as e:
        print(f"Error importing to Supabase: {e}")
        traceback.print_exc()


def parse_date_for_db(date_str):
    """Parse date string to ISO format for database"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        dt = datetime.strptime(date_str.strip(), '%d %b %y')
        return dt.date().isoformat()
    except:
        return None


def parse_date(date_str):
    """Parse date string in format 'DD Mon YY' to datetime object"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d %b %y')
    except:
        return None


def is_role_open(role):
    """Check if a role is currently open based on application dates"""
    today = datetime.now().date()
    
    app_opens = role.get('application_opens')
    app_closes = role.get('application_closes')
    
    if not app_opens:
        return False
    
    try:
        opens_date = datetime.fromisoformat(app_opens).date() if isinstance(app_opens, str) else app_opens
        if opens_date > today:
            return False
        
        if app_closes:
            closes_date = datetime.fromisoformat(app_closes).date() if isinstance(app_closes, str) else app_closes
            if closes_date < today:
                return False
        
        return True
    except:
        return False


def fetch_page_content(url):
    """Fetch content from a URL"""
    if not url or url.strip() == '':
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"Fetching content from: {url}")
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 403:
            print(f"Access denied (403) for {url}")
            return f"[Unable to access page - access denied]"
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(['script', 'style', 'header', 'footer', 'nav']):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"Successfully fetched {len(text)} characters from {url}")
        return text[:5000]
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching {url}: {e}")
        return f"[Unable to access page - HTTP {e.response.status_code}]"
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


# Authentication endpoints
# Note: Signup is disabled - admin creates users manually in Supabase Dashboard
# @app.route('/api/auth/signup', methods=['POST'])
# def signup():
#     """User signup - DISABLED"""
#     return jsonify({'success': False, 'error': 'Signup disabled. Contact admin for account.'}), 403


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if auth_response.user:
            return jsonify({
                'success': True,
                'user': {
                    'id': auth_response.user.id,
                    'email': auth_response.user.email
                },
                'session': {
                    'access_token': auth_response.session.access_token
                }
            })
        
        return jsonify({'success': False, 'error': 'Login failed'}), 401
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 401


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout"""
    try:
        supabase.auth.sign_out()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user_id = request.user.user.id
        # Use admin client to bypass RLS
        response = supabase_admin.table('user_profiles').select('*').eq('id', user_id).execute()
        
        print(f"DEBUG GET: user_id={user_id}, found={len(response.data)} rows")
        
        # If profile doesn't exist, return empty profile
        if not response.data:
            return jsonify({
                'success': True,
                'profile': {'id': user_id, 'email': request.user.user.email}
            })
        
        return jsonify({
            'success': True,
            'profile': response.data[0]
        })
    except Exception as e:
        print(f"ERROR getting profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        user_id = request.user.user.id
        data = request.json
        data['id'] = user_id
        data['email'] = request.user.user.email
        
        # Use upsert to insert or update
        supabase_admin.table('user_profiles').upsert(data).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/roles')
def get_roles():
    """Get all roles with optional filtering"""
    open_only = request.args.get('open', 'false').lower() == 'true'
    
    try:
        response = supabase.table('graduate_roles').select('*').execute()
        roles = response.data
        
        # Add open status
        for role in roles:
            role['is_open'] = is_role_open(role)
        
        if open_only:
            roles = [r for r in roles if r['is_open']]
        
        # Sort by opening date
        roles.sort(key=lambda x: x.get('application_opens') or '1900-01-01', reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(roles),
            'roles': roles
        })
    except Exception as e:
        print(f"Error getting roles: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-cover-letter', methods=['POST'])
@require_auth
def generate_cover_letter():
    """Generate a cover letter for a specific role using OpenAI"""
    try:
        user_id = request.user.user.id
        request_data = request.json
        
        company = request_data.get('company', '')
        role = request_data.get('role', '')
        company_link = request_data.get('company_link', '')
        role_link = request_data.get('role_link', '')
        notes = request_data.get('notes', '')
        
        # Get user profile for personalization
        # Use admin client to bypass RLS
        profile_response = supabase_admin.table('user_profiles').select('*').eq('id', user_id).execute()
        
        # Use empty profile if doesn't exist
        profile = profile_response.data[0] if profile_response.data else {}
        
        print(f"DEBUG: user_id={user_id}, Profile data: {profile}")
        
        # Build user info from profile
        user_info_parts = []
        if profile.get('full_name'):
            user_info_parts.append(f"Name: {profile['full_name']}")
        if profile.get('university'):
            user_info_parts.append(f"University: {profile['university']}")
        if profile.get('degree'):
            user_info_parts.append(f"Degree: {profile['degree']}")
        if profile.get('graduation_year'):
            user_info_parts.append(f"Graduation Year: {profile['graduation_year']}")
        if profile.get('gpa'):
            user_info_parts.append(f"GPA: {profile['gpa']}")
        if profile.get('skills'):
            user_info_parts.append(f"Skills: {', '.join(profile['skills'])}")
        if profile.get('experience'):
            user_info_parts.append(f"Experience: {profile['experience']}")
        if profile.get('achievements'):
            user_info_parts.append(f"Achievements: {profile['achievements']}")
        if profile.get('interests'):
            user_info_parts.append(f"Interests: {profile['interests']}")
        
        user_info = "\n".join(user_info_parts) if user_info_parts else "No profile information provided"
        
        # Fetch additional context from links
        company_context = ""
        role_context = ""
        
        print(f"\nGenerating cover letter for {company} - {role}")
        
        if company_link:
            print(f"Fetching company page: {company_link}")
            content = fetch_page_content(company_link)
            if content and not content.startswith("[Unable to access"):
                company_context = f"\n\nCompany information from tracker:\n{content}"
            elif content:
                print(f"Could not access company page: {content}")
        
        if role_link:
            print(f"Fetching role page: {role_link}")
            content = fetch_page_content(role_link)
            if content and not content.startswith("[Unable to access"):
                role_context = f"\n\nDetailed role description:\n{content}"
            elif content:
                print(f"Could not access role page: {content}")
        
        # Create prompt for OpenAI
        prompt = f"""Write a professional cover letter for the following graduate role:

Company: {company}
Role: {role}
Additional Notes: {notes}
{company_context}
{role_context}

Candidate Information:
{user_info}

Requirements:
- Professional and enthusiastic tone
- Highlight relevant skills and experience from the candidate's profile
- Reference the specific company and programme
- Keep it concise (250-300 words)
- Format it properly with appropriate paragraphs
- Make it personalized and compelling

Write the cover letter now:"""

        # Call OpenAI API
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert career advisor specializing in finance graduate applications. Write compelling, professional cover letters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        cover_letter = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'cover_letter': cover_letter
        })
        
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scrape-now', methods=['POST'])
def scrape_now():
    """Manually trigger the scraper"""
    try:
        run_scraper()
        return jsonify({
            'success': True,
            'message': 'Scraper executed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status')
def status():
    """Get application status"""
    try:
        response = supabase.table('graduate_roles').select('*').execute()
        roles = response.data
        
        for role in roles:
            role['is_open'] = is_role_open(role)
        
        open_roles = [r for r in roles if r['is_open']]
        
        return jsonify({
            'success': True,
            'total_roles': len(roles),
            'open_roles': len(open_roles),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Run scraper once at startup if database is empty
    try:
        response = supabase_admin.table('graduate_roles').select('id').limit(1).execute()
        if not response.data:
            print("No roles in database. Running initial scrape...")
            run_scraper()
    except:
        print("Database empty or error. Running initial scrape...")
        run_scraper()
    
    print(f"\n{'='*60}")
    print(f"UK Finance Tracker App Started")
    print(f"{'='*60}")
    print(f"🌐 Open in browser: http://localhost:8080")
    print(f"🔄 Auto-refresh: Disabled (use manual refresh button)")
    print(f"🤖 OpenAI Model: {OPENAI_MODEL}")
    print(f"🗄️  Database: Supabase")
    print(f"{'='*60}\n")
    
    try:
        app.run(debug=True, port=8080, use_reloader=False, host='0.0.0.0')
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down...")
        print("Goodbye!")
