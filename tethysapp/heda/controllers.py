# -*- coding: utf-8 -*-
from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import TextInput, MapView, Button

from django.shortcuts import reverse

from django.shortcuts import redirect
from django.contrib import messages

from .model import add_new_data,segmentation
from .helpers import create_hydrograph

from tethys_sdk.permissions import has_permission

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
    site_number = '01646500'
    owner = ''
    hydrograph_plot = create_hydrograph(1)
    segment_button_disable= True
    # Errors
    site_number_error = ''
    owner_error = ''
    event_id = 'event_id_default'
    
    

    if request.POST and 'upload-button' in request.POST:
        # Get values
        has_errors = False
        site_number = request.POST.get('site_number', None)
        owner = request.POST.get('owner', None)

        # Validate
        if not site_number:
            has_errors = True
            site_number_error = 'Site Number is required.'
            print('yada')
        if not owner:
            has_errors = True
            owner_error = 'Owner is required.'

        if not has_errors:
            
            event_id = add_new_data(sites=site_number, start=owner,end = 'dummy',value='dummy')
            hydrograph_plot =create_hydrograph(event_id)
            
            if not event_id:
                messages.error(request, "Please fix input fields.")
                segment_button_disable = True
                
            else:
                segment_button_disable = False
                
            
            
            #return redirect(reverse('heda:add_data'))
        else:

            messages.error(request, "Please fix errors.")
            
            
   
    
        

    # Define form gizmos
    site_number_input = TextInput(
        display_text='Site Number',
        name='site_number',
        initial=site_number,
        placeholder='e.g.: 01646500'
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
    
    segment_button = Button(
        display_text='Segment',
        name='segment-button',
        icon='glyphicon glyphicon-scissors',
        #href=reverse('heda:segment_data'),
        href=reverse('heda:segment_data', kwargs={"event_id": event_id}),
        disabled=segment_button_disable,
        submit = False
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('heda:home')
    )
    
    
        

    context = {
        'upload_button': upload_button,
        'cancel_button': cancel_button,
        'site_number_input': site_number_input,
        'owner_input': owner_input,
        'hydrograph_plot':hydrograph_plot,
        'segment_button':segment_button,
        
        

    }
    

    return render(request, 'heda/add_data.html', context)
    
    
    
@login_required()
def segment_data(request,event_id):
    """
    Controller for the segment page.
    """

    #load discharge series from database
    # Default Values
    
    hydrograph_plot = create_hydrograph(event_id)
    download_button_disable = True
    parameter1 = ''
    parameter2 = ''
    
    
    # Errors
    parameter1_error = ''
    parameter2_error = ''
    
    if request.POST and 'segment-button' in request.POST:
        # Get values
        has_errors = False
        parameter1 = request.POST.get('parameter1', None)
        parameter2 = request.POST.get('parameter2', None)
        
        # Validate
        if not parameter1:
            has_errors = True
            parameter1_error = 'Parameter 1 is required.'
            
        if not parameter2:
            has_errors = True
            parameter2_error = 'Parameter 2 required.'

        if not has_errors:
            
            status = segmentation(event_id,parameter1, parameter2)
            
            if not status:
                messages.error(request, "Please fix parameters")
                download_button_disable = True
                
            else:
                
                hydrograph_plot = create_hydrograph(event_id)
                download_button_disable = False
            
            #return redirect(reverse('heda:add_data'))
        else:
            
            messages.error(request, "Please fix errors.")
    

    if request.POST and 'download-button' in request.POST:
        # Get values
        has_errors = False
        if not has_errors:
            '''
            write code to download file here
            
            '''
            download_button_disable = False
            #return redirect(reverse('heda:add_data'))
        else:

            messages.error(request, "Please fix errors.")
            download_button_disable = True
        
    
    # Define form gizmos
    parameter1_input = TextInput(
        display_text='Parameter 1',
        name='parameter1',
        initial=parameter1,
        placeholder='3'
    )
    
    
    parameter2_input = TextInput(
        display_text='Parameter 2',
        name='parameter2',
        initial=parameter2,
        placeholder='3'
    )
    
    download_button = Button(
        display_text='Download',
        name='download-button',
        icon='glyphicon glyphicon-download',
        style='success',
        disabled=download_button_disable
    )
    
    segment_button = Button(
        display_text='Segment',
        name='segment-button',
        icon='glyphicon glyphicon-scissors',
        style='success',
        attributes={'form': 'segment-data-form'},
        submit=True
    )
    

    context = {
        'download_button': download_button,        
        'hydrograph_plot':hydrograph_plot,
        'parameter1': parameter1_input,
        'parameter2': parameter2_input,
        'segment_button':segment_button,

    }
    

    return render(request, 'heda/segment_data.html', context)
