import json
from io import BytesIO
from pathlib import Path
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
from typing import List

import aiofiles
from fastapi import Depends, FastAPI, File, Response, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .models import Issue
from .render import render_issue

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
    openapi_tags=tags_metadata
)

# Configure CORS policy
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "PATCH", "GET"]
)


async def get_dir_path(issue_id: str):
    dir_path = Path(gettempdir()) / f"muckraker{issue_id}"
    if not (dir_path.exists() and dir_path.is_dir()):
        raise HTTPException(status_code=404, detail="No data")
    return dir_path


@app.exception_handler(RequestValidationError)
async def clear_tempdir_handler(request, exc):
    issue_id = request.path_params.get("issue_id")
    if issue_id:
        rmtree(await get_dir_path(issue_id))
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.post("/issue/", tags=["issue"])
async def upload_issue_data(issue: Issue):
    dir_path = mkdtemp(prefix="muckraker")
    issue_path = Path(dir_path) / "issue.json"
    with open(issue_path, "w") as fd:
        fd.write(issue.model_dump_json())
    return {"issue_id": dir_path.split("muckraker")[-1]}


@app.patch("/issue/{issue_id}", tags=["issue"])
async def upload_images(
    dir_path: Path = Depends(get_dir_path),
    images: List[UploadFile] = File()
):
    # Check if there are already images
    uploaded_files = dir_path.glob('**/*')
    uploaded_images = [
        x for x in uploaded_files
        if x.is_file() and x.suffix in IMAGE_SUFFIXES
    ]
    if len(uploaded_images) > 0:
        rmtree(dir_path)
        raise HTTPException(429, detail="To many uploads")

    # Validate number of images
    if len(images) > MAX_IMAGE_NUM:
        rmtree(dir_path)
        raise HTTPException(413, detail="To many images")

    # Validate images
    for image in images:
        if image.content_type not in ACCEPTED_FILE_TYPES:
            detail = f"Invalid file type: {image.filename}"
            rmtree(dir_path)
            raise HTTPException(415, detail=detail)
        if image.size > MAX_IMAGE_SIZE:
            detail = f"File is too large: {image.filename}"
            rmtree(dir_path)
            raise HTTPException(413, detail=detail)

    # Save images to the disk
    for image in images:
        image_path = dir_path / image.filename
        async with aiofiles.open(image_path, "wb") as fd:
            while content := await image.read(IMAGE_BATCH):
                await fd.write(content)
    return JSONResponse(content={"filename": image.filename})


@app.get("/issue/{issue_id}", tags=["issue"])
async def get_issue(dir_path: Path = Depends(get_dir_path)):
    # Read issue data
    with open(dir_path / "issue.json", "r") as fd:
        issue_dict = json.load(fd)

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

    # Delete tempdir
    rmtree(dir_path)

    # Get pdf from buffer
    pdf_bytes = buf.getvalue()
    buf.close()

    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return Response(pdf_bytes, headers=headers, media_type='application/pdf')
