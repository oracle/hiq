import shutil
import sys
import traceback
import os


############################
def download_from_http(uri, local_file_path, display=False) -> str:
    import requests

    def get_proxies() -> dict:
        http_proxy = os.environ.get("http_proxy", "")
        https_proxy = os.environ.get("https_proxy", "")
        ftp_proxy = os.environ.get("ftp_proxy", "")
        return {"http": http_proxy, "https": https_proxy, "ftp": ftp_proxy}

    try:
        response = requests.get(uri, verify=False, stream=True, proxies=get_proxies())
        if response.status_code >= 400:
            raise IOError(
                response.status_code,
                f"Error retrieving {uri}. {response.status_code}: {response.text}",
            )
        if not display:
            response.raw.decode_content = True
            with open(local_file_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)
        else:
            pass
        return local_file_path
    except Exception as e:
        print(f"🦉 error: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        raise e
