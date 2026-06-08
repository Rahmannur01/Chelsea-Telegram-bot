from urllib import parse
from bs4 import BeautifulSoup

import os
import json
import httpx

class MSportChelsea:

    BASE_CALENDAR_URL = os.getenv("BASE_CALENDAR_URL")
    NEWS_URL = os.getenv("NEWS_URL")
    TABLE_URL = os.getenv("TABLE_URL")

    def __init__(self):
        self.calendar_params = {
            "tag_id": 1046674,
            "count": 3,
            "type": "next",
            "offset": 0,
            "season_id": 1298623
        }
    
    def create_calendar_url(self, calendar_params):
        if calendar_params == None:
            calendar_params = self.calendar_params

        json_str = json.dumps(calendar_params, ensure_ascii=False)
        encoded = parse.quote(json_str)
        final_url = f"{MSportChelsea.BASE_CALENDAR_URL}?args={encoded}"

        return final_url

    async def get_new_games(self, count = 5):
        cal_param_copy = self.calendar_params
        cal_param_copy['count'] = count
        cal_param_copy['type'] = 'next'

        url = self.create_calendar_url(cal_param_copy)

        text = await self.simple_search(url)
        data = json.loads(text.decode())

        result = []

        if len(data['matches']) == 0:
            print("[!] Could not find new games")
            return result

        mathces = data['matches']['next']

        for match in mathces:
            result.append({
                "first_team" : match['first_team']['name'],
                "second_team" : match['second_team']['name'],
                "tournament_name" : match['tournament']['name'],
                "datetime" : match['match']['start']['bulgakov'],
                "day_of_week" : match['match']['start']['short_day_of_week']
            })

        return result

    async def get_prev_games(self,count = 5):
        cal_param_copy = self.calendar_params
        cal_param_copy['count'] = count
        cal_param_copy['type'] = 'prev'

        url = self.create_calendar_url(cal_param_copy)
        text = await self.simple_search(url)
        data = json.loads(text.decode())

        mathces = data['matches']['prev']
        result = []

        for match in mathces:
            result.append({
                "first_team" : match['first_team']['name'],
                "second_team" : match['second_team']['name'],
                "tournament_name" : match['tournament']['name'],
                "datetime" : match['match']['start']['bulgakov'],
                "day_of_week" : match['match']['start']['short_day_of_week'],
                'result' : match['match']['result'],
                'score' : match['match']['score']
            })
        
        return result

    async def get_news(self):
        data = await self.simple_search(MSportChelsea.NEWS_URL)
        bs = BeautifulSoup(data, "html.parser")
        short_news = bs.find("div", {'class' : 'short-news'})
        titles = short_news.find_all('a', class_="short-text")

        result = ""
        for title in titles:
            result += (title.get_text() + '\n\n')
        
        return result
    
    async def get_news_list(self, count = 1):
        data = await self.simple_search(MSportChelsea.NEWS_URL)
        bs = BeautifulSoup(data, "html.parser")
        short_news = bs.find_all("div", {'class' : 'short-news'}, limit=count)

        result = []

        for news in short_news:
            one_news = news.find_all('p', class_="one_news")
            date = news.find('b').get_text()

            for one_n in one_news:
                time = one_n.find('span', class_="time").get_text()
                text = one_n.find('a', class_="short-text").get_text()
                result.append({
                    'date' : date,
                    'time' : time,
                    'text' : text
                })
        
        return result

    async def get_tournament_table(self):
        data = await self.simple_search(MSportChelsea.TABLE_URL)
        bs = BeautifulSoup(data, "html.parser")

        parent_table = bs.find('table', class_='grouptable')
        trs = parent_table.find_all('tr')

        result = []

        for tr in trs:
            try:
                place = tr.find('td').get_text().strip()
                name = tr.find('a').get_text().strip()
                score = tr.select_one('td strong').get_text().strip()

                result.append({
                    'place' : place,
                    'name' : name,
                    'score' : score
                })
            except:
                continue
        
        return result



    async def simple_search(self, url):
        headers={
            'User-Agent': 'Mozilla/5.0'
        }
        print('[*] Getting data...')
        html = ''
        async with httpx.AsyncClient() as client:
            html = await client.get(url, headers=headers)
        print('[*] Got a data: ')
        return html.read()
