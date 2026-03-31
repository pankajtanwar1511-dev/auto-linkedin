#!/usr/bin/env python3
"""
Automated LinkedIn Daily Poster
Main script that posts PDFs to LinkedIn daily
"""

import os
import sys
import json
import logging
import time
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

# Import our modules
try:
    from linkedin_api_v2 import LinkedInPoster
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from linkedin_api_v2 import LinkedInPoster


class AutoPoster:
    """Automated daily posting system."""

    def __init__(self, config_path: str = None):
        """
        Initialize auto poster.

        Args:
            config_path: Path to linkedin_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "linkedin_config.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Resolve paths relative to script location (not CWD)
        base_dir = Path(__file__).parent.parent.parent  # repo root
        self.data_dir = base_dir / "data"
        self.tracker_file = Path(__file__).parent.parent / self.config['tracking']['tracker_file']

        self.logger = self._setup_logging()
        self.poster = LinkedInPoster()

    def _setup_logging(self):
        """Setup logging."""
        log_file = Path(__file__).parent.parent / self.config['tracking']['log_file']
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def get_next_post(self) -> Optional[Dict]:
        """
        Find next post from tracker.

        Returns:
            Dict with day, pdf_path, caption_path, topic
        """
        try:
            with open(self.tracker_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('[ ]'):
                        # Parse: [ ] Post 1  | ch01_topic01_morning | Topic Title
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            day_part = parts[0].replace('[ ]', '').replace('Post', '').strip()
                            file_base = parts[1].strip()
                            topic_title = parts[2].strip()

                            return {
                                'day': int(day_part),
                                'file_base': file_base,
                                'pdf_path': self.data_dir / f"{file_base}.pdf",
                                'caption_path': self.data_dir / f"{file_base}.txt",
                                'topic': topic_title
                            }

            return None  # All done!

        except Exception as e:
            self.logger.error(f"Error reading tracker: {e}")
            return None

    def load_caption(self, caption_path: Path) -> str:
        """Load caption from file."""
        with open(caption_path, 'r') as f:
            return f.read().strip()

    def _get_jst_now(self) -> datetime:
        """Get current datetime in JST timezone."""
        jst = timezone(timedelta(hours=9))
        return datetime.now(timezone.utc).astimezone(jst)

    def _utc_to_jst(self, dt: datetime) -> datetime:
        """Convert UTC datetime to JST."""
        jst = timezone(timedelta(hours=9))
        if dt.tzinfo is None:
            # Assume naive datetime is UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(jst)

    def _check_already_posted_today(self, time_slot: str) -> bool:
        """
        Check if we already posted in this time slot today (JST).

        Args:
            time_slot: 'morning' or 'evening'

        Returns:
            True if already posted in this slot today
        """
        log_file = Path(__file__).parent.parent / "logs" / "posting_history.json"
        if not log_file.exists():
            return False

        try:
            with open(log_file, 'r') as f:
                history = json.load(f)

            # Get today's date in JST
            today_jst = self._get_jst_now().date()

            # Check last few entries for today's posts
            for entry in reversed(history[-10:]):  # Check last 10 entries
                if not entry.get('success', False):
                    continue

                # Parse timestamp (stored as naive UTC from GitHub Actions)
                entry_time_utc = datetime.fromisoformat(entry['timestamp'])

                # Convert to JST
                entry_time_jst = self._utc_to_jst(entry_time_utc)
                entry_date_jst = entry_time_jst.date()

                if entry_date_jst == today_jst:
                    # Determine if this was morning or evening based on JST hour
                    entry_hour_jst = entry_time_jst.hour
                    entry_slot = 'morning' if 6 <= entry_hour_jst < 12 else 'evening'

                    if entry_slot == time_slot:
                        self.logger.info(f"Found existing {time_slot} post from today (JST): {entry_time_jst.strftime('%Y-%m-%d %H:%M:%S')}")
                        return True

            return False

        except Exception as e:
            self.logger.warning(f"Could not check posting history: {e}")
            return False

    def post_next(self, dry_run: bool = False) -> bool:
        """
        Post next item from queue.

        Args:
            dry_run: If True, don't actually post (testing)

        Returns:
            True if successful
        """
        # Random posting time within fixed 40-minute windows
        # Only apply when running via automation (check if GITHUB_ACTIONS env var exists)
        if os.getenv('GITHUB_ACTIONS') == 'true' and not dry_run:
            # Get current time in JST (GitHub Actions runs in UTC)
            now_jst = self._get_jst_now()
            current_hour_utc = datetime.utcnow().hour
            current_weekday_jst = now_jst.weekday()  # 0=Monday, 6=Sunday (in JST!)

            # Random delay within 40-minute window (0-40 minutes)
            delay_minutes = random.randint(0, 40)

            # Morning: 23:00 UTC (11 PM) = 8:00 AM JST next day
            # Evening: 09:00 UTC (9 AM) = 6:00 PM JST same day
            if current_hour_utc >= 22 or current_hour_utc <= 1:  # Morning run window (22:00-01:00 UTC)
                time_label = "morning"
                window = "8:00-8:40 AM JST"
            else:  # Evening run (triggered at 9:00 AM UTC = 6:00 PM JST)
                # Check if today is an "evening post day" (Tue, Thu, Sat = days 1, 3, 5)
                # Pattern: Mon(1 post), Tue(2 posts), Wed(1), Thu(2), Fri(1), Sat(2), Sun(1)
                evening_post_days = [1, 3, 5]  # Tuesday, Thursday, Saturday

                if current_weekday_jst not in evening_post_days:
                    self.logger.info("⏭️  Skipping evening post (alternating pattern)")
                    return True  # Skip evening post on non-posting days

                time_label = "evening"
                window = "6:00-6:40 PM JST"

            # Safety check: Prevent double-posting in same time slot
            if self._check_already_posted_today(time_label):
                self.logger.info(f"⏭️  Already posted a {time_label} post today - skipping to prevent duplicate")
                return True

            delay_seconds = delay_minutes * 60

            self.logger.info(f"⏰ {time_label.capitalize()} post - Window: {window}")
            self.logger.info(f"⏰ Random delay: {delay_minutes} minutes from workflow start")

            if delay_seconds > 0:
                time.sleep(delay_seconds)

        # Get next post
        next_post = self.get_next_post()

        if next_post is None:
            self.logger.info("🎉 All posts complete!")
            return True

        day = next_post['day']
        pdf_path = next_post['pdf_path']
        caption_path = next_post['caption_path']
        topic = next_post['topic']

        self.logger.info(f"📅 Post {day}: {topic}")
        self.logger.info(f"📄 PDF: {pdf_path.name}")
        self.logger.info(f"📝 Caption: {caption_path.name}")

        # Validate files
        if not pdf_path.exists():
            self.logger.error(f"PDF not found: {pdf_path}")
            return False

        if not caption_path.exists():
            self.logger.error(f"Caption not found: {caption_path}")
            return False

        # Load caption
        caption = self.load_caption(caption_path)
        self.logger.info(f"Caption length: {len(caption)} chars")

        if dry_run:
            self.logger.info("🔍 DRY RUN - Not actually posting")
            self.logger.info(f"Would post:\n{caption[:200]}...")
            return True

        # Post to LinkedIn
        self.logger.info("📤 Posting to LinkedIn...")

        try:
            success = self.poster.post_pdf(
                pdf_path=str(pdf_path),
                caption=caption,
                title=f"Post {day}: {topic}"
            )

            if success:
                self.logger.info(f"✅ Post {day} posted successfully!")

                # Update tracker
                self.mark_complete(day)

                # Log success
                self._log_post(day, topic, success=True)

                return True
            else:
                self.logger.error(f"❌ Failed to post Post {day}")
                self._log_post(day, topic, success=False)
                return False

        except Exception as e:
            self.logger.error(f"Posting error: {e}")
            self._log_post(day, topic, success=False, error=str(e))
            return False

    def mark_complete(self, day: int):
        """
        Mark post as complete in tracker.

        Args:
            day: Post number to mark
        """
        try:
            # Read tracker
            with open(self.tracker_file, 'r') as f:
                lines = f.readlines()

            # Update line
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f'[ ] Post {day} '):
                    lines[i] = line.replace('[ ]', '[X]', 1)
                    updated = True
                    break

            if updated:
                # Write back
                with open(self.tracker_file, 'w') as f:
                    f.writelines(lines)

                self.logger.info(f"✅ Marked Post {day} as complete in tracker")
            else:
                self.logger.warning(f"Could not find Post {day} in tracker")

        except Exception as e:
            self.logger.error(f"Error updating tracker: {e}")

    def _log_post(self, day: int, topic: str, success: bool, error: str = None):
        """Log posting event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'day': day,
            'topic': topic,
            'success': success,
            'error': error
        }

        log_file = Path(__file__).parent.parent / "logs" / "posting_history.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Append to log
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []

            history.append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            self.logger.warning(f"Could not write to history log: {e}")


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Auto Poster")
    parser.add_argument("--dry-run", action="store_true", help="Test without actually posting")
    parser.add_argument("--test-connection", action="store_true", help="Test LinkedIn connection")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("LinkedIn Auto Poster")
    print("="*60 + "\n")

    try:
        poster = AutoPoster()

        if args.test_connection:
            print("🔍 Testing LinkedIn API connection...")
            if poster.poster.test_connection():
                print("✅ Connection successful! Ready to post.")
                sys.exit(0)
            else:
                print("❌ Connection failed. Check your credentials.")
                sys.exit(1)

        # Post next item
        success = poster.post_next(dry_run=args.dry_run)

        if success:
            print("\n✅ Success!")
            sys.exit(0)
        else:
            print("\n❌ Failed")
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup required:")
        print("1. Create linkedin_app/config/.env file")
        print("2. Add your LinkedIn API credentials")
        print("\nSee: linkedin_app/LINKEDIN_API_SETUP.md")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
