'''
[Modality Performed Procedure Step - aka MPPS]
MPPS는 AE가 N-CREATE, N-SET, N-EVENT-REPORT, N-GET 서비스를 통해 Modality에 의해 수행 된 절차를 기록하거나 추적할 수 있도록 한다. 
3개의 SOP 클래스를 갖는다.

- Modality Performed Procedure Step SOP Class: N-CREATE 및 N-SET와 함께 SOP 인스턴스의 속성 값을 생성하고 설정하는 데 사용
- Modality Performed Procedure Step Retrieve SOP Class: SOP 인스턴스의 속성 값을 검색하는 데 N-GET와 함께 사용
- Modality Performed Procedure Step Notification SOP Class: 피어에 procedure status를 알리기 위해 N-EVENT-REPORT와 함께 사용
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

ct_study_uid = generate_uid()
mpps_instance_uid = generate_uid()

# set attribute list
def build_attr_list():
    ds = Dataset()
    ds.ScheduledStepAttributesSequence = [Dataset()]
    step_seq = ds.ScheduledStepAttributesSequence
    step_seq[0].StudyInstanceUID = ct_study_uid
    step_seq[0].ReferencedStudySequence = []
    step_seq[0].AccessionNumber = '1'
    step_seq[0].RequestedProcedureID = "1"
    step_seq[0].RequestedProcedureDescription = 'Some procedure'
    step_seq[0].ScheduledProcedureStepID = "1"
    step_seq[0].ScheduledProcedureStepDescription = 'Some procedure step'
    step_seq[0].ScheduledProcedureProtocolCodeSequence = []
    ds.PatientName = 'Test^Test'
    ds.PatientID = '123456'
    ds.PatientBirthDate = '20000101'
    ds.PatientSex = 'O'
    ds.ReferencedPatientSequence = []
    # Performed Procedure Step Information
    ds.PerformedProcedureStepID = "1"
    ds.PerformedStationAETitle = 'SOMEAE'
    ds.PerformedStationName = 'Some station'
    ds.PerformedLocation = 'Some location'
    ds.PerformedProcedureStepStartDate = '20000101'
    ds.PerformedProcedureStepStartTime = '1200'
    ds.PerformedProcedureStepStatus = 'IN PROGRESS'
    ds.PerformedProcedureStepDescription = 'Some description'
    ds.PerformedProcedureTypeDescription = 'Some type'
    ds.PerformedProcedureCodeSequence = []
    ds.PerformedProcedureStepEndDate = None
    ds.PerformedProcedureStepEndTime = None
    # Image Acquisition Results
    ds.Modality = 'CT'
    ds.StudyID = "1"
    ds.PerformedProtocolCodeSequence = []
    ds.PerformedSeriesSequence = []

    return ds

ae = AE()
ae.add_requested_context(ModalityPerformedProcedureStepSOPClass)
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    status, attr_list = assoc.send_n_create(
        build_attr_list(),
        ModalityPerformedProcedureStepSOPClass,
        mpps_instance_uid
    )

    if status:
        print('N-CREATE request status: 0x{0:04x}'.format(status.Status))

        # request 성공 시, status는 success or warning
        category = code_to_category(status.Status)
        if category in ['Warning', 'Success']:
            print(attr_list)
    else:
        print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')


'''
MPPS SOP 인스턴스가 성공적으로 생성되면 촬영장비에서 하나 이상의 N-SET 요청을 MPPS SCP로 전송하여 SOP 인스턴스의 속성을 업데이트할 수 있다. 
절차가 완료되면 "COMPLETEED"의 (0040,0252)형식의 수정 목록이 포함된 최종 N-SET 요청이 전송된다.
'''

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
else:
    print('Association rejected, aborted or never connected')