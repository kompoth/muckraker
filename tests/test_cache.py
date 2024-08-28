import asyncio

from muckraker.sqlcache import SQLCache


def test_cache(issue_dict, good_image, thick_image):
    # Prepare cache
    cache = SQLCache("test.db")
    asyncio.run(cache.delete_issue("123"))

    # Insert and select issue data
    asyncio.run(cache.put_issue("123", issue_dict))
    select = asyncio.run(cache.get_issue("123"))
    assert select == issue_dict
    select = asyncio.run(cache.get_issue("456"))
    assert select is None

    # Insert some images
    asyncio.run(cache.put_image("123", "test1.png", good_image.read()))
    asyncio.run(cache.put_image("123", "test2.png", thick_image.read()))
