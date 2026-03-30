#!/usr/bin/env python3
"""
PDF to Image Converter for LinkedIn API
Converts PDF carousel slides to JPEG images
"""

import os
import sys
from pathlib import Path
from typing import List
import logging

try:
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print("Error: Missing dependencies")
    print("Run: pip install pdf2image Pillow")
    sys.exit(1)


class PDFConverter:
    """Convert PDF files to images for LinkedIn API."""

    def __init__(self, output_dir: str = None):
        """
        Initialize converter.

        Args:
            output_dir: Directory to save converted images
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "temp"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

    def convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """
        Convert PDF to list of JPEG images.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of paths to converted images

        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If conversion fails
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.logger.info(f"Converting PDF: {pdf_path.name}")

        try:
            # Convert PDF to images
            # LinkedIn requires: 1080x1080px (square), JPEG format
            images = convert_from_path(
                str(pdf_path),
                dpi=144,  # High quality
                fmt='jpeg',
                size=(1080, 1080),  # LinkedIn carousel size
                thread_count=4  # Faster conversion
            )

            self.logger.info(f"PDF has {len(images)} slides")

            # Save images
            image_paths = []
            base_name = pdf_path.stem

            for i, image in enumerate(images, 1):
                # Ensure image is exactly 1080x1080
                if image.size != (1080, 1080):
                    self.logger.warning(f"Resizing slide {i} from {image.size} to (1080, 1080)")
                    image = image.resize((1080, 1080), Image.LANCZOS)

                # Convert to RGB if needed (remove alpha channel)
                if image.mode != 'RGB':
                    self.logger.info(f"Converting slide {i} to RGB mode")
                    image = image.convert('RGB')

                # Save with high quality
                image_path = self.output_dir / f"{base_name}_slide_{i:02d}.jpg"
                image.save(image_path, 'JPEG', quality=95, optimize=True)

                image_paths.append(str(image_path))
                self.logger.debug(f"Saved: {image_path.name}")

            self.logger.info(f"✅ Converted {len(image_paths)} slides")
            return image_paths

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            raise

    def cleanup_temp_images(self):
        """Delete all temporary images."""
        try:
            for file in self.output_dir.glob("*.jpg"):
                file.unlink()
            self.logger.info("🧹 Cleaned up temporary images")
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")

    def get_image_info(self, image_path: str) -> dict:
        """
        Get image metadata.

        Args:
            image_path: Path to image

        Returns:
            Dict with width, height, size, format
        """
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'size_kb': Path(image_path).stat().st_size // 1024,
                'format': img.format,
                'mode': img.mode
            }


def main():
    """Test converter."""
    import argparse

    parser = argparse.ArgumentParser(description="Convert PDF to images for LinkedIn")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--output-dir", help="Output directory", default="temp")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Convert
    converter = PDFConverter(args.output_dir)

    try:
        image_paths = converter.convert_pdf_to_images(args.pdf_path)

        print("\n✅ Conversion successful!")
        print(f"\nConverted {len(image_paths)} slides:")

        for i, path in enumerate(image_paths, 1):
            info = converter.get_image_info(path)
            print(f"  Slide {i}: {Path(path).name}")
            print(f"    Size: {info['width']}x{info['height']}px")
            print(f"    File: {info['size_kb']} KB")
            print(f"    Format: {info['format']} ({info['mode']})")

        print(f"\nImages saved to: {converter.output_dir}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
