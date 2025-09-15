"""File format synthesizers for CredentialForge."""

# New format-only synthesizers
from .format_synthesizer import FormatSynthesizer
from .eml_format_synthesizer import EMLFormatSynthesizer
from .msg_format_synthesizer import MSGFormatSynthesizer
from .excel_format_synthesizer import ExcelFormatSynthesizer
from .word_format_synthesizer import WordFormatSynthesizer, RTFFormatSynthesizer
from .pptx_format_synthesizer import PPTXFormatSynthesizer
from .opendocument_format_synthesizer import OpenDocumentFormatSynthesizer
from .pdf_format_synthesizer import PDFFormatSynthesizer
from .image_format_synthesizer import ImageFormatSynthesizer
from .visio_format_synthesizer import VisioFormatSynthesizer

__all__ = [
    "FormatSynthesizer",
    "EMLFormatSynthesizer",
    "MSGFormatSynthesizer",
    "ExcelFormatSynthesizer",
    "WordFormatSynthesizer",
    "RTFFormatSynthesizer",
    "PPTXFormatSynthesizer",
    "OpenDocumentFormatSynthesizer",
    "PDFFormatSynthesizer",
    "ImageFormatSynthesizer",
    "VisioFormatSynthesizer",
]
