import os
import tempfile
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from loguru import logger
from jinja2 import Template

from app.config import settings


class PDFGenerator:
    """Service for generating PDF documents from markdown with company branding."""
    
    def __init__(self) -> None:
        self.font_config = FontConfiguration()
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.css_path = self.template_dir / "company_template.css"
        self.cover_template_path = self.template_dir / "cover_page.html"
        self.logo_path = self.template_dir / "assets" / "logo.svg"
    
    async def generate_pdf(
        self,
        markdown_content: str,
        image_mapping: Dict[str, str],
        title: str = "Document",
        include_toc: bool = True,
        page_format: str = "A4"
    ) -> bytes:
        """
        Generate PDF from markdown content with company branding.
        
        Args:
            markdown_content: The markdown content to convert
            image_mapping: Mapping of image paths to actual file paths
            title: Document title for cover page
            include_toc: Whether to include table of contents
            page_format: Page format (A4, Letter, etc.)
            
        Returns:
            PDF content as bytes
            
        Raises:
            ValueError: If PDF generation fails
        """
        logger.info(
            "Starting PDF generation",
            extra={
                "title": title,
                "content_length": len(markdown_content),
                "image_count": len(image_mapping),
                "include_toc": include_toc,
                "page_format": page_format
            }
        )
        
        try:
            # Process markdown content
            processed_content = await self._process_markdown_content(markdown_content, image_mapping)
            
            # Generate HTML content
            html_content = await self._generate_html_content(
                processed_content, title, include_toc
            )
            
            # Generate PDF
            pdf_bytes = await self._generate_pdf_from_html(html_content)
            
            logger.info(
                "PDF generation completed successfully",
                extra={
                    "pdf_size": len(pdf_bytes),
                    "title": title
                }
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error("PDF generation failed", extra={"error": str(e), "title": title})
            raise ValueError(f"PDF generation failed: {str(e)}")
    
    async def _process_markdown_content(
        self, 
        markdown_content: str, 
        image_mapping: Dict[str, str]
    ) -> str:
        """Process markdown content and update image references."""
        # Replace image references with actual file paths
        processed_content = markdown_content
        
        for relative_path, actual_path in image_mapping.items():
            # Handle various markdown image syntax patterns
            patterns = [
                rf'!\[([^\]]*)\]\({re.escape(relative_path)}\)',
                rf'!\[([^\]]*)\]\(./{re.escape(relative_path)}\)',
                rf'!\[([^\]]*)\]\(\./{re.escape(relative_path)}\)',
                rf'<img[^>]+src=["\'](?:\.\/)?{re.escape(relative_path)}["\'][^>]*>',
            ]
            
            for pattern in patterns:
                processed_content = re.sub(
                    pattern,
                    lambda m: self._replace_image_reference(m, actual_path),
                    processed_content,
                    flags=re.IGNORECASE
                )
        
        logger.debug(
            "Markdown content processed",
            extra={
                "original_length": len(markdown_content),
                "processed_length": len(processed_content),
                "images_replaced": len(image_mapping)
            }
        )
        
        return processed_content
    
    def _replace_image_reference(self, match, actual_path: str) -> str:
        """Replace image reference with actual file path."""
        if match.group(0).startswith('<img'):
            # HTML img tag
            return re.sub(
                r'src=["\'][^"\']*["\']',
                f'src="file://{actual_path}"',
                match.group(0)
            )
        else:
            # Markdown image syntax
            alt_text = match.group(1) if match.lastindex >= 1 else ""
            return f'![{alt_text}](file://{actual_path})'
    
    async def _generate_html_content(
        self,
        markdown_content: str,
        title: str,
        include_toc: bool
    ) -> str:
        """Generate complete HTML content with cover page and content."""
        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.attr_list',
                'markdown.extensions.md_in_html'
            ],
            extension_configs={
                'markdown.extensions.toc': {
                    'title': 'Table of Contents',
                    'anchorlink': True,
                    'permalink': False
                },
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False
                }
            }
        )
        
        content_html = md.convert(markdown_content)
        toc_html = md.toc if include_toc and hasattr(md, 'toc') else ""
        
        # Generate cover page
        cover_html = await self._generate_cover_page(title)
        
        # Load CSS template
        css_content = await self._load_css_template(title)
        
        # Combine all parts
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
            {css_content}
            </style>
        </head>
        <body>
            {cover_html}
            
            {f'<div class="toc">{toc_html}</div>' if toc_html else ''}
            
            <div class="content">
                {content_html}
            </div>
        </body>
        </html>
        """
        
        logger.debug(
            "HTML content generated",
            extra={
                "html_length": len(full_html),
                "has_toc": bool(toc_html),
                "title": title
            }
        )
        
        return full_html
    
    async def _generate_cover_page(self, title: str) -> str:
        """Generate cover page HTML."""
        try:
            with open(self.cover_template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            cover_html = template.render(
                document_title=title,
                company_name=settings.company_name,
                logo_path=f"file://{self.logo_path}",
                generation_date=datetime.now().strftime("%B %d, %Y"),
                document_subtitle=""
            )
            
            return cover_html
            
        except Exception as e:
            logger.warning(
                "Failed to generate cover page, using fallback",
                extra={"error": str(e)}
            )
            return f"""
            <div class="cover-page">
                <h1 class="document-title">{title}</h1>
                <p>Generated on {datetime.now().strftime("%B %d, %Y")}</p>
                <p>{settings.company_name}</p>
            </div>
            """
    
    async def _load_css_template(self, title: str) -> str:
        """Load and process CSS template."""
        try:
            with open(self.css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Replace template variables
            css_content = css_content.replace("{{ company_name }}", settings.company_name)
            css_content = css_content.replace("{{ document_title }}", title)
            
            return css_content
            
        except Exception as e:
            logger.error("Failed to load CSS template", extra={"error": str(e)})
            raise ValueError(f"Failed to load CSS template: {str(e)}")
    
    async def _generate_pdf_from_html(self, html_content: str) -> bytes:
        """Generate PDF from HTML content using WeasyPrint."""
        try:
            # Create HTML object
            html_doc = HTML(string=html_content, base_url=str(self.template_dir))
            
            # Generate PDF
            pdf_bytes = html_doc.write_pdf(
                font_config=self.font_config,
                optimize_images=True,
                presentational_hints=True
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error("WeasyPrint PDF generation failed", extra={"error": str(e)})
            raise ValueError(f"PDF generation failed: {str(e)}")
    
    def validate_requirements(self) -> bool:
        """Validate that all required files and dependencies are available."""
        required_files = [self.css_path, self.cover_template_path]
        
        for file_path in required_files:
            if not file_path.exists():
                logger.error(f"Required template file missing: {file_path}")
                return False
        
        return True