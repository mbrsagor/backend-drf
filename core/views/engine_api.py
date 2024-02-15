from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from django_filters.views import FilterView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin

from engine.models import *
from engine.forms import engine_form
from engine.forms import fuel_form


# Create new engine
@login_required
def create_engine_view(request):
    template_name = 'engine/create_engine.html'

    # Engine main form
    if request.method == 'POST' and 'engine_form' in request.POST:
        form = engine_form.EngineGalleryModelForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid():
            engine = form.save(commit=False)
            engine.save()
            if files:
                for f in files:
                    EngineGallery.objects.create(engine=engine, image=f)
                messages.add_message(request, messages.INFO, "The engine has been created.")
                return redirect('create_engine')
            else:
                messages.add_message(request, messages.ERROR, 'There was an error')
    else:
        form = engine_form.EngineGalleryModelForm()
    # Fuel form
    if request.method == 'POST' and 'fuel_add_form' in request.POST:
        fuel_add_form = fuel_form.FuelModelForm(request.POST)
        if fuel_add_form.is_valid():
            instance = fuel_add_form.save(commit=False)
            instance.save()
            messages.add_message(request, messages.INFO, 'Fuel added.')
            return redirect('create_engine')
    else:
        fuel_add_form = fuel_form.FuelModelForm()

    manufacturers = Manufacturer.objects.filter(is_active=True)
    engine_types = EngineType.objects.all()
    models = Model.objects.filter(is_active=True)
    governors = GovernorType.objects.all()
    cleaner_types = CleanerType.objects.all()
    categories = Category.objects.all()
    consumptions = Consumption.objects.all()
    dimensions = Dimension.objects.all()
    fuels = Fuel.objects.all()
    context = {
        'form': form,
        'fuels': fuels,
        'models': models,
        'manufacturers': manufacturers,
        'governors': governors,
        'categories': categories,
        'cleaner_types': cleaner_types,
        'fuel_add_form': fuel_add_form,
        'engine_types': engine_types,
        'dimensions': dimensions,
        'consumptions': consumptions
    }
    return render(request, template_name, context)


