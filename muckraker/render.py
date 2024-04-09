from pathlib import Path

import nh3
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

from .md_extensions import FilterExtension, ImagePathExtension

STATIC = Path(__file__).parent / "static"
jinja_env = Environment(loader=FileSystemLoader(STATIC / "templates"))

TAGS = set()


def font_size_css(selector: str, size_pt: int | None):
    if size_pt is None:
        return ""
    return f"{selector} {{ font-size: {size_pt}pt !important; }}\n"


def render_issue(
    page: dict,
    header: dict,
    body: str,
    fonts: dict,
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

    # Sanitize all str header fields
    for key, value in header.items():
        if isinstance(value, str):
            header.update({key: nh3.clean(value, tags=TAGS)})

    # Select background
    if page.get("bg") is not None:
        bg_path = STATIC / "bg" / (page["bg"] + ".jpg")
        bg_file_str = "file://" + str(bg_path.resolve())
        page.update({"bg": bg_file_str})

    # Render HTML
    issue_template = jinja_env.get_template("newspaper.html")
    html = issue_template.render(
        page=page,
        header=header,
        body=body,
        static="file://" + str(STATIC.resolve())
    )

    # Configure fonts
    font_config = FontConfiguration()
    fonts_css = ""
    fonts_css += font_size_css("header h1", fonts.get("header_title_pt"))
    fonts_css += font_size_css("header h2", fonts.get("header_subtitle_pt"))
    fonts_css += font_size_css(".details", fonts.get("header_details_pt"))
    fonts_css += font_size_css("main h1", fonts.get("main_title_pt"))
    fonts_css += font_size_css("main h2", fonts.get("main_subtitle_pt"))
    fonts_css += font_size_css("main p", fonts.get("main_text_pt"))
    fonts_css = CSS(string=fonts_css, font_config=font_config)

    # Render PDF
    css = CSS(STATIC / "style.css", font_config=font_config)
    HTML(string=html).write_pdf(
        output,
        stylesheets=[css, fonts_css],
        font_config=font_config
    )


if __name__ == "__main__":
    import json
    import sys

    # Load issue config
    with open(sys.argv[1], "r") as fd:
        config = json.load(fd)
    page = config.get("page")
    header = config.get("header")
    fonts = config.get("fonts")

    # Load issue body
    with open(sys.argv[2], "r") as fd:
        body = fd.read()

    # Create PDF
    output = sys.argv[3]
    render_issue(page, header, body, fonts, output, image_dir=".")
