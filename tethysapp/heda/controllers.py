# -*- coding: utf-8 -*-
from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import TextInput, MapView, Button,DatePicker, DataTableView

from django.shortcuts import reverse

from django.shortcuts import redirect
from django.contrib import messages

from .model import add_new_data,segmentation,upload_trajectory,calculate_metrics
from .helpers import create_hydrograph,cqt_event_plot,cq_event_plot,candq_event_plot,cqt_cq_event_plot

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
    Controller for the Add Data page.
    """

    # Default Values
    site_number = '01646500'
    start_date = ''
    end_date =''
    segment_done_button_disable = True
    if event_id == 1 or event_id == '1':
        segment_button_disable= True
    else:
        segment_button_disable= False
    # Errors
    site_number_error = ''
    start_date_error = ''
    end_date_error = ''
    PKThreshold_error  =''
    fc_error = ''
    fc = ''
    PKThreshold = '' 
    ReRa = ''
    BSLOPE = ''
    ESLOPE = ''
    SC = ''
    MINDUR = ''
    dyslp = ''
    hydrograph_file_error = ''
    hydrograph_file = None
    hydrograph_plot = create_hydrograph(event_id)




    # Case where the form has been submitted
    if request.POST and 'upload-button' in request.POST:
        # Get Values
        has_errors = False
        
        # Get File
        if request.FILES and 'hydrograph-file' in request.FILES:
            # Get a list of the files
            hydrograph_file = request.FILES.getlist('hydrograph-file')
            

        if not hydrograph_file:
            has_errors = True
            hydrograph_file_error = 'Hydrograph File is Required.'

        if not has_errors:
            # Process file here
            success = upload_trajectory(hydrograph_file[0])
            print('trajectory function returned with event id as : '+str(success))
            # Provide feedback to user
            if success:
                messages.info(request, 'Successfully uploaded trajectory.')
            else:
                messages.info(request, 'Unable to upload trajectory. Please try again or check file format.')
            
            return redirect(reverse('heda:add_data', kwargs={"event_id": success}))

        messages.error(request, "Please fix errors.")


    
    if request.POST and 'segment-button' in request.POST:
        
        # Get values
        has_errors = False
        
        fc = request.POST.get('fc',None)
        PKThreshold = request.POST.get('PKThreshold',None)
        ReRa = request.POST.get('ReRa',None)
        BSLOPE = request.POST.get('BSLOPE',None)
        ESLOPE = request.POST.get('ESLOPE',None)
        SC = request.POST.get('SC',None)
        MINDUR = request.POST.get('MINDUR',None)
        dyslp = request.POST.get('dyslp',None)
        
        
        

        # Validate
        if not PKThreshold:
            has_errors = True
            PKThreshold_error = 'PKThreshold 1 is required.'
            
        if not fc:
            has_errors = True
            fc_error = 'FC required.'
            
        
        if not has_errors:
            
            status = segmentation(event_id,float(fc),float(PKThreshold),float(ReRa),float(BSLOPE),float(ESLOPE),float(SC),float(MINDUR),float(dyslp))
            
            if not status:
                messages.error(request, "Please fix parameters")
                hydrograph_plot = create_hydrograph(event_id)
                
                
            else:
                
                hydrograph_plot = create_hydrograph(event_id)
                segment_done_button_disable = False
            
            
        else:
            
            messages.error(request, "Please fix errors.")
    

    if request.POST and 'retrieve-button' in request.POST:
        # Get values
        has_errors = False
        site_number = request.POST.get('site-number', None)
        start_date = request.POST.get('start-date', None)
        end_date = request.POST.get('end-date', None)
        
        
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
            print('add new data completed')
            #hydrograph_plot =create_hydrograph(event_id)
            
            
            if not event_id:
                messages.error(request, "Unable to retrieve data please check parameters or try again later.")
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
        #attributes={'form': 'retrieve-form'},
    )
    
    
    
    
    start_date_input = DatePicker(
        name='start-date',
        display_text='Start Date',
        autoclose=True,
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        error=start_date_error,
        initial = '2019-06-04',
        #attributes={'form': 'retrieve-form'},
    )
    
    end_date_input = DatePicker(
        name='end-date',
        display_text='End Date',
        autoclose=True,
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        error=end_date_error,
        initial = '2019-06-05',
        #attributes={'form': 'retrieve-form'},
    )

    
    
    dyslp_input = TextInput(
        display_text='dyslp',
        name='dyslp',
        initial='0.001',
        placeholder='e.g.: 0.001',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    
    MINDUR_input = TextInput(
        display_text='Minimum Duration',
        name='MINDUR',
        initial='0',
        placeholder='e.g.: 0',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    
    SC_input = TextInput(
        display_text='SC',
        name='SC',
        initial='0.4',
        placeholder='e.g.: 0.4',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    ESLOPE_input = TextInput(
        display_text='ESLOPE',
        name='ESLOPE',
        initial='0.0001',
        placeholder='e.g.: 0.0001',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    
    BSLOPE_input = TextInput(
        display_text='BSLOPE',
        name='BSLOPE',
        initial='0.001',
        placeholder='e.g.: 0.001',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )
    
    ReRa_input = TextInput(
        display_text='Return Ratio',
        name='ReRa',
        initial='0.1',
        placeholder='e.g.: 0.1',
        disabled=segment_button_disable,
        #error = parameter1_error,
    )

    PKThreshold_input = TextInput(
        display_text='PKThreshold',
        name='PKThreshold',
        initial='0.03',
        placeholder='e.g.: 0.03',
        disabled=segment_button_disable,
        error = PKThreshold_error,
    )
    
    fc_input = TextInput(
        display_text='fc',
        name='fc',
        initial='0.995',
        placeholder='e.g.: 0.995',
        disabled=segment_button_disable,
        error = fc_error,
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
    
    visualize_button = Button(
        display_text='Visualize Events',
        name='visualize-button',
        icon='glyphicon glyphicon-picture',
        href=reverse('heda:visualize_events', kwargs={"event_id": event_id,"sub_event": 0}),
        disabled=segment_done_button_disable,
    )
    
    download_button = Button(
        display_text='Download',
        name='Download',
    )
    
    
    upload_button = Button(
        display_text='Upload',
        name='upload-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'upload-data-form'},
        submit=True
    )
        

    context = {
        'retrieve_button': retrieve_button,
        'cancel_button': cancel_button,
        'visualize_button':visualize_button,
        'site_number_input': site_number_input,
        'start_date_input':start_date_input,
        'end_date_input':end_date_input,
        'hydrograph_plot':hydrograph_plot,
        'segment_button':segment_button,
        'fc_input': fc_input,
        'PKThreshold_input': PKThreshold_input,
        'ReRa_input':ReRa_input,
        'BSLOPE_input':BSLOPE_input,
        'ESLOPE_input':ESLOPE_input,
        'SC_input':SC_input,
        'MINDUR_input':MINDUR_input,
        'dyslp_input':dyslp_input,
        'download_button':download_button,
        'upload_button': upload_button,
        'hydrograph_file_error': hydrograph_file_error,
        
        

    }
    

    return render(request, 'heda/add_data.html', context)
  
    
@login_required()
def visualize_events(request,event_id,sub_event):


    
    
    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('heda:home')
    )
    
    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        icon='glyphicon glyphicon-step-backward',
        href=reverse('heda:visualize_events', kwargs={"event_id": event_id,"sub_event": str(int(sub_event)-1)}),
        style='success',
    )
        
        
    download_button = Button(
        display_text='Download',
        name='Download',
    )
    
    next_button = Button(
    display_text='Next',
        name='next-button',
        icon='glyphicon glyphicon-step-forward',
        href=reverse('heda:visualize_events', kwargs={"event_id": event_id,"sub_event": str(int(sub_event)+1)}),
        style='success',
    )
    #hydrograph_plot = create_hydrograph(1)
    
    
    #cqt_plot = cqt_event_plot(int(event_id),int(sub_event))
    #cq_plot = cq_event_plot(int(event_id),int(sub_event))
    #candq_plot = candq_event_plot(int(event_id),int(sub_event))
    cqt_cq_plot = cqt_cq_event_plot(int(event_id),int(sub_event))
    
    table_rows = []
    metrics_dict = calculate_metrics(event_id,sub_event)
    
    for k in metrics_dict.keys():
        table_rows.append((k,metrics_dict[k]))
    
    
    
    if request.POST and 'previous-button' in request.POST:
        return redirect(reverse('heda:visualize_events', kwargs={"event_id": event_id,"sub_event": sub_event}))
        
        
    metric_table = DataTableView(
        column_names=('Name', 'Value'),
        rows=table_rows,
        searching=False,
        orderClasses=False,
        lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
    )

    
    context = {
        #'candq_plot':candq_plot,
        #'cqt_plot':cqt_plot,
        'cq_plot':cqt_cq_plot, 
        'cancel_button': cancel_button,
        'previous_button': previous_button,
        'download_button':download_button,
        'next_button':next_button,
        'metric_table':metric_table
        

    }
    
    
    #return redirect(reverse('heda:add_data', kwargs={"event_id": event_id}))
    return render(request, 'heda/visualize_events.html', context)
    
    
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