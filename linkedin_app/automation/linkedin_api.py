#!/usr/bin/env python3
"""
LinkedIn API Client for Content Posting
Handles authentication and post creation
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "config" / ".env")
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables.")


class LinkedInAPIClient:
    """LinkedIn API client for posting content."""

    def __init__(self, access_token: str = None, user_id: str = None):
        """
        Initialize LinkedIn API client.

        Args:
            access_token: LinkedIn OAuth access token
            user_id: LinkedIn user/organization ID (urn)
        """
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.user_id = user_id or os.getenv('LINKEDIN_USER_ID')

        if not self.access_token:
            raise ValueError("LinkedIn access token not provided. Set LINKEDIN_ACCESS_TOKEN environment variable.")

        if not self.user_id:
            raise ValueError("LinkedIn user ID not provided. Set LINKEDIN_USER_ID environment variable.")

        self.api_base = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        self.logger = logging.getLogger(__name__)

    def test_connection(self) -> bool:
        """
        Test API connection and token validity.

        Returns:
            True if connection successful
        """
        try:
            response = requests.get(
                f"{self.api_base}/me",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("✅ LinkedIn API connection successful")
                return True
            else:
                self.logger.error(f"API connection failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to LinkedIn.

        Args:
            image_path: Path to image file

        Returns:
            Image URN if successful, None otherwise
        """
        try:
            # Step 1: Register upload
            register_url = f"{self.api_base}/assets?action=registerUpload"

            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": self.user_id,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            self.logger.debug(f"Registering upload for: {Path(image_path).name}")

            register_response = requests.post(
                register_url,
                headers=self.headers,
                json=register_payload,
                timeout=30
            )

            if register_response.status_code != 200:
                self.logger.error(f"Registration failed: {register_response.status_code}")
                self.logger.error(f"Response: {register_response.text}")
                return None

            register_data = register_response.json()
            upload_url = register_data['value']['uploadMechanism']\
                ['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_data['value']['asset']

            # Step 2: Upload binary
            with open(image_path, 'rb') as f:
                image_data = f.read()

            upload_headers = {
                'Authorization': f'Bearer {self.access_token}',
            }

            self.logger.debug(f"Uploading {len(image_data) // 1024} KB")

            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=image_data,
                timeout=60
            )

            if upload_response.status_code != 201:
                self.logger.error(f"Upload failed: {upload_response.status_code}")
                return None

            self.logger.info(f"✅ Uploaded: {Path(image_path).name}")
            return asset_urn

        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            return None

    def create_post(self, text: str, image_urns: List[str] = None) -> Optional[str]:
        """
        Create LinkedIn post.

        Args:
            text: Post caption/text
            image_urns: List of uploaded image URNs

        Returns:
            Post ID if successful, None otherwise
        """
        try:
            post_url = f"{self.api_base}/ugcPosts"

            # Build post payload
            post_payload = {
                "author": self.user_id,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE" if image_urns else "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Add images if provided
            if image_urns:
                post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": f"Slide {i+1}"
                        },
                        "media": urn,
                        "title": {
                            "text": f"Slide {i+1}"
                        }
                    }
                    for i, urn in enumerate(image_urns)
                ]

            self.logger.debug("Creating post")

            response = requests.post(
                post_url,
                headers=self.headers,
                json=post_payload,
                timeout=30
            )

            if response.status_code == 201:
                post_id = response.headers.get('X-RestLi-Id')
                self.logger.info(f"✅ Post created: {post_id}")
                return post_id
            else:
                self.logger.error(f"Post creation failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Post creation failed: {e}")
            return None

    def post_carousel(self, image_paths: List[str], caption: str) -> bool:
        """
        Post carousel with multiple images.

        Args:
            image_paths: List of paths to image files
            caption: Post caption/text

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not image_paths:
                self.logger.error("No images provided")
                return False

            if len(image_paths) > 10:
                self.logger.warning(f"LinkedIn supports max 10 images. Using first 10 of {len(image_paths)}")
                image_paths = image_paths[:10]

            # Upload all images
            self.logger.info(f"Uploading {len(image_paths)} images...")
            image_urns = []

            for i, image_path in enumerate(image_paths, 1):
                self.logger.info(f"Uploading slide {i}/{len(image_paths)}")
                urn = self.upload_image(image_path)

                if urn:
                    image_urns.append(urn)
                else:
                    self.logger.error(f"Failed to upload slide {i}")
                    return False

                # Rate limiting: wait between uploads
                if i < len(image_paths):
                    time.sleep(1)

            self.logger.info(f"✅ All {len(image_urns)} images uploaded")

            # Create post
            post_id = self.create_post(caption, image_urns)

            if post_id:
                self.logger.info("🎉 Carousel posted successfully!")
                return True
            else:
                self.logger.error("Failed to create post")
                return False

        except Exception as e:
            self.logger.error(f"Carousel posting failed: {e}")
            return False


def main():
    """Test LinkedIn API client."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn API Client Test")
    parser.add_argument("--test-connection", action="store_true", help="Test API connection")
    parser.add_argument("--test-post", help="Test post with text")
    parser.add_argument("--images", nargs="+", help="Image paths for carousel")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        client = LinkedInAPIClient()

        if args.test_connection:
            print("\n🔍 Testing LinkedIn API connection...")
            success = client.test_connection()
            if success:
                print("✅ Connection successful!")
            else:
                print("❌ Connection failed. Check your credentials.")
                sys.exit(1)

        elif args.test_post:
            if not args.images:
                print("❌ Error: --images required for posting")
                sys.exit(1)

            print(f"\n📤 Posting carousel with {len(args.images)} images...")
            print(f"Caption: {args.test_post[:50]}...")

            success = client.post_carousel(args.images, args.test_post)

            if success:
                print("\n🎉 Post successful!")
            else:
                print("\n❌ Post failed. Check logs above.")
                sys.exit(1)

        else:
            print("Use --test-connection or --test-post")
            print("\nExamples:")
            print("  # Test connection")
            print("  python linkedin_api.py --test-connection")
            print("\n  # Test post")
            print("  python linkedin_api.py --test-post 'Test post' --images image1.jpg image2.jpg")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set up your LinkedIn API credentials:")
        print("1. Create .env file in linkedin_app/config/")
        print("2. Add:")
        print("   LINKEDIN_ACCESS_TOKEN=your_token_here")
        print("   LINKEDIN_USER_ID=your_urn_here")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
