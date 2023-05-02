import asyncio
import datetime
from typing import AsyncGenerator, Iterable

from aiohttp import ClientSession
from pydantic import BaseModel
from sqlalchemy.future import select

from model import Base, Session, SwapiPeople, engine


class People(BaseModel):
    birth_year: str
    eye_color: str
    films: str
    gender: str
    hair_color: str
    height: str
    homeworld: str
    mass: str
    name: str
    skin_color: str
    species: str
    starships: str
    vehicles: str
    url: str


class Swapi:
    base_url = 'https://swapi.dev/api/'
    people_url = base_url + 'people/'
    additional_fields = [
        ('films', 'title'),
        ('species', 'name'),
        ('starships', 'name'),
        ('vehicles', 'name'),
    ]

    async def get_people(self, client: ClientSession) -> AsyncGenerator:
        """Returns a people page that contains a list of 10 people.

        Args:
            client (ClientSession): client
        """
        next_page = self.people_url
        while next_page:
            json_data = await self.get_json(client, next_page)
            next_page = json_data['next']
            people = json_data['results']
            yield people

    async def get_json(self, client: ClientSession, url: str) -> dict:
        """
        Get json from Swapi response.

        Args:
            client (ClientSession): client
            url (str): url
        """
        async with client.get(url) as response:
            return await response.json()

    async def get_people_field_values(
        self, client: ClientSession, field: str, urls: list[str]
    ) -> str:
        """
        Return a comma-separated list of values by each url in specified field.

        For example:
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/",
            ...
        ]
        became:
        "films": "A New Hope, The Empire Strikes Back..."

        Args:
            client (ClientSession): client
            field (field): field name of received json
            urls (list[str]): url list in specific field
        """
        jsons_coros = [self.get_json(client, url) for url in urls]
        jsons = await asyncio.gather(*jsons_coros)
        return ', '.join([json[field] for json in jsons])

    async def get_people_fields(
        self, client: ClientSession, people_json: dict
    ) -> Iterable:
        """Return zipped list of people fields and it's updated value list."""
        field_names = []
        field_vals_coros = []
        for people_field, value_field in self.additional_fields:
            field_vals_coro = self.get_people_field_values(
                client, value_field, people_json[people_field]
            )
            field_names.append(people_field)
            field_vals_coros.append(field_vals_coro)
        upd_values = await asyncio.gather(*field_vals_coros)
        return zip(field_names, upd_values)

    async def paste_people_to_db(self, people: People) -> None:
        """Paste people to db."""
        async with Session() as session:
            orm_objects = []
            orm_objects.append(SwapiPeople(**people.dict()))
            session.add_all(orm_objects)
            await session.commit()

    async def run(self) -> None:
        """Get all people data from Swapi and write it to database."""
        async with ClientSession() as client:
            g = self.get_people(client)
            async for people_jsons in g:
                for people_json in people_jsons:
                    filled_fields = await self.get_people_fields(
                        client, people_json
                    )
                    for field, values in filled_fields:
                        people_json[field] = values

                    paste_to_db_coro = self.paste_people_to_db(
                        People(**people_json)
                    )
                    asyncio.create_task(paste_to_db_coro)

        tasks = asyncio.all_tasks() - {
            asyncio.current_task(),
        }
        for task in tasks:
            await task

    async def print_all(self) -> None:
        """Print the contents of the database."""
        async with Session() as session:
            q = select(SwapiPeople)
            result = await session.execute(q)
            for r in result.all():
                for f in r:
                    print(f)


async def migrate():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)


async def main():
    swapi = Swapi()
    await migrate()
    await swapi.run()
    await swapi.print_all()


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    print("время работы:", datetime.datetime.now() - start)
