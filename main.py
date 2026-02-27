#!/usr/bin/env python3
"""
Ozlo Firmware Downloader
A Python application for parsing Ozlo firmware index and downloading 
all release firmware files with automatic verification and organization.
"""

import sys
from firmware_parser import FirmwareParser
from firmware_downloader import FirmwareDownloader


def main():
    """Main entry point for the firmware downloader"""
    index_url = "https://releases.firmware.ozloapp.co/dd/sleepbuds3/index.xml"
    output_dir = "./firmware_downloads"

    # Check for custom arguments
    if len(sys.argv) > 1:
        index_url = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    print("Ozlo Firmware Downloader")
    print("========================")
    print(f"Index URL: {index_url}")
    print(f"Output Directory: {output_dir}\n")

    # Download and parse the XML from URL
    print("Downloading firmware index...")
    downloader = FirmwareDownloader(output_dir)
    xml_content = downloader.download_index_xml(index_url)

    if not xml_content:
        print("Error: Failed to download firmware index", file=sys.stderr)
        return 1

    print("Parsing firmware index...")
    parser = FirmwareParser()
    index = parser.parse_from_string(xml_content)

    if not index.devices:
        print("Error: No devices found in XML file", file=sys.stderr)
        return 1

    print(f"Found {len(index.devices)} device(s)\n")

    # Download all firmware
    downloader.download_all(index)

    return 0


if __name__ == "__main__":
    sys.exit(main())
