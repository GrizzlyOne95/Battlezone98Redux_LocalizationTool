from __future__ import annotations

import os
import re
from pathlib import Path

APP_NAME = "BZLocalizationTool"
FILE_DESCRIPTION = "Battlezone Localization Tool"
PRODUCT_NAME = "Battlezone Localization Tool"
COMPANY_NAME = "GrizzlyOne95"


def version_from_ref(ref_name: str) -> tuple[tuple[int, int, int, int], str]:
    display = ref_name.strip() or "dev"
    numeric = re.findall(r"\d+", display)
    parts = [int(value) for value in numeric[:4]]
    parts.extend([0] * (4 - len(parts)))
    if not numeric:
        parts = [0, 0, 0, 0]
    return tuple(parts), display.lstrip("vV") or "dev"


def main() -> None:
    version_tuple, _version_text = version_from_ref(os.environ.get("GITHUB_REF_NAME", "dev"))
    version_csv = ", ".join(str(value) for value in version_tuple)
    dotted_version = ".".join(str(value) for value in version_tuple)

    output = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_csv}),
    prodvers=({version_csv}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{COMPANY_NAME}'),
          StringStruct('FileDescription', '{FILE_DESCRIPTION}'),
          StringStruct('FileVersion', '{dotted_version}'),
          StringStruct('InternalName', '{APP_NAME}'),
          StringStruct('OriginalFilename', '{APP_NAME}.exe'),
          StringStruct('ProductName', '{PRODUCT_NAME}'),
          StringStruct('ProductVersion', '{dotted_version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

    destination = Path(__file__).with_name("windows_version_info.txt")
    destination.write_text(output, encoding="utf-8")
    print(f"Wrote {destination} for {APP_NAME} {dotted_version}")


if __name__ == "__main__":
    main()
