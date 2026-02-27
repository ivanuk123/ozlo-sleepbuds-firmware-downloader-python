"""
Firmware Parser Module
Parses Ozlo firmware XML index files to extract release and device metadata.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List


@dataclass
class Image:
    """Represents a firmware image file"""
    filename: str = ""
    md5: str = ""
    nxh_version: str = ""
    l_bud_version: str = ""
    r_bud_version: str = ""
    revision: str = ""
    build_id: str = ""
    length: int = 0
    target: int = 0
    subid: int = 0


@dataclass
class Release:
    """Represents a firmware release"""
    channel: str = ""
    date: str = ""
    httphost: str = ""
    urlpath: str = ""
    revision: str = ""
    images: List[Image] = field(default_factory=list)


@dataclass
class Hardware:
    """Represents a device hardware revision"""
    revision: str = ""
    releases: List[Release] = field(default_factory=list)


@dataclass
class Device:
    """Represents a device"""
    id: str = ""
    productname: str = ""
    hardware: List[Hardware] = field(default_factory=list)


@dataclass
class FirmwareIndex:
    """Represents the complete firmware index"""
    revision: str = ""
    devices: List[Device] = field(default_factory=list)


class FirmwareParser:
    """Parser for firmware XML index files"""

    def parse(self, xml_file: str) -> FirmwareIndex:
        """
        Parse a firmware XML file and return the firmware index.
        
        Args:
            xml_file: Path to the XML file
            
        Returns:
            FirmwareIndex: Parsed firmware index
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            return self._parse_root(root)
        except Exception as e:
            print(f"Error: Could not parse XML file: {xml_file}")
            print(f"Details: {e}")
            return FirmwareIndex()

    def parse_from_string(self, xml_content: str) -> FirmwareIndex:
        """
        Parse firmware XML from a string and return the firmware index.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            FirmwareIndex: Parsed firmware index
        """
        try:
            root = ET.fromstring(xml_content)
            return self._parse_root(root)
        except Exception as e:
            print(f"Error: Could not parse XML content")
            print(f"Details: {e}")
            return FirmwareIndex()

    def _parse_root(self, root: ET.Element) -> FirmwareIndex:
        """Parse the root INDEX element"""
        index = FirmwareIndex()

        # Get INDEX revision
        index.revision = root.get("REVISION", "")

        # Iterate through DEVICE elements
        for device_elem in root:
            if device_elem.tag == "DEVICE":
                device = self._parse_device(device_elem)
                index.devices.append(device)

        return index

    def _parse_device(self, device_elem: ET.Element) -> Device:
        """Parse a DEVICE element"""
        device = Device()
        device.id = device_elem.get("ID", "")
        device.productname = device_elem.get("PRODUCTNAME", "")

        # Iterate through HARDWARE elements
        for hw_elem in device_elem:
            if hw_elem.tag == "HARDWARE":
                hardware = self._parse_hardware(hw_elem)
                device.hardware.append(hardware)

        return device

    def _parse_hardware(self, hw_elem: ET.Element) -> Hardware:
        """Parse a HARDWARE element"""
        hardware = Hardware()
        hardware.revision = hw_elem.get("REVISION", "")

        # Iterate through RELEASE elements
        for rel_elem in hw_elem:
            if rel_elem.tag == "RELEASE":
                release = self._parse_release(rel_elem)
                hardware.releases.append(release)

        return hardware

    def _parse_release(self, rel_elem: ET.Element) -> Release:
        """Parse a RELEASE element"""
        release = Release()
        release.channel = rel_elem.get("CHANNEL", "")
        release.date = rel_elem.get("DATE", "")
        release.httphost = rel_elem.get("HTTPHOST", "")
        release.urlpath = rel_elem.get("URLPATH", "")
        release.revision = rel_elem.get("REVISION", "")

        # Iterate through IMAGE elements
        for img_elem in rel_elem:
            if img_elem.tag == "IMAGE":
                image = self._parse_image(img_elem)
                release.images.append(image)

        return release

    def _parse_image(self, img_elem: ET.Element) -> Image:
        """Parse an IMAGE element"""
        image = Image()
        image.filename = img_elem.get("FILENAME", "")
        image.md5 = img_elem.get("MD5", "")
        image.nxh_version = img_elem.get("NXH_VERSION", "")
        image.l_bud_version = img_elem.get("L_BUD_VERSION", "")
        image.r_bud_version = img_elem.get("R_BUD_VERSION", "")
        image.revision = img_elem.get("REVISION", "")
        image.build_id = img_elem.get("BUILD_ID", "")

        # Parse integer fields
        try:
            image.length = int(img_elem.get("LENGTH", "0"))
        except ValueError:
            image.length = 0

        try:
            image.target = int(img_elem.get("TARGET", "0"))
        except ValueError:
            image.target = 0

        try:
            image.subid = int(img_elem.get("SUBID", "0"))
        except ValueError:
            image.subid = 0

        return image
