import asyncio
import datetime

from aiohttp.client import ClientSession
from more_itertools import chunked
from model import Base, SwapiPeople, Session, engine

BASE_URL = "https://swapi.dev/api"
MAX_REQUESTS = 5


async def get_people(client: ClientSession, people_id):
    async with client.get(BASE_URL + f"/people/{people_id}") as response:  # <- тут уже больше для красоты
        json_data = await response.json()
        return json_data


async def paste_to_db(people_jsons):
    async with Session() as session:
        orm_objects = [SwapiPeople(json=item) for item in people_jsons]
        session.add_all(orm_objects)
        await session.commit()


async def main():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    async with ClientSession() as client:
        for people_ids_chunk in chunked(range(1, 51), MAX_REQUESTS):
            person_coros = [
                get_people(client, people_id) for people_id in people_ids_chunk
            ]
            result = await asyncio.gather(*person_coros)
            print(result)
            paste_to_db_coro = paste_to_db(result)
            paste_to_db_task = asyncio.create_task(paste_to_db_coro)
    tasks = asyncio.all_tasks() - {asyncio.current_task(), }
    for task in tasks:
        await task

if __name__ == "__main__":
    start = datetime.datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    print("время работы:", datetime.datetime.now() - start)
