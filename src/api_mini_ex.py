import httpx

def fetch_data(url):
    try:
        print("Mengirim request ke:", url)
        response = httpx.get(url)
        print("Status:", response.status_code)

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        print("Terjadi kesalahan HTTP:", e)
        return None
    except Exception as e:
        print("Terjadi kesalahan:", e)
        return None

def print_data(data):
    print(f"""
{data["name"]}

Email: 
{data["email"]}

Website:
{data["website"]}
""")

if __name__ == "__main__":
    url = "https://jsonplaceholder.typicode.com/users/1"
    data = fetch_data(url)
    if data:
        print_data(data)