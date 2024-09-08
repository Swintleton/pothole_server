import os
from PIL import Image, ExifTags

class ImageService:
    UPLOAD_FOLDER = 'uploaded_frames'
    CONFIRMED_FOLDER = 'uploaded_frames/confirmed'

    @staticmethod
    def correct_image_orientation(image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass

    @staticmethod
    def process_image(file, filename):
        file_path = os.path.join(ImageService.UPLOAD_FOLDER, filename)
        file.save(file_path)
        with Image.open(file_path) as img:
            ImageService.correct_image_orientation(img)
            img = img.resize((416, 416))
            img.save(file_path)
        return file_path
