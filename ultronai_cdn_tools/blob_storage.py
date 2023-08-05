from azure.storage.blob import (
    AccountSasPermissions,
    BlobServiceClient,
    ResourceTypes,
    generate_account_sas,
)
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ClientAuthenticationError,
)
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import requests


class BlobStorageClient:
    def __init__(self):
        self.logger = self._setup_logger()

        load_dotenv()
        self.account_name = os.getenv("ACCOUNT_NAME")
        self.account_key = os.getenv("ACCOUNT_KEY")
        self.account_url = os.getenv("ACCOUNT_URL")

        # Check if account_name and account_key are set
        if not self.account_name or not self.account_key:
            self.logger.error(
                "Azure Blob Storage account key and account name not found in environment variables."
            )
            raise ValueError(
                "Azure Blob Storage account key and account name not found in environment variables."
            )

        self.blob_service_client = self.__get_blob_service_client()

    def _setup_logger(self):
        logger = logging.getLogger("BlobStorageClient")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("blob_storage.log")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def __get_blob_service_client(self):
        sas_token = generate_account_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            resource_types=ResourceTypes(service=True, object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(minutes=120),
        )

        self.expiry = datetime.utcnow() + timedelta(minutes=1)

        if not self.account_url:
            self.logger.error(
                "Azure Blob Storage account url not found in environment variables."
            )
            raise ValueError(
                "Azure Blob Storage account url not found in environment variables."
            )

        blob_service_client = BlobServiceClient(
            account_url=self.account_url, credential=sas_token
        )
        return blob_service_client

    def get_url_from_path(self, image_path, container_name="gallery"):
        cdn_root = f"{self.account_url}/{container_name}/"
        image_name = "_".join(image_path.split("/")[-2:])
        cdn_url = cdn_root + image_name
        return cdn_url

    def is_image_url(self, url):
        image_formats = (
            "image/png",
            "image/jpeg",
            "image/jpg",
            "application/octet-stream",
        )
        try:
            response = requests.head(url)
            content_type = response.headers.get("Content-Type", "")
            return content_type in image_formats
        except requests.exceptions.RequestException:
            return False

    def reupload(self, blob_client, image_path, max_retry=4):
        rt = 0
        success = False
        while rt < max_retry:
            with open(image_path, "rb") as image_file:
                blob_client.upload_blob(image_file)
            if self.is_image_url(self.get_url_from_path(image_path)):
                success = True
                break
        return success

    def upload_image(self, container_name, image_path, blob_name=None):
        if not blob_name:
            blob_name = "_".join(image_path.split("/")[-2:])

        if datetime.utcnow() > self.expiry:
            self.blob_service_client = self.__get_blob_service_client()

        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )

        try:
            with open(image_path, "rb") as image_file:
                blob_client.upload_blob(image_file)
                image_url = self.get_url_from_path(image_path, container_name)

            if self.is_image_url(image_url):
                self.logger.info(f"Image uploaded successfully. Blob URL: {image_url}")
                return 201, image_url
            else:
                self.reupload(blob_client, image_path)

        except ResourceExistsError:
            self.logger.error(
                f"A blob with the name '{blob_name}' already exists in the container '{container_name}'."
            )
            image_url = self.get_url_from_path(image_path, container_name)
            return 409, image_url

        except ResourceNotFoundError:
            self.logger.error(
                f"The container '{container_name}' does not exist. Please create the container before uploading."
            )
            return 404, None

        except ClientAuthenticationError:
            self.logger.error(f"Authentication failed")
            self.blob_service_client = self.__get_blob_service_client()
            return 401, None

        except Exception as e:
            self.logger.error(f"An error occurred while uploading the image: {str(e)}")
            return 500, None


if __name__ == "__main__":
    storage_client = BlobStorageClient()
    status, url = storage_client.upload_image(
        "gallery-mobile",
        "/Users/anudeepsekhar/Documents/CMU/Hardtail/image-shelf-1686091880.700568.jpg",
    )
    print(status, url)
