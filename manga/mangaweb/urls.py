from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("addmanga", views.addmanga, name="addmanga"),
    path("addchapter", views.addchapter, name="addchapter"),
    path("mangapage/<int:mangaid>", views.mangapage, name="mangapage"),
    path("like/<int:manga_id>", views.like, name="mangalike"),
    path("mangas", views.mangas, name="mangas"),
    path("userpage/<int:user_id>", views.userpage, name="userpage"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("editmanga/<int:manga_id>", views.edit, name="editmanga"),
    path("edituser",views.edituser, name="edituser"),
    path("authorregister", views.authorregister, name='authorregister'),
    path("mangapage/<int:manga_id>/<int:chapter_number>", views.mangaread, name="mangaread"),
    path("chapter_visualization/<int:manga_id>/<int:chapter>", views.visualization, name="visualization"),
    path("moderator/retain_manga/<int:manga_id>", views.retain_manga, name="retain_manga"),
    path("moderator/retain_user/<int:user_id>", views.retain_user, name="retain_user"),
    path("moderator/free_user/<int:user_id>", views.free_user, name="free_user"),
    path("moderator/block_user/<int:user_id>", views.block_user, name="block_user"),
    path("moderator/free_manga/<int:manga_id>", views.free_manga, name='free_manga'),
    path("moderator/block_manga/<int:manga_id>", views.block_manga, name='block_manga'),
    path("moderator/retained", views.retained, name="retained"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)