import aiohttp
import asyncio
import json

async def fetch_and_stream(url, model, messages):
    """
    Envoie une requête streaming à l’API et affiche chaque fragment dès réception.
    """
    payload = {"model": model, "messages": messages, "stream": True}
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Erreur HTTP {resp.status} : {text}")

            async for line in resp.content:
                decoded = line.decode('utf-8').strip()
                if not decoded:
                    continue
                if decoded == "data: [DONE]":
                    break
                if decoded.startswith("data: "):
                    try:
                        data = json.loads(decoded[6:])
                    except json.JSONDecodeError:
                        continue
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        print(content, end="", flush=True)

async def main():
    url = "http://localhost:1337/v1/chat/completions"
    model = "gpt-4"
    messages = [
        {"role": "system", "content": "Tu es un assistant utile."},
        {"role": "user", "content": "Écris-moi un poème de 200 mots."}
    ]
    try:
        await fetch_and_stream(url, model, messages)
    except Exception as e:
        print(f"\nErreur : {e}")

if __name__ == "__main__":
    asyncio.run(main())
