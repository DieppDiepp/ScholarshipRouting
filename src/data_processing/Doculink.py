# https://github.com/docling-project/docling?tab=readme-ov-file
# https://www.youtube.com/watch?v=Lr1koR-YkMw

import time
from docling.document_converter import DocumentConverter

class cParserCV:
    def __init__(self, link_cv, parsered_content = "", time_processing = 0):
        # Data source can be various formats, including:
        # - Local file path (e.g., "path/to/document.pdf, .png, .jpg, .docx, .txt,...")
        # - URL (e.g., "https://example.com/document.pdf")
        self.link_cv = link_cv
        self.parsered_content = parsered_content
        self.time_processing = time_processing

    def __str__(self):
        return f"ParserCV(link_cv={self.link_cv}, \n        time_processing={self.time_processing}) \n\n parsered_content={self.parsered_content}"

    def parse(self):
        converter = DocumentConverter()

        # Measure processing time
        start_time = time.time()
        result = converter.convert(self.link_cv)
        end_time = time.time()
        self.time_processing = end_time - start_time

        # Export the processed document to Markdown format
        self.parsered_content = result.document.export_to_markdown()

        return self.parsered_content

    def get_time_processing(self):
        return self.time_processing

