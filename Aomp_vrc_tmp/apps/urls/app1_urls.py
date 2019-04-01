import apps.app1.controller as ap1_ctrl


urls = [
    '/app1/testobject', ap1_ctrl.TestObject,
    '/app1/testlog', ap1_ctrl.TestLog,
    '/app1/testxml2dict',ap1_ctrl.TestXml2Dict,
    '/app1/testdb',ap1_ctrl.TestDb,
]
