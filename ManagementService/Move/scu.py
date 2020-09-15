from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

debug_logger()

ae = AE()

ae.add_requested_conatext(PatientRootQueryRetrieveInformationModelMove)

ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'
ds.PatientID = '1233'
ds.StudyInstanceUID = '1.2.3'
ds.SeriesInstanceUID = '1.2.3.4'

assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    res = assoc.send_e_mov(ds, b'STORE_SCP', PatientRootQueryRetrieveInformationModelMove)

    for (status, identifier) in res:
        if status:
            print('C-MOVE query status: 0x{0:04x}'.format(status.Status))
        else: 
            print('Connection timed out, was aborted or received invalid response')

    assoc.release()
else:
    print('Association 실패')