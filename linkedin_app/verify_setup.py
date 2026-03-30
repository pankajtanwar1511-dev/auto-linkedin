#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all components are ready for LinkedIn automation
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_pass(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def check_fail(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def check_warn(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def check_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

class SetupVerifier:
    """Verify LinkedIn automation setup."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.app_dir = Path(__file__).parent
        self.issues = []
        self.warnings = []

    def verify_all(self) -> bool:
        """Run all verification checks."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}LinkedIn Automation - Setup Verification{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

        checks = [
            ("Directory Structure", self.check_directory_structure),
            ("Content Files", self.check_content_files),
            ("Configuration Files", self.check_config_files),
            ("Automation Scripts", self.check_automation_scripts),
            ("Python Dependencies", self.check_dependencies),
            ("Environment Variables", self.check_environment),
        ]

        all_passed = True

        for check_name, check_func in checks:
            print(f"\n{Colors.BOLD}Checking: {check_name}{Colors.END}")
            print("-" * 60)

            try:
                passed = check_func()
                if not passed:
                    all_passed = False
            except Exception as e:
                check_fail(f"Check failed with error: {e}")
                all_passed = False

        self.print_summary(all_passed)
        return all_passed

    def check_directory_structure(self) -> bool:
        """Verify directory structure exists."""
        required_dirs = [
            "data",
            "linkedin_app",
            "linkedin_app/automation",
            "linkedin_app/config",
            "linkedin_app/tracker",
            "linkedin_app/logs",
        ]

        all_exist = True
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists():
                check_pass(f"{dir_path}/ exists")
            else:
                check_fail(f"{dir_path}/ missing")
                all_exist = False
                self.issues.append(f"Create directory: {dir_path}/")

        return all_exist

    def check_content_files(self) -> bool:
        """Verify content files (PDFs and captions)."""
        data_dir = self.base_dir / "data"

        if not data_dir.exists():
            check_fail("data/ directory not found")
            return False

        # Count PDFs and TXT files
        pdfs = list(data_dir.glob("ch*.pdf"))
        txts = list(data_dir.glob("ch*.txt"))

        if len(pdfs) == 88:
            check_pass(f"Found all 88 PDFs in data/")
        else:
            check_warn(f"Found {len(pdfs)} PDFs (expected 88)")
            self.warnings.append(f"Only {len(pdfs)} PDFs found")

        if len(txts) == 88:
            check_pass(f"Found all 88 caption files in data/")
        else:
            check_warn(f"Found {len(txts)} caption files (expected 88)")
            self.warnings.append(f"Only {len(txts)} caption files found")

        # Verify naming pattern
        sample_pdf = data_dir / "ch01_topic01_morning.pdf"
        sample_txt = data_dir / "ch01_topic01_morning.txt"

        if sample_pdf.exists() and sample_txt.exists():
            check_pass("Sample files (Day 1) exist with correct naming")
        else:
            check_fail("Sample files missing or incorrect naming")
            self.issues.append("Check file naming: chXX_topicYY_morning.pdf/txt")

        return len(pdfs) >= 1 and len(txts) >= 1

    def check_config_files(self) -> bool:
        """Verify configuration files."""
        config_dir = self.app_dir / "config"

        files_to_check = [
            ("linkedin_config.json", True, "Main configuration file"),
            (".env.example", True, "Environment template"),
            (".env", False, "Your LinkedIn credentials (create from .env.example)"),
        ]

        all_exist = True

        for filename, required, description in files_to_check:
            filepath = config_dir / filename

            if filepath.exists():
                check_pass(f"{filename} - {description}")
            else:
                if required:
                    check_fail(f"{filename} missing - {description}")
                    all_exist = False
                    self.issues.append(f"Create {filename}")
                else:
                    check_warn(f"{filename} not found - {description}")
                    self.warnings.append(f"Create {filename} from .env.example")

        return all_exist

    def check_automation_scripts(self) -> bool:
        """Verify automation scripts exist."""
        automation_dir = self.app_dir / "automation"

        required_scripts = [
            ("linkedin_api_v2.py", "LinkedIn API client (PDF upload)"),
            ("auto_poster.py", "Main automation script"),
        ]

        optional_scripts = [
            ("pdf_converter.py", "PDF to image converter (optional)"),
            ("linkedin_api.py", "Legacy image-based API (optional)"),
        ]

        all_exist = True

        for script, description in required_scripts:
            filepath = automation_dir / script
            if filepath.exists():
                check_pass(f"{script} - {description}")
            else:
                check_fail(f"{script} missing - {description}")
                all_exist = False
                self.issues.append(f"Script missing: {script}")

        for script, description in optional_scripts:
            filepath = automation_dir / script
            if filepath.exists():
                check_pass(f"{script} - {description}")
            else:
                check_info(f"{script} not found - {description}")

        return all_exist

    def check_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        required = [
            ("requests", "HTTP requests for LinkedIn API"),
            ("dotenv", "Environment variable management"),
        ]

        optional = [
            ("pdf2image", "PDF conversion (optional)"),
            ("PIL", "Image processing (optional)"),
        ]

        all_installed = True

        for package, description in required:
            try:
                if package == "dotenv":
                    __import__("dotenv")
                else:
                    __import__(package)
                check_pass(f"{package} installed - {description}")
            except ImportError:
                check_fail(f"{package} not installed - {description}")
                all_installed = False
                self.issues.append(f"Install: pip3 install {package}")

        for package, description in optional:
            try:
                __import__(package)
                check_pass(f"{package} installed - {description}")
            except ImportError:
                check_info(f"{package} not installed - {description}")

        return all_installed

    def check_environment(self) -> bool:
        """Check if environment variables are configured."""
        config_dir = self.app_dir / "config"
        env_file = config_dir / ".env"

        if not env_file.exists():
            check_fail(".env file not found")
            self.issues.append("Create .env file from .env.example")
            self.issues.append("See LINKEDIN_API_SETUP.md for instructions")
            return False

        # Read .env and check for required variables (without exposing values)
        required_vars = [
            "LINKEDIN_ACCESS_TOKEN",
            "LINKEDIN_USER_ID",
        ]

        with open(env_file, 'r') as f:
            env_content = f.read()

        all_configured = True

        for var in required_vars:
            if f"{var}=" in env_content:
                # Check if it has a value (not just "your_token_here")
                lines = [l for l in env_content.split('\n') if l.startswith(f"{var}=")]
                if lines:
                    value = lines[0].split('=', 1)[1].strip()
                    if value and not value.startswith("your_") and value != "urn:li:person:YOUR_ID":
                        check_pass(f"{var} is configured")
                    else:
                        check_fail(f"{var} needs your actual value")
                        all_configured = False
                        self.issues.append(f"Update {var} in .env with your actual value")
            else:
                check_fail(f"{var} not found in .env")
                all_configured = False
                self.issues.append(f"Add {var} to .env file")

        return all_configured

    def print_summary(self, all_passed: bool):
        """Print verification summary."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Verification Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

        if all_passed and not self.issues and not self.warnings:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL CHECKS PASSED!{Colors.END}\n")
            print("Your system is ready for LinkedIn automation.\n")
            print("Next steps:")
            print("  1. Test connection:")
            print("     python3 linkedin_app/automation/auto_poster.py --test-connection")
            print("\n  2. Dry run (test without posting):")
            print("     python3 linkedin_app/automation/auto_poster.py --dry-run")
            print("\n  3. Post Day 1 (for real):")
            print("     python3 linkedin_app/automation/auto_poster.py")
        else:
            if self.issues:
                print(f"{Colors.RED}{Colors.BOLD}Issues Found:{Colors.END}")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue}")
                print()

            if self.warnings:
                print(f"{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.END}")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
                print()

            print(f"{Colors.YELLOW}Next steps:{Colors.END}")
            print("  1. Fix issues listed above")
            print("  2. See LINKEDIN_API_SETUP.md for detailed setup instructions")
            print("  3. Run this script again: python3 linkedin_app/verify_setup.py")

        print()

def main():
    """Main execution."""
    verifier = SetupVerifier()
    success = verifier.verify_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
