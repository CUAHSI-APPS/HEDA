from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import TextInput, MapView, Button

from django.shortcuts import reverse

from django.shortcuts import redirect
from django.contrib import messages

from .model import add_new_data


@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    dam_inventory_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        basemap='OpenStreetMap',
    )

    visualize = Button(
        display_text='Visualize',
        name='add-dam-button',
        icon='glyphicon glyphicon-plus',
        style='success'
    )

    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Next'
        }
    )

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button,
        'dam_inventory_map': dam_inventory_map,
        'visualize': visualize,
    }

    return render(request, 'heda/home.html', context)


@login_required()
def add_data(request):
    """
    Controller for the Add Dam page.
    """

    # Default Values
    site_name = ''
    owner = ''

    # Errors
    site_name_error = ''
    owner_error = ''

    if request.POST and 'upload-button' in request.POST:
        # Get values
        has_errors = False
        site_name = request.POST.get('site_name', None)
        owner = request.POST.get('owner', None)

        # Validate
        if not site_name:
            has_errors = True
            site_name_error = 'Site Name is required.'

        if not owner:
            has_errors = True
            owner_error = 'Owner is required.'

        if not has_errors:
            
            add_new_data(site_name=site_name, owner=owner)
            return redirect(reverse('heda:home'))

        messages.error(request, "Please fix errors.")

    # Define form gizmos
    site_name_input = TextInput(
        display_text='Site Name',
        name='site_name',
        initial=site_name,
        placeholder='e.g.: Mad River'
    )

    owner_input = TextInput(
        display_text='Owner Name',
        name='owner',
        initial=owner,
        placeholder='e.g.: Ali Javed'
    )

    upload_button = Button(
        display_text='Upload',
        name='upload-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-data-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('heda:home')
    )

    context = {
        'upload_button': upload_button,
        'cancel_button': cancel_button,
        'site_name_input': site_name_input,
        'owner_input': owner_input,

    }

    return render(request, 'heda/add_data.html', context)
