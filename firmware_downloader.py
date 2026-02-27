"""
Firmware Downloader Module
Handles downloading and validating firmware files from remote servers.
"""

import os
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional
from firmware_parser import FirmwareIndex, Release, Image


class FirmwareDownloader:
    """Downloader for firmware files with MD5 validation"""

    def __init__(self, output_base_dir: str):
        """
        Initialize the firmware downloader.
        
        Args:
            output_base_dir: Base directory for storing downloaded files
        """
        self.base_directory = output_base_dir
        self.create_directory(self.base_directory)

    def download_all(self, index: FirmwareIndex) -> None:
        """
        Download all firmware files from the index.
        
        Args:
            index: FirmwareIndex containing all devices and releases
        """
        print("Starting firmware download...")
        print(f"Index Revision: {index.revision}\n")

        for device in index.devices:
            print(f"Device: {device.productname} ({device.id})")

            for hardware in device.hardware:
                print(f"  Hardware Revision: {hardware.revision}")

                for release in hardware.releases:
                    print(
                        f"    Release: Channel={release.channel}, "
                        f"Date={release.date}, Version={release.revision}"
                    )
                    self.download_release(release, device.productname)

        print("\nDownload completed!")

    def download_release(self, release: Release, device_name: str) -> None:
        """
        Download all images in a release.
        
        Args:
            release: Release object containing images to download
            device_name: Name of the device (for logging)
        """
        for image in release.images:
            url = self.construct_url(release, image)
            output_path = self.construct_output_path(release, image)

            # Create parent directories if needed
            self.create_directory(os.path.dirname(output_path))

            # Check if file already exists and validate
            if os.path.exists(output_path):
                print(f"      Checking: {image.filename}")
                if self.validate_md5(output_path, image.md5):
                    print("      ✓ Already downloaded (MD5 valid)")
                    continue
                else:
                    print("      ⚠ File exists but MD5 invalid, re-downloading...")
                    os.remove(output_path)

            print(f"      Downloading: {image.filename}")

            if self.download_file(url, output_path):
                print("      ✓ Downloaded successfully")
                if self.validate_md5(output_path, image.md5):
                    print("      ✓ MD5 validation passed")
                else:
                    print("      ✗ MD5 validation failed")
            else:
                print("      ✗ Download failed")

    def construct_url(self, release: Release, image: Image) -> str:
        """
        Construct the full URL for a firmware image.
        
        Args:
            release: Release object
            image: Image object
            
        Returns:
            Full URL string
        """
        return f"https://{release.httphost}{release.urlpath}{image.filename}"

    def construct_output_path(self, release: Release, image: Image) -> str:
        """
        Construct the output path for a firmware image.
        Path structure: base_dir/channel/date/version/filename
        
        Args:
            release: Release object
            image: Image object
            
        Returns:
            Output file path
        """
        return os.path.join(
            self.base_directory,
            release.channel,
            release.date,
            release.revision,
            image.filename
        )

    def create_directory(self, path: str) -> bool:
        """
        Create a directory and its parents if needed.
        
        Args:
            path: Directory path
            
        Returns:
            True on success, False on error
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def download_file(self, url: str, output_path: str) -> bool:
        """
        Download a file from a URL.
        
        Args:
            url: URL to download from
            output_path: Path where to save the file
            
        Returns:
            True on success, False on error
        """
        try:
            # Create request with custom header
            req = urllib.request.Request(url)
            req.add_header("X-User-Agent", "OzloSleep/1.0.0")

            # Download with progress tracking
            with urllib.request.urlopen(req, timeout=300) as response:
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(output_path, "wb") as f:
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Show progress
                        if total_size > 0:
                            percent = (downloaded * 100.0) / total_size
                            print(f"\r  Progress: {percent:.1f}%", end="", flush=True)

                print()  # Newline after progress
                return True

        except urllib.error.URLError as e:
            print(f"\nURL error: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return False
        except Exception as e:
            print(f"\nDownload error: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return False

    def calculate_md5(self, file_path: str) -> str:
        """
        Calculate MD5 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 checksum as hex string, empty string on error
        """
        try:
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating MD5 for {file_path}: {e}")
            return ""

    def validate_md5(self, file_path: str, expected_md5: str) -> bool:
        """
        Validate a file's MD5 checksum.
        
        Args:
            file_path: Path to the file
            expected_md5: Expected MD5 checksum
            
        Returns:
            True if MD5 matches, False otherwise
        """
        calculated = self.calculate_md5(file_path)
        is_valid = calculated.lower() == expected_md5.lower()

        if not is_valid:
            print(f"        Expected MD5: {expected_md5}")
            print(f"        Calculated:  {calculated}")

        return is_valid

    def download_index_xml(self, url: str) -> str:
        """
        Download firmware index XML from a URL.
        
        Args:
            url: URL to the index XML
            
        Returns:
            XML content as string, empty string on error
        """
        try:
            # Create request with custom header
            req = urllib.request.Request(url)
            req.add_header("X-User-Agent", "OzloSleep/1.0.0")

            with urllib.request.urlopen(req, timeout=300) as response:
                return response.read().decode("utf-8")

        except urllib.error.URLError as e:
            print(f"URL error: {e}")
            return ""
        except Exception as e:
            print(f"Download error: {e}")
            return ""
