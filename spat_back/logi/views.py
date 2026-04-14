from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Materiau, Mouvement
from .serializers import MateriauSerializer, MouvementSerializer
from decouple import config
from groq import Groq
import json

# ── Catégories connues pour la classification automatique ─────────────────────
CATEGORIES = ["Maçonnerie", "Couverture", "Électricité", "Plomberie",
              "Menuiserie", "Revêtement", "Finition", "Autre"]

# ── Prompt système ────────────────────────────────────────────────────────────
def build_system_prompt():
    materiaux = Materiau.objects.all()
    stock_lines = "\n".join([
        f"- {m.nom} ({m.categorie}) : stock={m.stock} {m.unite}, seuil={m.seuil}, prix={m.prix} Ar"
        for m in materiaux
    ])
    alertes = [m.nom for m in materiaux if m.stock <= m.seuil]

    return f"""Tu es Logi, l'assistant IA logistique intégré à SPAT.

Tu gères les matériaux de construction d'un parc immobilier à Madagascar.

STOCK ACTUEL :
{stock_lines if stock_lines else "Aucun matériau enregistré."}

ALERTES STOCK BAS : {", ".join(alertes) if alertes else "Aucune"}

CATÉGORIES DISPONIBLES : {", ".join(CATEGORIES)}

Tu réponds UNIQUEMENT en JSON valide, sans markdown, sans explication.

FORMAT DE RÉPONSE :
{{
  "texte": "ta réponse courte en français",
  "action": null,
  "confirmation": false
}}

ACTIONS POSSIBLES :

1. Mouvement sur matériau EXISTANT :
{{
  "texte": "...",
  "action": {{
    "type": "mouvement",
    "data": {{
      "materiau": "nom exact",
      "typeOp": "Entrée" ou "Sortie",
      "quantite": 50,
      "logement": "LOG-001",
      "fournisseur": "nom ou Non précisé"
    }}
  }},
  "confirmation": true
}}

2. Matériau INCONNU — crée-le automatiquement puis enregistre :
{{
  "texte": "...",
  "action": {{
    "type": "nouveau_materiau",
    "data": {{
      "nom": "Parpaing",
      "categorie": "Maçonnerie",
      "unite": "unités",
      "prix": 2500,
      "seuil": 50,
      "typeOp": "Entrée",
      "quantite": 50,
      "logement": "LOG-001",
      "fournisseur": "Non précisé"
    }}
  }},
  "confirmation": true
}}

3. Afficher le stock :
{{"texte": "...", "action": {{"type": "stock"}}, "confirmation": false}}

4. Afficher les alertes :
{{"texte": "...", "action": {{"type": "alertes"}}, "confirmation": false}}

RÈGLES IMPORTANTES :
- Si le matériau n'existe pas dans le stock actuel, utilise "nouveau_materiau"
- Choisis la catégorie la plus logique parmi les catégories disponibles
- Estime le prix unitaire en Ariary si non précisé
- Demande toujours confirmation avant d'exécuter (confirmation: true)
- Si l'utilisateur dit "oui", "ok", "confirme", "valide" : exécute avec confirmation: false
- Si l'utilisateur annule : action null
"""


@api_view(['GET'])
def stock(request):
    materiaux = Materiau.objects.all()
    return Response(MateriauSerializer(materiaux, many=True).data)


@api_view(['GET'])
def alertes(request):
    bas = [m for m in Materiau.objects.all() if m.stock <= m.seuil]
    return Response(MateriauSerializer(bas, many=True).data)


@api_view(['POST'])
def mouvement(request):
    nom      = request.data.get('materiau', '').strip()
    type_op  = request.data.get('type', '').strip()
    quantite = request.data.get('quantite', 0)
    logement = request.data.get('logement', '')
    fourn    = request.data.get('fournisseur', '')

    if not nom:
        return Response({'error': 'Le champ "materiau" est requis.'}, status=400)
    if type_op not in ['Entrée', 'Sortie']:
        return Response({'error': 'Le type doit être "Entrée" ou "Sortie".'}, status=400)
    try:
        quantite = int(quantite)
        if quantite <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return Response({'error': 'La quantité doit être un entier positif.'}, status=400)

    try:
        mat = Materiau.objects.get(nom__iexact=nom)
    except Materiau.DoesNotExist:
        noms = list(Materiau.objects.values_list('nom', flat=True))
        return Response({'error': f'Matériau "{nom}" introuvable.', 'disponibles': noms}, status=404)

    if type_op == 'Sortie' and mat.stock < quantite:
        return Response({'error': f'Stock insuffisant. Stock actuel : {mat.stock} {mat.unite}.'}, status=400)

    mvt = Mouvement.objects.create(
        materiau=mat, type=type_op, quantite=quantite,
        logement=logement, fournisseur=fourn if type_op == 'Entrée' else None,
    )
    mat.refresh_from_db()
    return Response({'mouvement': MouvementSerializer(mvt).data, 'stock_mis_a_jour': MateriauSerializer(mat).data}, status=201)


@api_view(['POST'])
def creer_et_mouvement(request):
    """Crée un nouveau matériau automatiquement puis enregistre un mouvement."""
    data      = request.data
    nom       = data.get('nom', '').strip()
    categorie = data.get('categorie', 'Autre')
    unite     = data.get('unite', 'unités')
    prix      = int(data.get('prix', 0))
    seuil     = int(data.get('seuil', 10))
    type_op   = data.get('typeOp', 'Entrée')
    quantite  = int(data.get('quantite', 0))
    logement  = data.get('logement', 'LOG-001')
    fourn     = data.get('fournisseur', 'Non précisé')

    if not nom:
        return Response({'error': 'Nom du matériau requis.'}, status=400)

    mat, created = Materiau.objects.get_or_create(
        nom__iexact=nom,
        defaults={'nom': nom, 'categorie': categorie, 'unite': unite, 'prix': prix, 'seuil': seuil, 'stock': 0}
    )

    mvt = Mouvement.objects.create(
        materiau=mat, type=type_op, quantite=quantite,
        logement=logement, fournisseur=fourn if type_op == 'Entrée' else None,
    )
    mat.refresh_from_db()

    return Response({
        'cree': created,
        'materiau': MateriauSerializer(mat).data,
        'mouvement': MouvementSerializer(mvt).data,
        'stock_mis_a_jour': MateriauSerializer(mat).data,
    }, status=201)


@api_view(['GET'])
def mouvements_liste(request):
    mvts = Mouvement.objects.select_related('materiau').all()[:50]
    return Response(MouvementSerializer(mvts, many=True).data)


@api_view(['POST'])
def logi_chat(request):
    try:
        messages = request.data.get('messages', [])
        if not messages:
            return Response({'error': 'Aucun message reçu.'}, status=400)

        client = Groq(api_key=config('GROQ_API_KEY'))

        groq_messages = [{"role": "system", "content": build_system_prompt()}]
        for msg in messages:
            groq_messages.append({"role": msg["role"], "content": msg["content"]})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            max_tokens=1000,
            temperature=0.2,
        )

        raw = completion.choices[0].message.content.strip()

        # Nettoie si Groq ajoute des backticks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return Response({"content": raw})

    except Exception as e:
        import traceback
        return Response({"error": str(e), "detail": traceback.format_exc()}, status=500)
