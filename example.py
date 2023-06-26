from ultronai_cdn_tools.blob_storage import BlobStorageClient

storage_client = BlobStorageClient()
status, url = storage_client.upload_image(
    "gallery-mobile",
    "/Users/anudeepsekhar/Documents/CMU/Hardtail/image-shelf-1686091880.700568.jpg",
)
print(status, url)