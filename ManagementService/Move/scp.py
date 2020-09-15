import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

def handle_move(event):
    ds = event.identifier

    if 'QueryRetrieveLevel' in ds:
        # fail
        yield 0xC000, None
        return

    # known_aet_dict = get_known_aet()

    try:
        # (addr, port) = known_aet_dict[event.move_destination]
        addr = '127.0.0.1'
        port = 11120

    except KeyError:
        # unknown destitation AE
        yield (None, None)
        return

    yield (addr, port)

    instances = []
    matching = []
    fdir = './sample'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))

    if ds.QueryRetrieveLevel == 'STUDY':
        if 'PatientID' in ds:
            matching = [
                inst for inst in instances if inst.PatientID == ds.PatientID
            ]

    yield len(matching)

    # Yield the matching instances
    for instance in matching:
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return

        # Pending
        yield (0xFF00, instance)

handlers = [(evt.EVT_C_MOVE, handle_move)]

ae = AE()
ae.requested_contexts = StoragePresentationContexts
ae.add_supported_context(PatientRootQueryRetrieveInformationModelMove)
ae.start_server(('', 11112), evt_handlers=handlers)
