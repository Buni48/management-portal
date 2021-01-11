from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .controllers import HeartbeatController
from datetime import datetime
from rest_framework.decorators import api_view
from .models import Heartbeat
from licenses.models import License, UsedSoftwareProduct


def index(request: WSGIRequest) -> HttpResponse:
    return redirect('heartbeat_list')

def heartbeatList(request: WSGIRequest) -> HttpResponse:
    usedProducts = HeartbeatController.read()
    countMissing = HeartbeatController.getCountMissing(usedProducts)
    context = {
        'used_products' : usedProducts,
        'count_missing' : countMissing,
    }
    return render(request, 'heartbeat/list.html', context)


# API für den Empfang des Heartbeats
@api_view(["POST"])
def heartbeat(request):

    print(request.data)

    beat = {
        "meldung": request.data["meldung"],
        "log": request.data["log"]
    }

    # Filtern des genutztes_produkt_ID
    license = License.objects.get(key=beat["meldung"])
    kundenSoftware= UsedSoftwareProduct.objects.filter(id=1)
    datum = datetime.now()
    # print('Lizenz,Software,Datum'+license+ kundenSoftware)
    heartbeat = Heartbeat.objects.create(used_product=kundenSoftware[0], last_received=datum, message=beat["meldung"], detail=beat["log"])

    return render(request, 'Erfolgreich empfangen!')
