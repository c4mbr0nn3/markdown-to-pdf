from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from loguru import logger

from app.services.zip_processor import ZipProcessor
from app.services.pdf_generator import PDFGenerator
from app.utils.validators import (
    validate_upload_file,
    validate_title,
    validate_boolean_parameter,
    ValidationError,
    sanitize_filename
)

router = APIRouter(prefix="/api/v1", tags=["conversion"])


@router.post("/convert")
async def convert_markdown_to_pdf(
    file: UploadFile = File(..., description="ZIP file containing markdown and images"),
    title: str = Form(..., description="Document title for cover page"),
    include_toc: str = Form(default="true", description="Include table of contents")
):
    """
    Convert a ZIP file containing markdown and images to a branded PDF document.

    - **file**: ZIP file containing markdown files and images
    - **title**: Document title for the cover page (required)
    - **include_toc**: Include table of contents (default: true)

    Returns a PDF file as binary stream.
    """
    logger.info(
        "PDF conversion request received",
        extra={
            "filename": file.filename,
            "title": title,
            "include_toc": include_toc
        }
    )

    try:
        # Validate inputs
        file_content = await validate_upload_file(file)
        validated_title = validate_title(title)
        validated_include_toc = validate_boolean_parameter(include_toc, "include_toc")

        # Process ZIP file
        zip_processor = ZipProcessor()
        try:
            markdown_content, image_mapping = await zip_processor.process_zip(file_content)

            # Generate PDF
            pdf_generator = PDFGenerator()
            pdf_bytes = await pdf_generator.generate_pdf(
                markdown_content=markdown_content,
                image_mapping=image_mapping,
                title=validated_title,
                include_toc=validated_include_toc,
                page_format="A4"
            )

            # Create safe filename for download
            safe_filename = sanitize_filename(f"{validated_title}.pdf")

            logger.info(
                "PDF conversion completed successfully",
                extra={
                    "title": validated_title,
                    "pdf_size": len(pdf_bytes),
                    "output_filename": safe_filename
                }
            )

            # Return PDF as response
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=\"{safe_filename}\"",
                    "Content-Length": str(len(pdf_bytes))
                }
            )

        finally:
            zip_processor.cleanup()

    except ValidationError:
        raise  # Re-raise validation errors to be handled by exception handler
    except Exception as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "PDF_GENERATION_FAILED",
                    "message": "PDF generation failed",
                    "details": {"error": str(e)},
                    "timestamp": None,
                    "request_id": None
                }
            }
        )