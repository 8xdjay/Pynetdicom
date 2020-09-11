 
import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

# Implement the handler for evt.EVT_C_FIND
def handle_find(event):
    
    """Handle a C-FIND request event."""
    ds = event.identifier
     # Import stored SOP Instances
    instances = []
    fdir = './sample'

    for fpath in os.listdir(fdir):

        '''
        print(fpath)
        print('==========')
        print(ds)
        '''

        instances.append(dcmread(os.path.join(fdir, fpath)))

        if 'QueryRetrieveLevel' not in ds :
            # Failure
            yield 0xC000, None
            return

    print('Instances length: ', len(instances))
    # if ds.QueryRetrieveLevel == 'PATIENT':
    if ds.QueryRetrieveLevel == 'STUDY':
        print(ds.PatientID)
        if 'PatientID' in ds:
            if ds.PatientID not in ['*', '', '?']:
                matching = [
                    inst for inst in instances if inst.PatientID == ds.PatientID
                ]
                '''    
                matching =[]
                for inst in instances:
                    # print(ds.PatientName)
                    # print(inst.PatientName)
                    if inst.PatientID == ds.PatientID :
                        matching.append(inst)
                '''
    for instance in matching :
     
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return
        identifier = Dataset()
        identifier.PatientName = instance.PatientName
        identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

        print(identifier)

        '''
        (0008, 0052) Query/Retrieve Level                CS: 'STUDY'
        (0010, 0010) Patient's Name                      PN: '==문흥진'
        '''
         
        # Pending
        yield (0xFF00, identifier)

handlers = [(evt.EVT_C_FIND, handle_find)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)