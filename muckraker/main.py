from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
from io import BytesIO

from .models import Issue
from .render import render_issue

app = FastAPI(root_path="/api")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"]
)


@app.post("/issue/")
async def create_issue(issue: Issue):
    with tempfile.TemporaryDirectory() as tempdir:
        # Render PDF and save it in the tempdir
        pdf_tmp_path = Path(tempdir) / "out.pdf"
        render_issue(issue.config.model_dump(), issue.body, pdf_tmp_path)

        # Save PDF to the buffer
        with open(pdf_tmp_path, "rb") as fd:
            buf = BytesIO(fd.read())

    # Get it from the buffer
    pdf_bytes = buf.getvalue()
    buf.close()

    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return Response(pdf_bytes, headers=headers, media_type='application/pdf')
