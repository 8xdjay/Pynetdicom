from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

debug_logger()

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Identifier (query) dataset 생성
'''
ds = Dataset()
ds.PatientName = 'UNKNOWN'
ds.QueryRetrieveLevel = 'PATIENT'

'''

ds = Dataset()
ds.PatientID = '188'
ds.PatientName = '==문흥진'
ds.QueryRetrieveLevel = 'STUDY'


# Associate with the peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)
if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04X}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')