import asyncio

from .queries import determine_query


def process_query(text: str) -> str:
    try:
        Query = determine_query(text)
        query = Query.parse(text)
        result = asyncio.run(query.run())
        return result

    except Exception as e:
        response = f"Error: {e}"
    return response
