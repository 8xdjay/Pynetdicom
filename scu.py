# -*- coding: utf-8 -*- 

from pynetdicom import AE, debug_logger

debug_logger()

ae = AE()

'''
single presentation context를 추가합니다
모든 Association request는 적어도 하나의 presentation context를 가지고 있어야 하며, 
아래의 경우 검증 서비스 사용을 제안하는 context 추가했읍니다.
'''
ae.add_requested_context('1.2.840.10008.1.1')

# 기본 포트는 11112인데 왜인지 11112가 already use.... 는 local에 깔린 gravuty였음 -.-
assoc = ae.associate('localhost', 11112)

if assoc.is_established:
    print('Association established with Echop SCP!!!')
    
    status = assoc.send_c_echo()
    assoc.release()
    
else:
    # Association rejected, aborted or never connected
    print('Failed to associate..')


