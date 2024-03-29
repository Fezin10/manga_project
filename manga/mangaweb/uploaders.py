import os

# generate the path to store the thumb image of some manga
def manga_thumb(instance, filename):
    manga_id = instance.id
    file_extension = os.path.splitext(filename)[1].lower()
    return f"manga/{manga_id}/thumb{file_extension}"


# generate a path to store a page of some chapter of some manga
def manga_page(instance, filename):
    manga_id = instance.chapter.manga.id
    chapter_number = instance.chapter.chapter_number
    page_number = f"{instance.page_number:03d}"
    file_extension = os.path.splitext(filename)[1].lower()

    return f"manga/{manga_id}/{chapter_number}/{page_number}{file_extension}"


def user(instance, filename):
    user_id = instance.id
    file_extension = os.path.splitext(filename)[1].lower()
    return f"user/{user_id}/icon{file_extension}"