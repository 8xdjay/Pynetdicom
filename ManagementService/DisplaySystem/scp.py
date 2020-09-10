from pynetdicom import AE, evt
from pynetdicom.sop_class import DisplaySystemSOPClass

from my_code import create_attribute_list

def handle_get(event):
    # handle N-GET request event
    attr = event.request.AttributeIdentifierList
    
    # 필요한 속성 목록 데이터 집합을 생성하는 사용자 정의 함수
    # 현재 예제에서는 없음
    # pydicom Dataset을 반환하는 척 함
    dataset = create_attribute_list(attr)
    
    return 0x0000, dataset

handlers = [(evt.EVT_N_GET, handle_get)]

ae = AE()

ae.add_supported_context(DisplaySystemSOPClass)

ae.start_server(('', 11112), evt_handlers=handlers)