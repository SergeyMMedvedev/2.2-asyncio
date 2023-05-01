# import requests


# def get_swapi_people():
#     next_page = 'https://swapi.dev/api/people/'

#     while next_page:
#         resonse = requests.get(next_page).json()
#         next_page = resonse['next']
#         people = resonse['results']
#         for person in people:
#             yield person

# g = get_swapi_people()


# print(next(g))
# print(next(g))

import aiohttp
import asyncio



async def get_people(start, end):
    async with aiohttp.ClientSession() as client:
        for i in range(start, end):
            async with client.get(
                f"https://swapi.dev/api/people/?page={i}"
            ) as response:
                json_data = await response.json()
                yield json_data


async def main():

    async for item in get_people(1, 2):
        print(item)


asyncio.run(main())
