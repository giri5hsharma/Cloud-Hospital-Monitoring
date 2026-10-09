"""Create a GitHub-ready ZIP without credentials or submission documents."""

from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "output" / "SmartHospital_IoT_GitHub_Repository.zip"
ROOT_FILES = ["README.md", ".gitignore", "DEMO_AND_VIVA.md", "SIMULATOR_CODE_GUIDE.md"]
SOURCE_DIRS = ["source", "scripts", "tests", "evidence"]
EXCLUDED_DIRS = {".private", ".build", ".venv", "__pycache__", ".git"}
FORBIDDEN_NAMES = {".env", "local.settings.json", ".ds_store"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".pfx", ".pyc", ".pptx", ".pdf", ".zip"}
SECRET_PATTERNS = [
    re.compile(rb"AccountKey\s*=\s*[A-Za-z0-9+/]{20,}", re.I),
    re.compile(rb"SharedAccessSignature\s*=", re.I),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb'"FUNCTION_KEY"\s*:\s*"[^"\s]{12,}"'),
]

files = [ROOT / name for name in ROOT_FILES]
for folder in SOURCE_DIRS:
    files.extend(
        path for path in (ROOT / folder).rglob("*")
        if path.is_file() and not any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts)
    )
files = sorted(set(files))

for path in files:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        raise SystemExit(f"Forbidden directory: {relative}")
    if path.name.lower() in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise SystemExit(f"Forbidden file: {relative}")
    content = path.read_bytes()
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif"}:
        if any(pattern.search(content) for pattern in SECRET_PATTERNS):
            raise SystemExit(f"Possible credential in {relative}; inspect locally before packaging")

DESTINATION.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(DESTINATION, "w", zipfile.ZIP_DEFLATED) as package:
    for path in files:
        package.write(path, path.relative_to(ROOT))

with zipfile.ZipFile(DESTINATION) as package:
    names = package.namelist()
    if package.testzip() is not None:
        raise SystemExit("ZIP integrity check failed")
    assert not any(name.startswith("output/") for name in names)
    assert not any(name.endswith((".pdf", ".pptx")) for name in names)
    print(f"Created {DESTINATION.name}: {len(names)} files, {DESTINATION.stat().st_size:,} bytes")
