import click
import os
from tqdm import tqdm

from ultronai_cdn_tools import BlobStorageClient

from joblib import Parallel, delayed

def upload_file(image_file, container_name=None, root=None, storage_client=None):
    if not os.path.exists(image_file):
        if root:
            image_file = os.path.join(root, image_file)
        else:
            raise FileNotFoundError('invalid file paths. You can use --root to provide root directory if paths are partial.')
    if not os.path.exists(image_file):
        raise FileNotFoundError('invalid root or file paths.')
    else:
        print(image_file)
        print(container_name)
        status, url = storage_client.upload_image(container_name,image_file)
    
    return url

@click.command()
@click.option(
    '--source',
    required=True
)
@click.option('--type',
              type=click.Choice(['txt', 'image'], case_sensitive=False),
              required=True
)
@click.option(
    '--root',
    required=False
)
@click.option(
    '--container_name',
    required=True,
    default='gallery-references'
)
@click.option(
    '--parallel',
    required=True,
    default=True
)
@click.option(
    '--n_jobs',
    required=True,
    default=2
)
def upload(source, type, root, container_name, parallel, n_jobs):
    storage_client = BlobStorageClient()

    if type == 'txt':
        with open(source, 'r') as f:
            image_list = f.readlines()
            image_list = [x.strip() for x in image_list]
    if parallel:
        url_list = Parallel(n_jobs=n_jobs)(delayed(upload_file)(image_file, container_name, root, storage_client) for image_file in tqdm(image_list))
    else:
        url_list = [upload_file(image_file, container_name, root, storage_client) for image_file in tqdm(image_list)]

    with open('url_list.txt', 'w') as f:
        for url in url_list:
            if storage_client.is_image_url(url):
                f.write(url)
                f.write('\n')

if __name__ == '__main__':
    upload()