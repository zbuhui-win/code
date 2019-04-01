import apps.app2.controller as ap2_ctrl


urls = [
    '/app2/testargsget', ap2_ctrl.TestArgsGet,
    '/app2/testexception', ap2_ctrl.TestException,
    '/app2/testlog',ap2_ctrl.TestLog2,
    '/app2/testoutbound',ap2_ctrl.TestOutbound,
    '/app2/testerrorcode', ap2_ctrl.TestErrorCode,
]
