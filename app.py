from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)

def get_image_string(big_string):
    # Extracts the image URL after 'image='
    parts = big_string.split('image=', 1)
    if len(parts) > 1:
        return parts[1]
    return None

@app.route('/standings/<team>', methods=['GET'])
def getstandings(team):
    url = f'https://onefootball.com/en/team/{team}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    leagues = soup.find_all('option')
    allleagues = []
    allleagues1 = []
    for i in leagues:
        allleagues.append(f"/en/competition/uefa-champions-league-{i['value']}/table")
        allleagues1.append(i.text)
        
        
    allleagues.remove(allleagues[0])
    
    league2 = soup.find_all('a', class_='title-7-medium LinkWithArrow_container__AzozQ')
    allleagues1.append(league2[0].text)
    allleagues.append(league2[0]['href'])
    try {
    allleagues = [allleagues[1], allleagues[0]]
    }
    else {
    allleagues=[allleagues[0]
    }
    standings = []
    allstandings = []
    for index, a in enumerate(allleagues):
        standings = []
        url = f'https://onefootball.com/{a}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        leaguepage = a[:-6]
        lpageresponse = requests.get(f'https://onefootball.com/{leaguepage}')
        lpagesoup = BeautifulSoup(lpageresponse.content, 'html.parser')
        leaguelogo = lpagesoup.find('img', class_='EntityTitle_logo__WHQzH')
        leaguelogo = get_image_string(leaguelogo['src'])
        
        rows = soup.select('a.Standing_standings__rowGrid__45OOd')
        
        compname = allleagues1[index]
        
        for row in rows:

            cells = row.select('div.Standing_standings__cell__5Kd0W')
            
            teamname = row.select_one('p.Standing_standings__teamName__psv61')
    
            teamname = teamname.text.encode('utf-8').decode('utf-8')
            
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
        allstandings.append({
            'competition': compname, 
            'logo':leaguelogo,
            'standings': standings
        })

    return jsonify(allstandings)






if __name__ == '__main__':
    app.run(debug=True)
