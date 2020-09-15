from pydicom.dataset import Dataset

from pynetdicom import AE, evt, StoragePresentationContexts, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

debug_logger()

def handle_store(event):
    """Handle a C-STORE service request"""
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)
ae.supported_contexts = StoragePresentationContexts

# Start our Storage SCP in non-blocking mode, listening on port 11120
ae.ae_title = b'OUR_STORE_SCP'
scp = ae.start_server(('', 11120), block=False, evt_handlers=handlers)

# Create out identifier (query) dataset
ds = Dataset()
ds.PatientID = '188'
ds.PatientName = '==문흥진'
ds.QueryRetrieveLevel = 'STUDY'


# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-MOVE service to send the identifier
    responses = assoc.send_c_move(ds, b'OUR_STORE_SCP', PatientRootQueryRetrieveInformationModelMove)

    for (status, identifier) in responses:
        if status:
            print('C-MOVE query status: 0x{0:04x}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

# Stop our Storage SCP
scp.shutdown()