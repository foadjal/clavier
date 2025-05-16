import httpx
import random

WORDS_URL = "https://raw.githubusercontent.com/words/an-array-of-french-words/master/index.json"

async def get_random_words(n=20):
    async with httpx.AsyncClient() as client:
        response = await client.get(WORDS_URL)
        if response.status_code == 200:
            words = response.json()
            return random.sample(words, n)
        else:
            raise Exception("Impossible de récupérer la liste de mots.")
