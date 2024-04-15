import io
import logging
import os
from pathlib import Path

import dotenv
import requests
from botocore.exceptions import ClientError
from singleton import Singleton


class S3(metaclass=Singleton):
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.BasePath = Path("/mnt/HC_Volume_35080261/cadaster")
        os.makedirs(self.BasePath, exist_ok=True)

    def create_directory(self, directory_path):
        """Create a directory in the S3 bucket.

        :param client: S3 Client
        :param bucket: Bucket to create the directory in
        :param directory_path: Directory path in S3 bucket
        """
        os.makedirs(self.BasePath / directory_path, exist_ok=True)

    def upload_url(self, url, object_name=None, proxies=None):
        """Upload a file to an S3 bucket

        :param client: S3 Client
        :param url: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        response = requests.get(url, proxies=proxies, timeout=60, verify=False)
        response.raise_for_status()

        if object_name is None:
            object_name = url.split("/")[-1]  # Extract the file name from the URL
        # check if object_name has a directory path
        if "/" in object_name:
            directory_path = self.BasePath / ("/".join(object_name.split("/")[:-1]))
            self.create_directory(directory_path)
            file_path = directory_path / object_name.split("/")[-1]

        try:
            file_obj = io.BytesIO(response.content)
            file_size = len(file_obj.getbuffer())
            if file_size == 0:
                raise Exception(f"Empty file {url}")
            with open(file_path, "wb") as file:
                file.write(file_obj.getvalue())

        except Exception as e:
            logging.error(e)
            return 0
        return file_size


def main():
    try:
        s3 = S3()
        url = "https://smid.bot.inbeet.tech/fe7b7c63-1235-42c2-8b93-28700ab3567a.png"
        directory_path = "z/key"
        object_key = f"{directory_path}/img.png"

        s3.upload_url(url, object_key)
    except Exception as exc:
        logging.info(exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
