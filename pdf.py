import requests
import json
import time


def generate_upload_url(filename: str) -> json:
    """
    This function takes the filename as the input, and returns a unique fileId
    and uploadUrl for the file.
    :param filename:
    :return: response object which returns fileId and uploadUrl.
    """
    service_url1 = "https://api.pdf-tools.com/v1-beta/files/upload/fromLocal"

    payload_for_upload = json.dumps({
        "fileName": f"{filename}.pdf"
    })

    headers_for_upload = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Api-Key': 'HNaZlCgMEA4Aaf2lDieww7pCkhdx0qA03uWWlXe6'
    }

    response1 = requests.post(service_url1, headers=headers_for_upload, data=payload_for_upload)

    return response1.json()


def upload_local_file(filepath, upload_url):
    """
    The function takes a filepath, for the pdf 
    :param filepath:
    :param upload_url:
    :return: response object, only needed for status code.
    """
    with open(filepath, "rb") as PDFFile:
        response2 = requests.put(upload_url, data=PDFFile)

    return response2


def compressor_and_optimizer(file_id):
    """
    The function runs an HTTP POST request to the compression and optimization service.
    It returns a response object, with the status of the service.
    :param file_id:
    :return: response object, with operation details.
    """
    service_url2 = "https://api.pdf-tools.com/v1-beta/operations/optimize"

    payload_for_compress = json.dumps({
        "options": {
            "profile": "archive"
        },
        "input": {
            "fileId": file_id
        }
    })

    headers_for_compress_post = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Api-Key': 'HNaZlCgMEA4Aaf2lDieww7pCkhdx0qA03uWWlXe6'
    }

    response3 = requests.post(service_url2, headers=headers_for_compress_post, data=payload_for_compress)

    return response3


def endpoint_url(operationId):
    """
    The function triggers endpoint for the PDF compression operation.
    It returns a response object with the download URL, and endpoint status.
    :param operationId:
    :return: response object, with endpoint status.
    """
    service_url3 = f"https://api.pdf-tools.com/v1-beta/operations/{operationId}/result"
    null_payload = {}

    headers_for_endpoint = {
        'Accept': 'application/json',
        'X-Api-Key': 'HNaZlCgMEA4Aaf2lDieww7pCkhdx0qA03uWWlXe6'
    }

    endpoint = requests.get(service_url3, headers=headers_for_endpoint, data=null_payload)

    return endpoint


if __name__ == "__main__":
    fileData = generate_upload_url("os-compressed.pdf")
    filePath = "/home/k0mplex/Downloads/os-aat-images-1-merged_11zon.pdf"

    try:
        response_for_upload = upload_local_file(filePath, fileData["uploadUrl"])
        if response_for_upload.status_code != 200:
            print(response_for_upload.text)
    except KeyError:
        print("Check API Key.")
        exit(1)

    try:
        compression_response = compressor_and_optimizer(fileData["fileId"]).json()
    except KeyError:
        print("Check API Key.")
        exit(1)

    operation_id = compression_response["operationId"]
    endpoint_object = endpoint_url(operation_id).json()
    while endpoint_object["operationStatus"] == "inProgress":
        time.sleep(2)
        endpoint_object = endpoint_url(operation_id).json()

    endData = endpoint_object["outputFile"]
    compressed_url = requests.get(endData["url"])

    # Successful Request
    if compressed_url.status_code == 200:
        name = endData["name"]
        with open(f"/home/k0mplex/Downloads/{name}", "wb") as CompressedPDF:
            CompressedPDF.write(compressed_url.content)

