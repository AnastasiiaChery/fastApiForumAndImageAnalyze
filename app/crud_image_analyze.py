from PIL import Image, ExifTags
from fastapi import HTTPException
from starlette import status

from app import models
from app.color_list import list_color


def create_new_image(image, db):
    new_image = models.Images(**image.dict())
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image


def delete_image_data(db, image_id):
    image_query = db.query(models.Image).filter(models.Image.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_query.delete(synchronize_session=False)
    db.commit()
    return True


def image_detail_data(db, image_id):
    image_query = db.query(models.Images).filter(models.Images.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_info = Image.open(image.image)
    detail = image_info._getexif()
    detail_dict = {}
    if detail:
        for key, val in detail.items():
            if key in ExifTags.TAGS:
                detail_dict[ExifTags.TAGS[key]] = str(val)

    return detail_dict


def update_tag_data(image_id, tag, db):
    tag_data = tag.dict()
    tag_name = tag_data.get('tag_name')
    tag_data = tag_data.get('tag_data')
    try:
        new_data = int(tag_data)
    except:
        print('')
    image_query = db.query(models.Images).filter(models.Images.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_info = Image.open(image.image)
    exif = image_info.getexif()

    for k, v in ExifTags.TAGS.items():
        if v == tag_name:
            key_tag = k

    exif[key_tag] = new_data
    image_info.save(f'{image.image}', exif=exif)
    return True


def remove_tag_data(image_id, tag, db):
    tag_data = tag.dict()
    tag_name = tag_data.get('tag_name')
    image_query = db.query(models.Images).filter(models.Images.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_info = Image.open(image.image)
    exif = image_info.getexif()

    for k, v in ExifTags.TAGS.items():
        if v == tag_name:
            key_tag = k
            break

    if key_tag in exif:
        del exif[key_tag]
    image_info.save(f'{image.image}', exif=exif)

    return True


def update_color(image_id, colors, db):
    image_query = db.query(models.Images).filter(models.Images.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_info = Image.open(image.image)
    rgb = list_color.get(colors.color_code)
    gray_img = image_info.convert("RGB", (rgb))
    gray_img.save(f'{image.image}')
    return True


def update_size(image_id, sizes, db):
    image_query = db.query(models.Images).filter(models.Images.id == image_id)
    image = image_query.first()

    if image.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image with {image_id} id was not found")

    image_info = Image.open(image.image)

    (left, upper, right, lower) = (sizes.left, sizes.upper, sizes.right, sizes.lower)
    (width, height) = (sizes.width, sizes.height)

    try:
        new_image = image_info.crop((int(left), int(upper), int(right), int(lower)))
        new_image.save(f'{image.image}')
    except:
        print('ok')

    try:
        new_image = image_info.resize((int(width), int(height)))
        new_image.save(f'{image.image}')
    except:
        print('ok')

    return True
