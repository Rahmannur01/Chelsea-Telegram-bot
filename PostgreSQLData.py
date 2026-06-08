import asyncpg
import asyncio
import os
from MSportParser import MSportChelsea
from logger import logger

class DBChelsea:
    def __init__(self):
        self.conn = None

        self.news_table_name = 'news'
        self.prev_games_table_name = 'prev_games'
        self.next_games_table_name = 'next_games'
        self.tournament_EPL_table_name = 'tournament_table_epl'
    
    async def connect(self):
        logger.info("[*] Connecting to db...")
        self.conn = await asyncpg.connect(
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            host=os.getenv("HOST"),
            port=5432
        )
        logger.info("Success")
    
    async def close(self):
        logger.info("[*] Closing db...")
        await self.conn.close()
        logger.info("[*] Success")
    
    async def is_table_exists(self, name):
        try:
            table_exists = await self.conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = $1
                )
            """, name)

            return table_exists
            
        except Exception as e:
            logger.error(str(e))
        
        return False

    async def clear_table(self, table_name):
        await self.conn.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")

        logger.info(f"[*] Clear '{table_name}' table")

    async def create_news_table(self):
        await self.conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.news_table_name} (
            id SERIAL PRIMARY KEY,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            text TEXT NOT NULL
        )''')

        logger.info(f"[*] Created '{self.news_table_name}' table")
    
    async def create_EPL_table(self):
        await self.conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tournament_EPL_table_name} (
            id SERIAL PRIMARY KEY,
            place INTEGER NOT NULL,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )''')

        logger.info(f"[*] Created '{self.tournament_EPL_table_name}' table")
    
    async def create_prev_games_table(self):
        await self.conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.prev_games_table_name} (
            id SERIAL PRIMARY KEY,
            first_team TEXT NOT NULL,
            second_team TEXT NOT NULL,
            tournament_name TEXT NOT NULL,
            datetime TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            result TEXT NOT NULL,
            score TEXT NOT NULL
        );''')

        logger.info(f"[*] Created '{self.prev_games_table_name}' table")
    
    async def create_next_games_table(self):
        await self.conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.next_games_table_name} (
            id SERIAL PRIMARY KEY,
            first_team TEXT NOT NULL,
            second_team TEXT NOT NULL,
            tournament_name TEXT NOT NULL,
            datetime TEXT NOT NULL,
            day_of_week TEXT NOT NULL
        )''')

        logger.info(f"[*] Created '{self.next_games_table_name}' table")
    
    async def update_news(self, news_count = 5):
        if await self.is_table_exists(self.news_table_name) == False:
            await self.create_news_table()
        
        mSportChelsea = MSportChelsea()
        news_data = await mSportChelsea.get_news_list(news_count)

        await self.clear_table(self.news_table_name)

        async with self.conn.transaction():
            for news in news_data:
                await self.conn.execute(f'INSERT INTO {self.news_table_name} (date, time, text) VALUES ($1, $2, $3)', news['date'], news['time'], news['text'])
                logger.info(f"[*] Inserted new data for '{self.news_table_name}' table")
    
    async def update_prev_games(self, games_count = 10):
        if await self.is_table_exists(self.prev_games_table_name) == False:
            await self.create_prev_games_table()

        mSportChelsea = MSportChelsea()
        games_data = await mSportChelsea.get_prev_games(games_count)

        await self.clear_table(self.prev_games_table_name)

        async with self.conn.transaction():
            for games in games_data:
                await self.conn.execute(f'INSERT INTO {self.prev_games_table_name} (first_team, second_team, tournament_name, datetime, day_of_week, result, score) VALUES ($1, $2, $3, $4, $5, $6, $7);',
                                games['first_team'], 
                                games['second_team'], 
                                games['tournament_name'], 
                                games['datetime'],
                                games['day_of_week'], 
                                games['result'], 
                                games['score']
                )
                logger.info(f"[*] Inserted new data for '{self.prev_games_table_name}' table")

    async def update_next_games(self, games_count = 10):
        if await self.is_table_exists(self.next_games_table_name) == False:
            await self.create_next_games_table()

        mSportChelsea = MSportChelsea()
        games_data = await mSportChelsea.get_new_games(games_count)

        if len(games_data) == 0:
            return

        await self.clear_table(self.next_games_table_name)

        async with self.conn.transaction():
            for games in games_data:
                await self.conn.execute(f'INSERT INTO {self.next_games_table_name} (first_team, second_team, tournament_name, datetime, day_of_week) VALUES ($1, $2, $3, $4, $5)', 
                                games['first_team'], 
                                games['second_team'], 
                                games['tournament_name'], 
                                games['datetime'],
                                games['day_of_week']
                )
                logger.info(f"[*] Inserted new data for '{self.next_games_table_name}' table")
    
    async def update_EPL_table(self):
        if await self.is_table_exists(self.tournament_EPL_table_name) == False:
            await self.create_EPL_table()
        
        mSportChelsea = MSportChelsea()
        EPL_table = await mSportChelsea.get_tournament_table()

        await self.clear_table(self.tournament_EPL_table_name)

        async with self.conn.transaction():
            for team in EPL_table:
                await self.conn.execute(f'INSERT INTO {self.tournament_EPL_table_name} (place, name, score) VALUES ($1, $2, $3);', 
                                int(team['place'][:-1]),
                                team['name'], 
                                int(team['score'])
                )
                logger.info(f"[*] Inserted new data for '{self.tournament_EPL_table_name}' table")
    
    async def get_news(self, count = 5):
        if await self.is_table_exists(self.news_table_name) == False:
            logger.info(f"[!] '{self.news_table_name}' table is not exists")
            return None

        rows = await self.conn.fetch(f'SELECT * FROM {self.news_table_name} LIMIT $1', count)

        data = []

        for row in rows:
            data.append({
                'date' : row[1],
                'time' : row[2],
                'text' : row[3]
            })

        return data
    
    async def get_next_games(self, count = 5):
        if await self.is_table_exists(self.next_games_table_name) == False:
            logger.info(f"[!] '{self.next_games_table_name}' table is not exists")
            return None

        rows = await self.conn.fetch(f'SELECT * FROM {self.next_games_table_name} LIMIT $1', count)

        data = []

        for row in rows:
            data.append({
                'first_team' : row[1],
                'second_team' : row[2],
                'tournament_name' : row[3],
                'datetime' : row[4],
                'day_of_week' : row[5]
            })

        return data
    
    async def get_prev_games(self, count = 5):
        if await self.is_table_exists(self.prev_games_table_name) == False:
            logger.info(f"[!] '{self.prev_games_table_name}' table is not exists")
            return None

        rows = await self.conn.fetch(f'SELECT * FROM {self.prev_games_table_name} LIMIT $1;', count)

        data = []

        for row in rows:
            data.append({
                'first_team' : row[1],
                'second_team' : row[2],
                'tournament_name' : row[3],
                'datetime' : row[4],
                'day_of_week' : row[5],
                'result' : row[6],
                'score' : row[7]
            })

        return data

    async def get_EPL_table(self):
        if await self.is_table_exists(self.tournament_EPL_table_name) == False:
            logger.info(f"[!] '{self.tournament_EPL_table_name}' table is not exists")
            return None

        rows = await self.conn.fetch(f'SELECT * FROM {self.tournament_EPL_table_name}')

        data = []

        for row in rows:
            data.append({
                'place' : row[1],
                'name' : row[2],
                'score' : row[3]
            })

        return data

    async def update_all_data(self):
        await self.update_next_games()
        await self.update_prev_games()
        await self.update_EPL_table()
        await self.update_news()

async def main():
    dbChelsea = DBChelsea()
    await dbChelsea.connect()
    await dbChelsea.update_all_data()
    await dbChelsea.close()

if __name__ == "__main__":
    asyncio.run(main())