#!/usr/bin/env python3
"""
LinkedIn API Client - PDF Document Upload Version
Simplified version that uploads PDFs directly (no image conversion needed)
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional
import logging

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "config" / ".env")
except ImportError:
    pass


class LinkedInPoster:
    """LinkedIn API client for posting PDF documents."""

    def __init__(self, access_token: str = None, user_id: str = None):
        """
        Initialize LinkedIn poster.

        Args:
            access_token: LinkedIn OAuth access token
            user_id: LinkedIn user/organization ID (urn:li:person:XXXX or urn:li:organization:XXXX)
        """
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.user_id = user_id or os.getenv('LINKEDIN_USER_ID')

        if not self.access_token:
            raise ValueError("Set LINKEDIN_ACCESS_TOKEN in .env file")

        if not self.user_id:
            raise ValueError("Set LINKEDIN_USER_ID in .env file")

        self.api_base = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        self.logger = logging.getLogger(__name__)

    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            response = requests.get(
                f"{self.api_base}/me",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                profile = response.json()
                self.logger.info(f"✅ Connected as: {profile.get('localizedFirstName', 'User')}")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def upload_document(self, pdf_path: str, title: str = None) -> Optional[str]:
        """
        Upload PDF document to LinkedIn using Documents API.

        Args:
            pdf_path: Path to PDF file
            title: Document title (optional)

        Returns:
            Document URN if successful
        """
        try:
            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")

            if title is None:
                title = pdf_path.stem

            self.logger.info(f"Uploading PDF: {pdf_path.name}")

            # Step 1: Initialize document upload (NEW Documents API)
            from datetime import datetime
            linkedin_version = datetime.now().strftime("%Y%m")

            init_url = "https://api.linkedin.com/rest/documents?action=initializeUpload"

            init_payload = {
                "initializeUploadRequest": {
                    "owner": self.user_id
                }
            }

            init_headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Linkedin-Version': linkedin_version,
                'X-Restli-Protocol-Version': '2.0.0'
            }

            register_response = requests.post(
                init_url,
                headers=init_headers,
                json=init_payload,
                timeout=30
            )

            if register_response.status_code != 200:
                self.logger.error(f"Document initialization failed: {register_response.status_code}")
                self.logger.error(f"Response: {register_response.text}")
                return None

            register_data = register_response.json()
            upload_url = register_data['value']['uploadUrl']
            document_urn = register_data['value']['document']

            # Step 2: Upload PDF binary
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()

            upload_headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/pdf'
            }

            self.logger.info(f"Uploading {len(pdf_data) // 1024} KB...")

            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=pdf_data,
                timeout=120  # PDFs can be large
            )

            if upload_response.status_code not in [200, 201]:
                self.logger.error(f"Upload failed: {upload_response.status_code}")
                self.logger.error(f"Response: {upload_response.text}")
                return None

            self.logger.info(f"✅ PDF uploaded successfully")
            return document_urn

        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            return None

    def create_post_with_document(self, caption: str, document_urn: str, title: str = None) -> bool:
        """
        Create LinkedIn post with PDF document using new Posts API.

        Args:
            caption: Post caption/text
            document_urn: URN of uploaded document
            title: Document title (not used in new API)

        Returns:
            True if successful
        """
        try:
            # Use new Posts API endpoint
            post_url = "https://api.linkedin.com/rest/posts"

            # New Posts API payload structure
            post_payload = {
                "author": self.user_id,
                "commentary": caption,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                },
                "content": {
                    "media": {
                        "title": title or "C++ Learning Content",
                        "id": document_urn
                    }
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False
            }

            # Add Linkedin-Version header for new API
            from datetime import datetime
            linkedin_version = datetime.now().strftime("%Y%m")

            post_headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Linkedin-Version': linkedin_version,
                'X-Restli-Protocol-Version': '2.0.0'
            }

            self.logger.info("Creating post with new Posts API...")

            response = requests.post(
                post_url,
                headers=post_headers,
                json=post_payload,
                timeout=30
            )

            if response.status_code == 201:
                post_id = response.headers.get('x-restli-id')
                self.logger.info(f"✅ Post created: {post_id}")
                return True
            else:
                self.logger.error(f"Post creation failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Post creation failed: {e}")
            return False

    def post_pdf(self, pdf_path: str, caption: str, title: str = None) -> bool:
        """
        Upload PDF and create post in one step.

        Args:
            pdf_path: Path to PDF file
            caption: Post caption/text
            title: Document title (optional)

        Returns:
            True if successful
        """
        try:
            # Upload document
            document_urn = self.upload_document(pdf_path, title)

            if not document_urn:
                self.logger.error("Failed to upload document")
                return False

            # Create post
            success = self.create_post_with_document(caption, document_urn, title)

            if success:
                self.logger.info("🎉 PDF posted successfully!")
                return True
            else:
                self.logger.error("Failed to create post")
                return False

        except Exception as e:
            self.logger.error(f"Posting failed: {e}")
            return False


def main():
    """Test LinkedIn poster."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn PDF Poster")
    parser.add_argument("--test-connection", action="store_true", help="Test API connection")
    parser.add_argument("--post", help="Path to PDF file to post")
    parser.add_argument("--caption", help="Post caption")
    parser.add_argument("--title", help="Document title")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        poster = LinkedInPoster()

        if args.test_connection:
            print("\n🔍 Testing LinkedIn API connection...")
            if poster.test_connection():
                print("✅ Connection successful! Ready to post.")
            else:
                print("❌ Connection failed. Check your credentials.")
                sys.exit(1)

        elif args.post:
            if not args.caption:
                print("❌ Error: --caption required")
                sys.exit(1)

            print(f"\n📤 Posting PDF: {args.post}")
            print(f"Caption: {args.caption[:50]}...")

            success = poster.post_pdf(args.post, args.caption, args.title)

            if success:
                print("\n🎉 Posted successfully!")
            else:
                print("\n❌ Post failed. Check logs above.")
                sys.exit(1)

        else:
            print("LinkedIn PDF Poster\n")
            print("Usage:")
            print("  # Test connection")
            print("  python linkedin_api_v2.py --test-connection")
            print("\n  # Post PDF")
            print("  python linkedin_api_v2.py --post data/ch01_topic01_morning.pdf \\")
            print("    --caption 'Day 1: Classes and Structs' \\")
            print("    --title 'C++ OOP Fundamentals'")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup steps:")
        print("1. Copy linkedin_app/config/.env.example to .env")
        print("2. Add your LinkedIn credentials:")
        print("   LINKEDIN_ACCESS_TOKEN=your_token")
        print("   LINKEDIN_USER_ID=urn:li:person:YOUR_ID")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
