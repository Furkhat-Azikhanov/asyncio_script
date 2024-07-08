import asyncio
import aiohttp
import hashlib
import os
import tempfile
from pathlib import Path
import shutil

BASE_URL = "https://gitea.radium.group/api/v1"
REPO_PATH = "radium/project-configuration"
HEAD_URL = f"{BASE_URL}/repos/{REPO_PATH}/archive/master.zip"

async def download_file(session: aiohttp.ClientSession, url: str, dest: Path):
    async with session.get(url) as response:
        response.raise_for_status()
        dest.write_bytes(await response.read())

async def download_head(dest: Path):
    async with aiohttp.ClientSession() as session:
        await download_file(session, HEAD_URL, dest)

async def calculate_hashes(directory: Path):
    hashes = {}
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            hashes[file_path.name] = file_hash
    return hashes

async def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        zip_file_path = temp_dir_path / "HEAD.zip"
        
        # Download the zip file
        await download_head(zip_file_path)
        
        # Extract the zip file
        await asyncio.to_thread(shutil.unpack_archive, zip_file_path, temp_dir_path)
        
        # Calculate hashes
        hashes = await calculate_hashes(temp_dir_path)
        
        for file_name, file_hash in hashes.items():
            print(f"{file_name}: {file_hash}")

if __name__ == "__main__":
    asyncio.run(main())
