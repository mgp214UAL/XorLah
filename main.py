import re
import sys
import uuid
import requests

# ============================================================
# Configuration
# ============================================================
API_HOST = "api.wuolah.com"
PREVIEW_EVENTS_URL = f"https://{API_HOST}/v2/preview/events"

COMMON_HEADERS = {
    "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "es-ES,es;q=0.9",
    "Priority": "u=0, i",
}


# ============================================================
# Helpers
# ============================================================
def extract_file_id(url: str) -> int:
    """Extracts the trailing numeric id after the last hyphen in the URL path."""
    match = re.search(r"-(\d+)\s*$", url.strip())
    if not match:
        raise ValueError(f"[ERROR] Could not extract fileId from URL: {url}")
    return int(match.group(1))


def normalize_output_name(name: str) -> str:
    """Appends .pdf extension if missing."""
    name = name.strip()
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def decrypt_pdf(data: bytes) -> bytes:
    """Reverses the XOR applied to the first 128 bytes (key 27)."""
    data = bytearray(data)
    n = min(128, len(data))
    for i in range(n):
        data[i] ^= 27
    return bytes(data)


# ============================================================
# Step 1: Request preview metadata
# ============================================================
def fetch_preview_info(file_id: int, machine_id: str) -> dict:
    payload = {
        "fileId": file_id,
        "adblockDetected": False,
        "captchaCode": None,
        "referralCode": None,
        "machineId": machine_id,
    }

    headers = {
        "Host": API_HOST,
        **COMMON_HEADERS,
        "X-Seg-Machine-Id": machine_id,
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
    }

    print(f"[INFO] Sending POST request to {PREVIEW_EVENTS_URL} with fileId={file_id}")
    response = requests.post(PREVIEW_EVENTS_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"[ERROR] Preview request failed with status {response.status_code}")
        print(response.text[:300])
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        print("[ERROR] Response is not valid JSON")
        print(response.text[:300])
        sys.exit(1)

    print(f"[DEBUG] Server response: {data}")

    if "extension" not in data or data["extension"].lower() != "pdf":
        print(f"[ERROR] Unexpected file extension: {data.get('extension')!r} (expected 'pdf')")
        sys.exit(1)

    if not data.get("isEncrypted", False):
        print("[WARNING] isEncrypted is False — file may not require XOR decryption.")
       

    if "url" not in data:
        print("[ERROR] No 'url' field found in server response")
        sys.exit(1)

    return data


# ============================================================
# Step 2: Download and decrypt the PDF
# ============================================================
def download_and_decrypt(pdf_url: str, output_name: str, is_encrypted: bool):
    headers = {
        "Host": pdf_url.split("/")[2],
        **COMMON_HEADERS,
        "Accept-Encoding": "gzip, deflate",
    }

    print(f"[INFO] Downloading PDF from {pdf_url}")
    response = requests.get(pdf_url, headers=headers)

    if response.status_code != 200:
        print(f"[ERROR] Download failed with status {response.status_code}")
        print(response.text[:300])
        sys.exit(1)

    raw = response.content
    content = decrypt_pdf(raw) if is_encrypted else raw

    if content.startswith(b"%PDF"):
        with open(output_name, "wb") as f:
            f.write(content)
        print(f"[SUCCESS] PDF saved as '{output_name}'")
    else:
        print("[ERROR] Decrypted content does not start with %PDF. Check key/offset.")
        print("[DEBUG] First bytes (raw):       ", raw[:16])
        print("[DEBUG] First bytes (decrypted): ", content[:16])
        sys.exit(1)


# ============================================================
# Main flow
# ============================================================
def main():
    source_url = input("Enter the document URL (e.g: https://wuolah.com/apuntes/estructura-de-computadores-2/parcial-2-hecho-clase-pdf-14445576): ").strip()
    output_name = input("Enter the output filename (default extension: .pdf): ").strip()
    output_name = normalize_output_name(output_name) if output_name else "output.pdf"

    try:
        file_id = extract_file_id(source_url)
    except ValueError as e:
        print(e)
        sys.exit(1)

    machine_id = str(uuid.uuid4())
    print(f"[INFO] Extracted fileId: {file_id}")
    print(f"[INFO] Generated machineId: {machine_id}")

    preview_data = fetch_preview_info(file_id, machine_id)
    pdf_url = preview_data["url"]
    is_encrypted = preview_data.get("isEncrypted", False)

    download_and_decrypt(pdf_url, output_name, is_encrypted)


if __name__ == "__main__":
    main()