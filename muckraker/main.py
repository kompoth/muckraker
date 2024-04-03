import json
from io import BytesIO
from pathlib import Path
from shutil import rmtree
from tempfile import gettempdir, mkdtemp

import aiofiles
from fastapi import Depends, FastAPI, File, Response, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import Issue
from .render import render_issue

MAX_IMAGE_NUM = 4
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
IMAGE_BATCH = 1024
ACCEPTED_FILE_TYPES = ("image/png", "image/jpeg", "image/jpg")
IMAGE_SUFFIXES = (".png", ".jpeg", ".jpg")

app = FastAPI(root_path="/api")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "PATCH", "GET"]
)


@app.post("/issue/")
async def create_s_issue(issue: Issue):
    dir_path = mkdtemp(prefix="muckraker")
    issue_path = Path(dir_path) / "issue.json"
    with open(issue_path, "w") as fd:
        fd.write(issue.model_dump_json())
    return {"issue_id": dir_path.split("muckraker")[-1]}


async def dir_path(issue_id: str):
    dir_path = Path(gettempdir()) / f"muckraker{issue_id}"
    if not (dir_path.exists() and dir_path.is_dir()):
        raise HTTPException(status_code=404, detail="No data")
    return dir_path


@app.patch("/issue/{issue_id}")
async def patch_s_issue(
    dir_path: Path = Depends(dir_path),
    image: UploadFile = File()
):
    # Validate image
    if image.content_type not in ACCEPTED_FILE_TYPES:
        detail = f"Invalid file type: {image.filename}"
        rmtree(dir_path)
        raise HTTPException(415, detail=detail)
    if image.size > MAX_IMAGE_SIZE:
        detail = f"File is too large: {image.filename}"
        rmtree(dir_path)
        raise HTTPException(413, detail=detail)

    # Save image to the disk
    image_path = dir_path / image.filename
    async with aiofiles.open(image_path, "wb") as fd:
        while content := await image.read(IMAGE_BATCH):
            await fd.write(content)
    return JSONResponse(content={"filename": image.filename})


@app.get("/issue/{issue_id}")
async def get_s_issue(dir_path: Path = Depends(dir_path)):
    # Read issue data
    with open(dir_path / "issue.json", "r") as fd:
        issue_dict = json.load(fd)

    # Render PDF and write it to buffer
    pdf_path = dir_path / "out.pdf"
    render_issue(
        config=issue_dict["config"],
        heading=issue_dict["heading"],
        body=issue_dict["body"],
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
