from asyncio import gather
import uuid
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from fastapi import FastAPI, File, Response, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .models import Issue
from .render import render_issue
from .sqlcache import SQLCache, CacheError

CACHE_PATH = "cache.sqlite"
MAX_IMAGE_NUM = 4
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
IMAGE_BATCH = 1024
ACCEPTED_FILE_TYPES = ("image/png", "image/jpeg", "image/jpg")
IMAGE_SUFFIXES = (".png", ".jpeg", ".jpg")

# Setup the application
tags_metadata = [{"name": "issue"}]
app = FastAPI(
    title="Muckraker",
    root_path="/api",
    version=__version__,
    summary="A vintage gazette generator for your creative projects.",
    openapi_tags=tags_metadata,
)

# Configure CORS policy
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "PATCH", "GET"],
)

cache = SQLCache(CACHE_PATH)


@app.post("/issue/", tags=["issue"])
async def upload_issue_data(issue: Issue) -> dict:
    issue_id = uuid.uuid4().hex
    await cache.put_issue(issue_id, issue.model_dump())
    return {"issue_id": issue_id}


@app.patch("/issue/{issue_id}", tags=["issue"])
async def upload_images(
    issue_id: str,
    images: List[UploadFile] = File(),
):
    issue = await cache.get_issue(issue_id)
    if issue is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Issue not found")

    # Validate number of images
    image_num = await cache.count_images(issue_id)
    if image_num + len(images) > MAX_IMAGE_NUM:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too many images")

    # Validate images
    for image in images:
        if image.content_type not in ACCEPTED_FILE_TYPES:
            detail = f"Invalid file type: {image.filename}"
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail)
        if image.size > MAX_IMAGE_SIZE:
            detail = f"File is too large: {image.filename}"
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=detail)

    # Save images
    tasks = [cache.put_image(issue_id, image.filename, image.file.read()) for image in images]
    try:
        await gather(*tasks)
    except CacheError as err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(err))
    return JSONResponse(content={"filename": image.filename})


@app.get("/issue/{issue_id}", tags=["issue"])
async def get_issue(issue_id: str):
    # Read issue data
    issue_dict = await cache.get_issue(issue_id)
    if issue_dict is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Issue not found")

    with TemporaryDirectory() as tmp_dir_name:
        dir_path = Path(tmp_dir_name)

        # Extract images
        async for filename, image in cache.load_images(issue_id):
            image_path = dir_path / filename
            with open(image_path, "wb") as fd:
                fd.write(image)

        # Render PDF and write it to buffer
        pdf_path = dir_path / "out.pdf"
        render_issue(
            page=issue_dict["page"],
            header=issue_dict["header"],
            body=issue_dict["body"],
            fonts=issue_dict["fonts"],
            output=pdf_path,
            image_dir=dir_path
        )
        with open(pdf_path, "rb") as fd:
            buf = BytesIO(fd.read())

    # Get pdf from buffer
    pdf_bytes = buf.getvalue()
    buf.close()

    # Delete cached data
    await cache.delete_issue(issue_id)

    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return Response(pdf_bytes, headers=headers, media_type='application/pdf')
