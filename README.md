# Ozlo Firmware Downloader - Python Version

A Python implementation of the Ozlo firmware downloader with identical functionality to the C++ version.

## Features

- **XML Parsing**: Parses firmware.xml to extract firmware release metadata
- **Batch Download**: Downloads all firmware files from releases sequentially
- **Custom Header**: Adds `X-User-Agent: OzloSleep/1.0.0` header to all downloads
- **Organized Storage**: Files are organized in folders: `channel/date/version/filename`
- **MD5 Validation**: Validates downloaded files using MD5 checksums
- **Progress Tracking**: Shows download progress for each file
- **Zero External Dependencies**: Uses only Python standard library

## Requirements

- Python 3.7 or higher

## Installation

## Usage

### Basic usage (downloads index from default URL)
```bash
python3 main.py
```

### Custom index URL
```bash
python3 main.py "https://example.com/index.xml"
```

### Custom index URL and output directory
```bash
python3 main.py "https://example.com/index.xml" "/path/to/output"
```

## File Structure

- `firmware_parser.py` - XML parsing module with data structures
  - `Image` - Represents a firmware image file
  - `Release` - Represents a firmware release
  - `Hardware` - Represents a device hardware revision
  - `Device` - Represents a device
  - `FirmwareIndex` - Represents the complete firmware index
  - `FirmwareParser` - Parser for XML files

- `firmware_downloader.py` - Download and validation module
  - `FirmwareDownloader` - Handles downloading and MD5 validation

- `main.py` - Entry point script
