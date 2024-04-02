import aiofiles
import asyncio
from fastapi import FastAPI, Response, UploadFile, File, Form
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, IO

from .models import Issue
from .render import render_issue

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
IMAGE_BATCH = 1024
ACCEPTED_FILE_TYPES = ("image/png", "image/jpeg", "image/jpg")

app = FastAPI(root_path="/api")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"]
)


async def process_image(image: IO, dir_path: Path):
    # Validate image
    if image.content_type not in ACCEPTED_FILE_TYPES:
        detail = f"Invalid file type: {image.filename}"
        raise HTTPException(415, detail=detail)
    if image.size > MAX_IMAGE_SIZE:
        detail = f"File is too large: {image.filename}"
        raise HTTPException(413, detail=detail)

    # Save image to the disk
    image_path = dir_path / image.filename
    async with aiofiles.open(image_path, "wb") as fd:
        while content := await image.read(IMAGE_BATCH):
            await fd.write(content)


@app.post("/issue/")
async def create_issue(
    issue: Issue = Form(),
    images: List[UploadFile] = []
):
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Asynchronously process files
        tasks = [process_image(image, temp_dir_path) for image in images]
        await asyncio.gather(*tasks)

        # Render PDF and save it in the temp_dir
        pdf_path = temp_dir_path / "out.pdf"
        render_issue(
            config=issue.config.model_dump(),
            heading=issue.heading.model_dump(),
            body=issue.body,
            output=pdf_path,
            image_dir=temp_dir_path
        )

        # Save PDF to the buffer
        with open(pdf_path, "rb") as fd:
            buf = BytesIO(fd.read())

    # Get it from the buffer
    pdf_bytes = buf.getvalue()
    buf.close()

    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return Response(pdf_bytes, headers=headers, media_type='application/pdf')
