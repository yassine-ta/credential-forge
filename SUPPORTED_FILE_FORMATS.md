# 📁 CredentialForge Supported File Formats

This document provides a comprehensive overview of all file formats supported by CredentialForge, organized by category.

## 📧 Email Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| EML | `.eml` | Standard email message format |
| MSG | `.msg` | Microsoft Outlook message format |

## 📊 Microsoft Office Excel Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| XLSM | `.xlsm` | Excel macro-enabled workbook |
| XLSX | `.xlsx` | Excel Open XML workbook |
| XLTM | `.xltm` | Excel macro-enabled template |
| XLS | `.xls` | Excel 97-2003 workbook |
| XLSB | `.xlsb` | Excel binary workbook |

## 📝 Microsoft Office Word Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| DOCX | `.docx` | Word Open XML document |
| DOC | `.doc` | Word 97-2003 document |
| DOCM | `.docm` | Word macro-enabled document |
| RTF | `.rtf` | Rich Text Format |

## 📈 Microsoft Office PowerPoint Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PPTX | `.pptx` | PowerPoint Open XML presentation |
| PPT | `.ppt` | PowerPoint 97-2003 presentation |

## 📄 OpenDocument Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| ODF | `.odf` | OpenDocument text document |
| ODS | `.ods` | OpenDocument spreadsheet |
| ODP | `.odp` | OpenDocument presentation |

## 📋 PDF Format

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Portable Document Format |

## 🖼️ Image Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PNG | `.png` | Portable Network Graphics |
| JPG | `.jpg` | Joint Photographic Experts Group |
| JPEG | `.jpeg` | Joint Photographic Experts Group |
| BMP | `.bmp` | Bitmap image |

## 🔧 Visio Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| VSD | `.vsd` | Visio 2003-2010 drawing |
| VSDX | `.vsdx` | Visio drawing |
| VSDM | `.vsdm` | Visio macro-enabled drawing |
| VSSX | `.vssx` | Visio stencil |
| VSSM | `.vssm` | Visio macro-enabled stencil |
| VSTX | `.vstx` | Visio template |
| VSTM | `.vstm` | Visio macro-enabled template |

## 📊 Summary

**Total Supported Formats**: 30

**Categories**:
- Email: 2 formats
- Excel: 5 formats  
- Word: 4 formats
- PowerPoint: 2 formats
- OpenDocument: 3 formats
- PDF: 1 format
- Images: 4 formats
- Visio: 9 formats

## 🔍 Format Validation

Each format includes specific validation logic:

- **Email formats**: Validates MIME headers and structure
- **Office formats**: Validates binary structure and metadata
- **RTF format**: Validates RTF syntax
- **PDF format**: Validates PDF header structure
- **Image formats**: Validates binary image data
- **Visio formats**: Validates binary structure

## 🚀 Usage

All formats can be used with CredentialForge's generation and validation systems:

```python
from credentialforge.utils.validators import Validators

# Check if format is supported
Validators.validate_file_format('xlsx')

# Get format category
category = Validators.get_format_category('docx')  # Returns 'word'

# Get all formats in a category
excel_formats = Validators.get_formats_by_category('excel')
```

## 📝 Notes

- Binary formats (Office, PDF, Images, Visio) cannot have their content easily validated
- Text-based formats (EML, RTF) include content structure validation
- All formats support credential embedding and realistic content generation
- Macro-enabled formats support embedded macro code for advanced scenarios
