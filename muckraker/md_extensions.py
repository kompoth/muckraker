import re
import xml.etree.ElementTree as etree
from pathlib import Path

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import IMAGE_LINK_RE, ImageInlineProcessor


class FilterExtension(Extension):
    """Ignore some tags"""

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.deregister("link")
        md.inlinePatterns.deregister("reference")
        md.inlinePatterns.deregister("short_reference")
        md.inlinePatterns.deregister("backtick")
        md.inlinePatterns.deregister("autolink")
        md.inlinePatterns.deregister("automail")
        md.inlinePatterns.deregister("html")
        md.inlinePatterns.deregister("entity")

        md.parser.blockprocessors.deregister("reference")
        md.parser.blockprocessors.deregister("code")
        md.parser.blockprocessors.deregister("indent")


class ImagePathProcessor(ImageInlineProcessor):
    """Return an `img` element from the given match."""

    def __init__(self, pattern: str, md: Markdown, image_dir: str = "") -> None:
        super().__init__(pattern, md)
        self.image_dir = image_dir

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | None, int | None, int | None]:
        el, start, ind = super().handleMatch(m, data)
        src_path = Path(el.get("src"))
        src_path = Path(self.image_dir) / src_path
        el.set("src", "file://" + str(src_path.resolve()))
        return el, start, ind


class ImagePathExtension(Extension):
    """Modify image paths so that Weasyprint could handle them"""

    def __init__(self, **kwargs) -> None:
        self.config = {"image_dir": ["", "Images root directory"]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.deregister("image_link")
        md.inlinePatterns.deregister("image_reference")
        md.inlinePatterns.deregister("short_image_ref")

        processor = ImagePathProcessor(IMAGE_LINK_RE, md, self.getConfig("image_dir"))
        md.inlinePatterns.register(processor, "image_path", 140)
