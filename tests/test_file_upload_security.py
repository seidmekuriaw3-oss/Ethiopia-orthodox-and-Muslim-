from io import BytesIO

from PIL import Image

from utils.file_handler import validate_image_content


def test_image_upload_requires_valid_image_content():
    fake_image = BytesIO(b'not an image')
    fake_image.filename = 'fake.jpg'
    assert validate_image_content(fake_image) is False

    valid_image = BytesIO()
    Image.new('RGB', (1, 1), 'white').save(valid_image, format='JPEG')
    valid_image.filename = 'real.jpg'
    assert validate_image_content(valid_image) is True