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
    path("mangaread/<int:manga_id>/<int:chapter>", views.mangaread, name="mangaread"),
    path("mangas", views.mangas, name="mangas"),
    path("userpage/<int:user_id>", views.userpage, name="userpage"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("editmanga/<int:manga_id>", views.edit, name="editmanga"),
    path("edituser",views.edituser, name="edituser")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)