from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_overview(request):
    return Response({"message": "Bienvenue sur l'API de Learnia"})
