# Ultron AI CDN Tools

## Installation 
``` git clone https://github.com/anudeepsekhar/ultronai-cdn-tools.git```

``` pip install -e . ```

## Usage 

```
from ultronai_cdn_tools.blob_storage import BlobStorageClient

storage_client = BlobStorageClient()
status, url = storage_client.upload_image(
    container_name = <Container name you want to upload to>,
    image_path = <Path to image file to upload>,
)
print(status, url)

```

## Status Codes

- **201** - Upload successful
- **409** - Blob already exists
- **404** - Container not found
- **401** - Authorization failed
- **500** - Unknown Error


