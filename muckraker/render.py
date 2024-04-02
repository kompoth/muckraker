from pathlib import Path
import nh3
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from .md_extensions import FilterExtension, ImagePathExtension

STATIC = Path(__file__).parent / "static"
jinja_env = Environment(loader=FileSystemLoader(STATIC / "templates"))

TAGS = set()


def render_issue(
    config: dict,
    heading: dict,
    body: str,
    output: str,
    image_dir: str = ""
) -> None:
    # Sanitize Markdown and convert it to HTML
    body = nh3.clean(body, tags=TAGS)
    md = Markdown(extensions=[
        "tables",
        "sane_lists",
        FilterExtension(),
        ImagePathExtension(image_dir=image_dir)
    ])
    body = md.convert(body)

    # Sanitize all str heading fields
    for key, value in heading.items():
        if isinstance(value, str):
            heading.update({key: nh3.clean(value, tags=TAGS)})

    # Select background
    if config.get("bg") is not None:
        bg_path = STATIC / "bg" / (config["bg"] + ".jpg")
        bg_file_str = "file://" + str(bg_path.resolve())
        config.update({"bg": bg_file_str})

    # Render HTML
    issue_template = jinja_env.get_template("newspaper.html")
    html = issue_template.render(
        config=config,
        heading=heading,
        body=body,
        static="file://" + str(STATIC.resolve())
    )

    # Render PDF
    font_config = FontConfiguration()
    css = CSS(STATIC / "style.css", font_config=font_config)
    HTML(string=html).write_pdf(
        output,
        stylesheets=[css],
        font_config=font_config
    )


if __name__ == "__main__":
    import sys
    import json

    # Load issue configuration
    with open(sys.argv[1], "r") as fd:
        config = json.load(fd)

    # Load issue heading
    with open(sys.argv[2], "r") as fd:
        heading = json.load(fd)

    # Load issue body
    with open(sys.argv[3], "r") as fd:
        body = fd.read()

    # Create PDF
    output = sys.argv[4]
    render_issue(config, heading, body, output, image_dir=".")
