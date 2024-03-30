from pathlib import Path
import nh3
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from .md_extensions import FilterExtension, ImagePathExtension

STATIC = Path(__file__).parent / "static"
jinja_env = Environment(loader=FileSystemLoader(STATIC / "templates"))
md = Markdown(extensions=[
    "tables", "sane_lists",
    FilterExtension(),
    ImagePathExtension()
])

TAGS = set()


def render_issue(
    issue_config: dict,
    body: str,
    result_path: str
) -> None:
    # Sanitize Markdown and convert it to HTML
    body = md.convert(nh3.clean(body, tags=TAGS))

    # Sanitize all str heading fields
    heading = issue_config["heading"]
    for key, value in heading.items():
        if isinstance(value, str):
            heading.update({key: nh3.clean(value, tags=TAGS)})
    issue_config.update({"heading": heading})

    # Select background
    if issue_config.get("bg") is not None:
        bg_path = STATIC / "bg" / (issue_config["bg"] + ".jpg")
        bg_file_str = "file://" + str(bg_path.resolve())
        issue_config.update({"bg": bg_file_str})

    # Render HTML
    issue_template = jinja_env.get_template("newspaper.html")
    html = issue_template.render(config=issue_config, body=body)

    # Render PDF
    styles = [CSS(STATIC / "style.css"),]
    HTML(string=html).write_pdf(
        result_path,
        stylesheets=styles,
        font_config=FontConfiguration()
    )


if __name__ == "__main__":
    import sys
    import json

    # Load issue configuration
    with open(sys.argv[1], "r") as fd:
        issue_config = json.load(fd)
    # Load issue body
    with open(sys.argv[2], "r") as fd:
        body = fd.read()

    # Create PDF
    render_issue(issue_config, body, sys.argv[3])
