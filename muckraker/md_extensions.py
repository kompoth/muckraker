import re
import xml.etree.ElementTree as etree
from pathlib import Path
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import ImageInlineProcessor, IMAGE_LINK_RE


class FilterExtension(Extension):
    """ Ignore some tags """

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
    """ Return a `img` element from the given match. """

    def handleMatch(
        self,
        m: re.Match[str],
        data: str
    ) -> tuple[etree.Element | None, int | None, int | None]:
        el, start, ind = super().handleMatch(m, data)
        src = str(Path(el.get("src")).resolve())
        el.set("src", "file://" + src)
        return el, start, ind


class ImagePathExtension(Extension):
    """ Modify image paths so that Weasyprint could handle them """

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.deregister("image_link")
        md.inlinePatterns.deregister("image_reference")
        md.inlinePatterns.deregister("short_image_ref")

        md.inlinePatterns.register(
            ImagePathProcessor(IMAGE_LINK_RE, md), "image_path", 140
        )
