from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("manga/", views.mangas, name="mangas"),    
    path("manga/add", views.addmanga, name="addmanga"),
    path("manga/chapter/add", views.addchapter, name="addchapter"),
    path("manga/chapter/delete/<int:manga_id>/<int:chapter>", views.chapter_delete, name="chapter_delete"),
    path("manga/delete/<int:manga_id>", views.deletemanga, name="deletemanga"),
    path("manga/edit/<int:manga_id>", views.edit, name="editmanga"),
    path("manga/like/<int:manga_id>", views.like, name="mangalike"),
    path("manga/page/<int:manga_id>", views.mangapage, name="mangapage"),
    path("manga/read/<int:manga_id>/<int:chapter_number>", views.mangaread, name="mangaread"),
    path("manga/view/<int:manga_id>/<int:chapter>", views.visualization, name="visualization"),
    path("moderator/block/manga/<int:manga_id>", views.block_manga, name='block_manga'),
    path("moderator/block/user/<int:user_id>", views.block_user, name="block_user"),
    path("moderator/free/manga/<int:manga_id>", views.free_manga, name='free_manga'),
    path("moderator/free/user/<int:user_id>", views.free_user, name="free_user"),
    path("moderator/retain/manga/<int:manga_id>", views.retain_manga, name="retain_manga"),
    path("moderator/retain/user/<int:user_id>", views.retain_user, name="retain_user"),
    path("moderator/retained", views.retained, name="retained"),
    path("register", views.register_view, name="register"),
    path("user/author", views.authorregister, name="authorregister"),
    path("user/edit", views.edituser, name="edituser"),
    path("user/follow/<int:user_id>", views.follow, name="follow"),
    path("user/page/<int:user_id>", views.userpage, name="userpage")    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)