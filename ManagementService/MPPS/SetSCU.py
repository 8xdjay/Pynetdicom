'''
MPPS SOP 인스턴스가 성공적으로 생성되면 촬영장비에서 하나 이상의 N-SET 요청을 MPPS SCP로 전송하여 SOP 인스턴스의 속성을 업데이트할 수 있다. 
절차가 완료되면 "COMPLETEED"의 (0040,0252)형식의 수정 목록이 포함된 최종 N-SET 요청이 전송된다.
'''
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import (
    ModalityPerformedProcedureStepSOPClass,
    CTImageStorage
)
from pynetdicom.status import code_to_category

debug_logger()

ct_series_uid = generate_uid()
ct_instance_uids = [generate_uid() for ii in range(10)]

# Our N-SET *수정 리스트*
def build_mod_list(series_instance, sop_instances):
    ds = Dataset()
    ds.PerformedSeriesSequence = [Dataset()]

    series_seq = ds.PerformedSeriesSequence
    series_seq[0].PerformingPhysicianName = None
    series_seq[0].ProtocolName = "Some protocol"
    series_seq[0].OperatorName = None
    series_seq[0].SeriesInstanceUID = series_instance
    series_seq[0].SeriesDescription = "some description"
    series_seq[0].RetrieveAETitle = None
    series_seq[0].ReferencedImageSequence = []

    img_seq = series_seq[0].ReferencedImageSequence
    for uid in sop_instances:
        img_ds = Dataset()
        img_ds.ReferencedSOPClassUID = CTImageStorage
        img_ds.ReferencedSOPInstanceUID = uid
        img_seq.append(img_ds)

    series_seq[0].ReferencedNonImageCompositeSOPInstanceSequence = []

    return ds

final_ds = Dataset()
final_ds.PerformedProcedureStepStatus = "COMPLETED"
final_ds.PerformedProcedureStepEndDate = "20000101"
final_ds.PerformedProcedureStepEndTime = "1300"


assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the N-SET service to update the SOP Instance
    status, attr_list = assoc.send_n_set(
        build_mod_list(ct_series_uid, ct_instance_uids),
        ModalityPerformedProcedureStepSOPClass,
        mpps_instance_uid
    )

    if status:
        print('N-SET request status: 0x{0:04x}'.format(status.Status))
        category = code_to_category(status.Status)
        if category in ['Warning', 'Success']:
            # Send completion
            status, attr_list = assoc.send_n_set(
                final_ds,
                ModalityPerformedProcedureStepSOPClass,
                mpps_instance_uid
            )
            if status:
                print('Final N-SET request status: 0x{0:04x}'.format(status.Status))
    else:
        print('Connection timed out, was aborted or received invalid response')

    assoc.release()