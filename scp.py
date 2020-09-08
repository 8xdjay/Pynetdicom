# -*- coding: utf-8 -*- 
import os

from pydicom.filewriter import write_file_meta_info

from pydicom.uid import ExplicitVRLittleEndian

from pynetdicom import (AE, debug_logger, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES)
from pynetdicom.sop_class import CTImageStorage

debug_logger()

'''
[Event handler]
pynetdicom은 AE간에 교환된 데이터에 대한 액세르를 제공하고 서비스 요청에 대한 응답을 사용자 정의 하는 방법으로 이벤트핸들러 시스템을 사용

1. notification event: 사용자에게 일부 이벤트가 발생한 알림 이벤트
2. intervention event: 사용자가 어떤 방식으로든 개입해야 하는 개입 이벤트

함수 형태의 handler를 이벤트에 바인딩하여, 이벤트 발생 시 해당 handler를 호출하는 형태
'''

def handle_store(event, storage_dir) :
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except:
        return 0xC001

    fname = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID+'.dcm')

    with open(fname, 'wb') as f :
         # preamble, prefix and file meta information elements
         f.write(b'\x00' * 128)
         f.write(b'DICM')
         write_file_meta_info(f, event.file_meta)

         f.write(event.request.DataSet.getvalue())


    '''
    ds = event.dataset
    ds.file_meta = event.file_meta
    ds.save_as(ds.SOPInstanceUID, write_like_original=False)
    '''
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store, ['out'])]

ae = AE()
# ae.add_supported_context(CTImageStorage, ExplicitVRLittleEndian)

'''
AllStoragePresentationContexts는 스토리지 서비스의 모든 SOP 클래스에 대해 하나씩 사전 구축 된 Presentation Context의 목록
기본적으로 압축되지 않은 Transfer Context만 지원하기 때문에 ALL_TRNS_SYNTAXES와 함께 사용
'''
storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]

for uid in storage_sop_classes:
    ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

ae.start_server(('', 11112), block=True, evt_handlers=handlers)