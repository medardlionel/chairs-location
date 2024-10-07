import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Chaise, Panier, ArticlePanier, Location
from datetime import timedelta
from django.utils import timezone
from .forms import LocationForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def liste_chaises(request):
    chaises = Chaise.objects.filter(disponible=True)
    return render(request, 'liste_chaises.html', {'chaises': chaises})

def ajouter_au_panier(request, chaise_id):
    chaise = get_object_or_404(Chaise, id=chaise_id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)

    article, created = ArticlePanier.objects.get_or_create(panier=panier, chaise=chaise)
    if not created:
        article.quantite += 1
        article.save()

    return redirect('voir_panier')

def voir_panier(request):
    panier = Panier.objects.get(utilisateur=request.user)
    articles = panier.articles.all()

    # Calculer le total pour chaque article
    articles_avec_total = []
    for article in articles:
        total_article = article.quantite * article.chaise.prix_location_journalier
        articles_avec_total.append({
            'article': article,
            'total_article': total_article
        })

    # Calculer le total du panier
    total_panier = sum(article['total_article'] for article in articles_avec_total)

    context = {
        'articles_avec_total': articles_avec_total,
        'total_panier': total_panier,
    }
    return render(request, 'voir_panier.html', context)



def passer_commande(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)

    # Vérifier si le panier contient des articles
    if panier.articles.exists():
        # Calculer le prix total pour tous les articles du panier
        prix_total = sum([article.quantite * article.chaise.prix_location_journalier for article in panier.articles.all()])

        # Convertir le prix total en centimes pour Stripe (Stripe traite les montants en centimes)
        prix_total_centimes = int(prix_total * 100)

        # Créer une session de paiement Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Location de chaises',
                        },
                        'unit_amount': prix_total_centimes,  # Montant total en centimes
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/paiement_reussi/'),
            cancel_url=request.build_absolute_uri('/paiement_annule/'),
        )

        # Rediriger vers la page de paiement Stripe
        return redirect(session.url, code=303)

    else:
        # Si le panier est vide, rediriger vers la page du panier
        return redirect('voir_panier')

def paiement_reussi(request):
    # Ici, tu peux traiter la commande en enregistrant les détails dans la base de données
    # Une fois le paiement réussi, tu vides le panier et crées les locations
    panier = Panier.objects.get(utilisateur=request.user)
    for article in panier.articles.all():
        Location.objects.create(
            utilisateur=request.user,
            chaise=article.chaise,
            date_debut=timezone.now(),
            date_fin=timezone.now() + timedelta(days=1),
            prix_total=article.quantite * article.chaise.prix_location_journalier
        )
    panier.articles.all().delete()
    
    return render(request, 'paiement_reussi.html', {'message': 'Votre paiement a été effectué avec succès.'})

def paiement_annule(request):
    return render(request, 'paiement_annule.html', {'message': 'Le paiement a été annulé.'})


def louer_chaise(request, chaise_id):
    chaise = get_object_or_404(Chaise, id=chaise_id)
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.utilisateur = request.user
            location.prix_total = (location.date_fin - location.date_debut).days * chaise.prix_location_journalier
            chaise.disponible = False
            chaise.save()
            location.save()
            return redirect('historique_locations')
    else:
        form = LocationForm()
    return render(request, 'louer_chaise.html', {'form': form, 'chaise': chaise})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def modifier_quantite(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id, panier__utilisateur=request.user)

    if request.method == 'POST':
        nouvelle_quantite = int(request.POST.get('quantite', 1))

        if nouvelle_quantite > 0:
            article.quantite = nouvelle_quantite
            article.save()

    return redirect('voir_panier')

def supprimer_article(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id, panier__utilisateur=request.user)
    article.delete()
    return redirect('voir_panier')  # Redirige vers la page du panier après suppression