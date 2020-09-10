from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import ModalityPerformedProcedureStepSOPClass

managed_instances = {}

# EVT_N_CREATE handler
def handle_create(event):
    # MPPS' N-CREATE request는 반드시 Affected SOP Instance UID를 포함해야 함
    req = event.request
    if req.AffectedSOPInstanceUID is None:
        # Failed - invalid attribute value
        return 0x0106, None

    # 중복된 SOP Instance 생성 불가능
    if req.AffectedSOPInstanceUID in managed_instances:
        # Failed - duplicate SOP Instance
        return 0x0111, None

    # N-CREATE request의 Attribute List dataset
    attr_list = event.attribute_list

    # Performed Procedure Step Status는 'IN PROGRESS' 이어야 함
    if "PerformedProcedureStepStatus" not in attr_list:
        # Failed - missing attribute
        return 0x0120, None
    if attr_list.PerformedProcedureStepStatus.upper() != 'IN PROGRESS':
        return 0x0106, None

    # Skip other tests...

    # Modality Performed Procedure Step SOP Class Instance 생성
    # DICOM Standard, Part 3, Annex B.17
    ds = Dataset()

    # Add the SOP Common module elements (Annex C.12.1)
    ds.SOPClassUID = ModalityPerformedProcedureStepSOPClass
    ds.SOPInstanceUID = req.AffectedSOPInstanceUID

    # Update with the requested attributes
    ds.update(attr_list)

    # Add the dataset to the managed SOP Instances
    managed_instances[ds.SOPInstanceUID] = ds

    # Return status, dataset
    return 0x0000, ds

# EVT_N_SET handler
def handle_set(event):
    req = event.request
    if req.RequestedSOPInstanceUID not in managed_instances:
        # Failure - SOP Instance not recognised
        return 0x0112, None

    ds = managed_instances[req.RequestedSOPInstanceUID]

    # N-SET request의 Modification List dataset
    mod_list = event.attribute_list

    # Skip other tests...

    ds.update(mod_list)

    # Return status, dataset
    return 0x0000, ds

handlers = [(evt.EVT_N_CREATE, handle_create), (evt.EVT_N_SET, handle_set)]

ae = AE()
ae.add_supported_context(ModalityPerformedProcedureStepSOPClass)
ae.start_server(('', 11112), evt_handlers=handlers)