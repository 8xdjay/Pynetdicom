from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import (
    DisplaySystemSOPClass, DisplaySystemSOPInstance
)
from pynetdicom.status import code_to_category

debug_logger()

ae = AE()

ae.add_requested_context(DisplaySystemSOPClass)

assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # [N-GET] : Printer SOP Class의 instance를 retrieve할 때 사용.    
    # attr_list는 속성 값을 포함하는 pydicom Dataset
    status, attr_list = assoc.send_n_get(
        [(0x0008, 0x0070)],
        DisplaySystemSOPClass,
        DisplaySystemSOPInstance
    )

    if status :
        print('N-GET request status: 0x{0:04x}'.format(status.Status))

        # request 성공 시, status는 success or warning
        category = code_to_category(status.Status)
        if category in ['Warning', 'Success'] :
            print(attr_list)
    else:
        print('Connection timed out, was aborted or received invalid respone')
    
    assoc.release()

else:
    print('Association rejected, aborted or never connected')