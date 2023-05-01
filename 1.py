import aiohttp
import asyncio
from pydantic import BaseModel
from model import Session, SwapiPeople, engine, Base, select


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
    # starships: list
    # vehicles: list
    url: str


class Swapi:

    base_url = 'https://swapi.dev/api/'
    people_url = base_url + 'people/'
    
    async def _get(self, client, url):
        async with client.get(url) as response:
            json_data = await response.json()
            next_page = json_data['next']
            result = json_data['results']
            yield result, next_page

    async def get_people(self, client):
        next_page = self.people_url
        while next_page: 
            json_data = await self.get_json(client, next_page)
            next_page = json_data['next']
            people = json_data['results']
            yield people

    async def get_json(self, client, url) -> dict:
        async with client.get(url) as response:
            return await response.json()

    async def get_list(self, client, field, urls):
        films_coros = [self.get_json(client, url) for url in urls]
        films = await asyncio.gather(*films_coros)
        return ', '.join([film[field] for film in films])

    async def run(self):
        async with aiohttp.ClientSession() as client:
            g = self.get_people(client)
            peoples = []
            async for people_jsons in g:
                for people_json in people_jsons:
                    films_titles = await self.get_list(
                        client, 'title', people_json['films']
                    )
                    species_titles = await self.get_list(
                        client, 'name', people_json['species']
                    )
                    people_json['films'] = films_titles
                    people_json['species'] = species_titles
                    peoples.append(People(**people_json))
                await self.paste_to_db(peoples)
                break

    async def paste_to_db(self, peoples: list[People]):
        async with Session() as session:
            orm_objects = []
            for item in peoples:
                orm_objects.append(SwapiPeople(**item.dict()))
            session.add_all(orm_objects)
            await session.commit()

    async def print_all(self):
        async with Session() as session:
            q = select(SwapiPeople)
            result = await session.execute(q)
            for r in result.all():
                print(r)


async def main():
    swapi = Swapi()
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)

    await swapi.run()
    await swapi.print_all()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
