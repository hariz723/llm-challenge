from azure.storage.blob.aio import BlobServiceClient
from ..core.config import settings
from ..core.logging import logger
from fastapi import UploadFile


class AzureStorage:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_name = "documents"  # Or get from config

    async def upload_file(self, file: UploadFile, file_id: str) -> str:
        """
        Uploads a file to Azure Blob Storage.
        Returns the URL of the uploaded blob.
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            try:
                await container_client.create_container()
            except Exception as e:
                if "ContainerAlreadyExists" not in str(
                    e
                ):  # Ignore if container already exists
                    logger.error(f"Error creating container: {e}")
                    raise

            blob_name = f"{file_id}_{file.filename}"
            blob_client = container_client.get_blob_client(blob_name)

            # Read the file content asynchronously
            file_content = await file.read()

            await blob_client.upload_blob(file_content, overwrite=True)
            logger.info(f"Uploaded {blob_name} to Azure Blob Storage.")
            return blob_client.url
        except Exception as e:
            logger.error(f"Error uploading file to Azure Blob Storage: {e}")
            raise

    async def download_file(self, blob_name: str) -> bytes:
        """
        Downloads a file from Azure Blob Storage.
        Returns the content of the blob as bytes.
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(blob_name)
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()
            logger.info(f"Downloaded {blob_name} from Azure Blob Storage.")
            return data
        except Exception as e:
            logger.error(f"Error downloading file from Azure Blob Storage: {e}")
            raise
