import io
import json
import os
from pathlib import Path
import tempfile
import zipfile
import shutil
from hashlib import sha1
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes, serialization


def _sign_pass(folder: Path, p12_data: bytes, password: bytes | None = None) -> bytes:
    key, cert, _ = pkcs12.load_key_and_certificates(p12_data, password)
    if key is None or cert is None or not isinstance(key, pkcs7.PKCS7PrivateKeyTypes):
        raise ValueError("Invalid PKCS#12 data or password.")

    # Find all files in the pass folder
    files = list(folder.rglob('*'))

    manifest = {}

    # Sign each file
    for file in files:
        if file.is_file():
            manifest['/'.join(file.relative_to(folder).parts)] = sha1(
                file.read_bytes()
            ).hexdigest()

    # Create the manifest.json file
    manifest_path = folder / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=4)

    # Create the signature file
    signed_data = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(manifest_path.read_bytes())
        .add_signer(cert, key, hashes.SHA256())
        .sign(
            serialization.Encoding.DER,
            [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.Binary],
        )
    )
    signature_path = folder / 'signature'
    with open(signature_path, 'wb') as f:
        f.write(signed_data)

    # Create zip data
    files.append(manifest_path)
    files.append(signature_path)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            if file.is_file():
                zip_file.write(file, file.relative_to(folder))
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    return zip_data


def sign_pass(folder: Path, p12_data: bytes, password: bytes | None = None):
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copytree(folder, tmpdir, dirs_exist_ok=True)
        tmp_path = Path(tmpdir)
        return _sign_pass(tmp_path, p12_data, password)


if __name__ == '__main__':
    p12_data = (Path(__file__).parent / 'pass.p12').read_bytes()

    pass_folder = Path(__file__).parent / 'Generic.pass'

    signed_pass_data = sign_pass(pass_folder, p12_data)

    with open('signed_pass.pkpass', 'wb') as f:
        f.write(signed_pass_data)
