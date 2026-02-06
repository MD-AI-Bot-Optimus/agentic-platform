import urllib.request
import ssl
import shutil
import time
import os

def test_download():
    print("Testing download logic...")
    ssl_context = ssl.create_default_context()
    try:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        print("SSL context created (verification disabled).")
    except Exception as e:
        print(f"SSL context creation warning: {e}")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url = "https://loremflickr.com/600/800/handwriting"
    
    print(f"Attempting valid HTTP request to {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            print(f"Response code: {response.getcode()}")
            data = response.read()
            print(f"Read {len(data)} bytes.")
            with open("test_download.jpg", "wb") as f:
                f.write(data)
        print("Download successful.")
    except Exception as e:
        print(f"Download FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download()
