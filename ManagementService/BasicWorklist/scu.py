from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import ModalityWorklistInformationFind

debug_logger()

# Initialise the Application Entity
ae = AE()

# Request의 presentation context
'''
worklist 메커니즘에 의해 전달되는 정보의 일부는 Imaging modality 자체에 의해 사용되도록 되어있지만,
대부분의 정보는 촬영장비 운영자에게 제공되도록 되어 있음
http://dicom.nema.org/medical/dicom/2014c/output/chtml/part04/sect_K.6.html
'''
ae.add_requested_context(ModalityWorklistInformationFind)

# Create our Identifier (query) dataset
ds = Dataset()
ds.PatientName = '*'
ds.ScheduledProcedureStepSequence = [Dataset()]
item = ds.ScheduledProcedureStepSequence[0]
item.ScheduledStationAETitle = 'CTSCANNER'
item.ScheduledProcedureStepStartDate = '20181005'
item.Modality = 'CT'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # C-FIND Sevice 사용
    responses = assoc.send_c_find(ds, ModalityWorklistInformationFind)
    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04x}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')