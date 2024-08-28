import json

import aiosqlite


class SQLCache:
    def __init__(self, path: str) -> None:
        self.path = path

    async def setup(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    issue_id VARCHAR(32) PRIMARY KEY,
                    data BLOB,
                    ts TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    issue_id VARCHAR(32) NOT NULL,
                    name TEXT NOT NULL,
                    image BLOB,
                    FOREIGN KEY (issue_id) REFERENCES issues (issue_id)
                )
            """)

    async def put_issue(self, issue_id: str, issue_dict: dict) -> None:
        data = json.dumps(issue_dict).encode('utf-8')
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO issues (issue_id, data) VALUES (?, ?)", (issue_id, data))
            await db.commit()

    async def put_image(self, issue_id: str, name: str, image: bytes) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO images (issue_id, name, image) VALUES (?, ?, ?)", (issue_id, name, image))
            await db.commit()

    async def delete_issue(self, issue_id: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM images WHERE issue_id = ?", (issue_id,))
            await db.execute("DELETE FROM issues WHERE issue_id = ?", (issue_id,))
            await db.commit()

    async def get_issue(self, issue_id: str) -> dict:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT data FROM issues WHERE issue_id = ?", (issue_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                else:
                    return None

    async def load_images(self, issue_id: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT name, image FROM images WHERE issue_id = ?", (issue_id,)) as cursor:
                async for row in cursor:
                    name = row[0]
                    image = row[1]
                    yield name, image
