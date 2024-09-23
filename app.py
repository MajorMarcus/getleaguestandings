from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def get_with_retries(url, max_retries=3, backoff_factor=0.5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise error for bad responses
            return response
        except requests.RequestException as e:
            if attempt < max_retries - 1:  # Don't wait after the final attempt
                time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
            else:
                raise e  # If final attempt fails, raise the error

@app.route('/standings/<competition>', methods=['GET'])
def get_standings(competition):
    url = f'https://onefootball.com/en/competition/{competition}/table'
    
    try:
        response = get_with_retries(url)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    standings = []

    # Use CSS selectors for better performance
    rows = soup.select('a.Standing_standings__rowGrid__45OOd')
    for row in rows:
        cells = row.select('div.Standing_standings__cell__5Kd0W')
        
        teamname =  row.select_one('p.Standing_standings__teamName__psv61').get_text(strip=True),
        teamname = teamname.encode('utf-8').decode('utf-8')
        standings.append({
            'league_position': cells[0].get_text(strip=True),
            'team_name': teamname,
            
            'played_matches': cells[2].get_text(strip=True),
            'wins': cells[3].get_text(strip=True),
            'draws': cells[4].get_text(strip=True),
            'losses': cells[5].get_text(strip=True),
            'goal_difference': cells[6].get_text(strip=True),
            'points': cells[7].get_text(strip=True)
        })

   return Response(json.dumps(standings, ensure_ascii=False), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
