import unittest
from pyramid import testing
from genius_bar.models.user import GeniusUser
from genius_bar.models.user import GeniusUserQuery
from genius_bar.models.device import GeniusDevice
from genius_bar.models.device import GeniusDeviceQuery
from genius_bar.models.event import GeniusEvent
from genius_bar.models.event import GeniusEventQuery
from sqlalchemy import DDL
import random


def _initTestingDB():
    from sqlalchemy import create_engine
    from genius_bar.models import (
        DBSession,
        Base,
        BaseQuery,
    )
    sqlalchemy_url = "mysql+pymysql://root@localhost:3306/genius_bar_test?charset=utf8"
    engine = create_engine(sqlalchemy_url)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    return DBSession


class ViewTests(unittest.TestCase):
    
    omg = 0
    test_name = ["RickRick", "CarmenC", "DavidYA", "catscats"]
    test_slack_name = ["RRRRRRick", "CCCCCCCC", "DDDDDDYA", "dogdogdog"]
    test_device = ["minimini", "iphone", "nokia3310", "iphone10", "iphoan", "poorHTO", "GodDAPI", 
                   "lulu", "lala", "fafa", "X_X", "Orz"]
    test_osvision = ["1.1.1", "2.2.2" , "3.3.3.3", "5.5.5.5"]
    test_delete = [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0]
    event_type = ["add", "delete", "lend", "return"]

    index_tstname = len(test_name)
    index_device = len(test_device)
    index_type = len(event_type)
    event_num = 30
    ricknum = 0


    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()
        # Init Database

    def test_1_add_user(self):
        for x in range(self.index_tstname):# ini user 
            input_name = self.test_name[x]
            input_id = self.test_slack_name[x]
            input_user = GeniusUser(user_name=input_name, slack_user_id=input_id)
            try:
                self.session.flush()
                self.session.add(input_user)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
        query_res = GeniusUserQuery.get_all(self.session)
        assert_result = len(query_res)
        self.assertEqual(assert_result, self.index_tstname)

    def test_2_add_device(self):
        for x in range(self.index_device): # ini device 
            self.session.flush()
            input_name = self.test_device[x]
            os_id = self.test_osvision[x % self.index_tstname]
            tmp = random.randint(0, self.index_tstname-1)
            holder_input = GeniusUserQuery.get_by_name(self.session, self.test_name[tmp])
            delete_input =  self.test_delete[x]
            input_device = GeniusDevice(device_name = input_name, os_version = os_id,
                                        holder_id = holder_input.id, delete = delete_input)
            try:
                self.session.flush()
                self.session.add(input_device)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
        query_res = GeniusDeviceQuery.get_all(self.session)
        assert_result = len(query_res)
        self.assertEqual(assert_result, self.index_device)

    def test_3_add_event(self):
        for x in range(self.event_num): 
            self.session.flush()
            input_type = self.event_type[random.randint(0, self.index_type-1)]
            tmpx = random.randint(0, self.index_device-1)
            input_device = GeniusDeviceQuery.get_by_name(self.session, self.test_device[tmpx])
            tmp = random.randint(0, self.index_tstname-1)
            input_user = GeniusUserQuery.get_by_name(self.session, self.test_name[tmp])
            input_event = GeniusEvent(event_type=input_type, device_id=input_device.id, user_id=input_user.id)
            try:
                self.session.flush()
                self.session.add(input_event)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                print(e)
        query_res = GeniusEventQuery.get_all(self.session)
        assert_result = len(query_res)
        self.assertEqual(assert_result, self.event_num)

    def test_4_user_query(self):
        # get_by_name
        pt = GeniusUserQuery.get_by_name(self.session, "RickRick")
        self.assertEqual(pt.slack_user_id, "RRRRRRick")

    def test_5_device_query(self):
        # get_by_enable_device
        pt = GeniusDeviceQuery.get_enable_device(self.session)
        assert_result = len(pt)
        self.assertEqual(assert_result, self.test_delete.count(0))

        # get_by_name
        pt_2 = GeniusDeviceQuery.get_by_name(self.session, "iphone10")
        self.assertEqual(pt_2.device_name, "iphone10")

    def test_6_event_query(self):
        # get_event without limit and type
        pt_1 = GeniusEventQuery.get_event(self.session)
        assert_result = len(list(pt_1))
        self.assertEqual(assert_result, 20)

        # get_event with limit
        pt_2 = GeniusEventQuery.get_event(self.session, None, 10)
        assert_result = len(list(pt_2))
        self.assertEqual(assert_result, 10)

        # get_event with type
        pt_3 = GeniusEventQuery.get_event(self.session, "add")
        for pt in pt_3:
            self.assertEqual(pt.event_type, "add")
            pt.event_type = "more"
            self.assertEqual(pt.event_type, "more")

    def test_7_complex_query(self):
        # get_device_by_holder_name
        pt_3 = GeniusDeviceQuery.get_device_by_holder_name(self.session, "RickRick")
        for pt in pt_3:
            self.assertEqual(pt.genius_user.user_name, "RickRick")

    def test_8_tearDown(self):
        self.session.query(GeniusDevice).delete()
        self.session.query(GeniusEvent).delete()
        self.session.query(GeniusUser).delete()
        self.session.commit()
        testing.tearDown()
        from genius_bar.models import DBSession
        DBSession.remove()
        # Clean up Database
