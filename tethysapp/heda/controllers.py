# -*- coding: utf-8 -*-
from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import TextInput, MapView, Button,DatePicker

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
def add_data(request,event_id=1):
    """
    Controller for the Add Dam page.
    """

    # Default Values
    site_number = '01646500'
    start_date = ''
    end_date =''
    if event_id == 1:
        segment_button_disable= True
    else:
        segment_button_disable= False
    # Errors
    site_number_error = ''
    start_date_error = ''
    end_date_error = ''
    parameter1  =''
    parameter2 = ''
    
    hydrograph_plot = create_hydrograph(event_id)
    print('event id to add data is ' +str(event_id))
    
    if request.POST and 'segment-button' in request.POST:
        print('request started')
        # Get values
        has_errors = False
        parameter1 = request.POST.get('parameter1', None)
        parameter2 = request.POST.get('parameter2', None)
        print(parameter1)
        # Validate
        if not parameter1:
            has_errors = True
            parameter1_error = 'Parameter 1 is required.'
            print('p1 number error')
        if not parameter2:
            has_errors = True
            parameter2_error = 'Parameter 2 required.'
            print('p2 number error')
        if not has_errors:
            print('segmentation started')
            status = segmentation(event_id,parameter1, parameter2)
            print(status)
            if not status:
                messages.error(request, "Please fix parameters")
                hydrograph_plot = create_hydrograph(event_id)
                
                
            else:
                print('hydrograph plot made')
                print('event id for which plot is made '+str(event_id))
                hydrograph_plot = create_hydrograph(event_id)
                
            
            #return redirect(reverse('heda:add_data'))
        else:
            
            messages.error(request, "Please fix errors.")
    

    if request.POST and 'retrieve-button' in request.POST:
        # Get values
        print('retrieve started')
        has_errors = False
        site_number = request.POST.get('site-number', None)
        start_date = request.POST.get('start-date', None)
        end_date = request.POST.get('end-date', None)
        
        print(end_date)
        # Validate
        if not site_number:
            has_errors = True
            site_number_error = 'Site Number is required.'
            print('site number error')
        if not start_date:
            has_errors = True
            start_date_error = 'Start date is required.'
            
        if not end_date:
            has_errors = True
            end_date_error = 'End date is required.'
            

        if not has_errors:
            
            event_id = add_new_data(sites=site_number, start=start_date,end = end_date)
            #hydrograph_plot =create_hydrograph(event_id)
            
            
            if not event_id:
                messages.error(request, "Please fix input fields or try again.")
                segment_button_disable = True
                
            else:
                segment_button_disable = False
                return redirect(reverse('heda:add_data', kwargs={"event_id": event_id}))
                
            
            
            #return redirect(reverse('heda:add_data'))
        else:

            messages.error(request, "Please fix errors.")
            
            
    
    
        

    # Define form gizmos
    site_number_input = TextInput(
        display_text='Site Number',
        name='site-number',
        initial=site_number,
        placeholder='e.g.: 01646500',
        error=site_number_error,
    )
    
    start_date_input = DatePicker(
        name='start-date',
        display_text='Start Date',
        autoclose=True,
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        error=start_date_error,
        initial = '2019-06-03',
    )
    
    end_date_input = DatePicker(
        name='end-date',
        display_text='End Date',
        autoclose=True,
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        error=start_date_error,
        initial = '2019-06-09',
    )

    

    parameter1_input = TextInput(
        display_text='Parameter1',
        name='parameter1',
        initial='3',
        placeholder='e.g.: 3',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    parameter2_input = TextInput(
        display_text='Parameter2',
        name='parameter2',
        initial='3',
        placeholder='e.g.: 3',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )

    retrieve_button = Button(
        display_text='Retrieve',
        name='retrieve-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-data-form'},
        submit=True
    )
    
    
   
    segment_button = Button(
        display_text='Segment',
        name='segment-button',
        icon='glyphicon glyphicon-scissors',
        style='success',
        attributes={'form': 'segment-data-form'},
        #href=reverse('heda:add_data', kwargs={"event_id": event_id}),
        #disabled=segment_button_disable,
        submit=True
    )
    
    
    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('heda:home')
    )
    
    
        

    context = {
        'retrieve_button': retrieve_button,
        'cancel_button': cancel_button,
        'site_number_input': site_number_input,
        'start_date_input':start_date_input,
        'end_date_input':end_date_input,
        'hydrograph_plot':hydrograph_plot,
        'segment_button':segment_button,
        'parameter1_input': parameter1_input,
        'parameter2_input': parameter2_input,
        
        
        

    }
    

    return render(request, 'heda/add_data.html', context)
    
    
''' 
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
            
            #write code to download file here
            
            
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
        'event_id':event_id,

    }
    

    return render(request, 'heda/segment_data.html', context)
'''