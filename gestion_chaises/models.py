from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Chaise(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    disponible = models.BooleanField(default=True)
    prix_location_journalier = models.DecimalField(max_digits=6, decimal_places=2)
    photo = models.ImageField(upload_to='photos_chaises/', null=True, blank=True)

    def __str__(self):
        return self.nom
    
class Panier(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    def total(self):
        total = sum(article.total() for article in self.articles.all())
        return total

class ArticlePanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='articles', on_delete=models.CASCADE)
    chaise = models.ForeignKey(Chaise, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.chaise.nom}"

    def total(self):
        return self.quantite * self.chaise.prix_location_journalier

class Location(models.Model):
    chaise = models.ForeignKey(Chaise, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    prix_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.utilisateur.username} a loué {self.chaise.nom} du {self.date_debut} au {self.date_fin}"

