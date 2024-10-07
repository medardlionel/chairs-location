"""location_chaises URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gestion_chaises import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.liste_chaises, name='liste_chaises'),
    path('ajouter_au_panier/<int:chaise_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('voir_panier/', views.voir_panier, name='voir_panier'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('passer_commande/', views.passer_commande, name='passer_commande'),
    path('paiement_reussi/', views.paiement_reussi, name='paiement_reussi'),
    path('paiement_annule/', views.paiement_annule, name='paiement_annule'),
    path('modifier_quantite/<int:article_id>/', views.modifier_quantite, name='modifier_quantite'),
    path('supprimer_article/<int:article_id>/', views.supprimer_article, name='supprimer_article'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
