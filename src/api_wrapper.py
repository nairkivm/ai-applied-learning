import httpx

try:

    print("Mengirim request...")

    response = httpx.get(...)

    print("Status:", response.status_code)


    response.raise_for_status()

    print(response.json())

except httpx.HTTPStatusError as e:

    print(e)
