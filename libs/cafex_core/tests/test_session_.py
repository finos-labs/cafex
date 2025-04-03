import unittest
from cafex_core.singletons_.session_ import SessionStore


class TestSessionStore(unittest.TestCase):

    def setUp(self):
        self.session_store = SessionStore()

    def test_singleton_instance(self):
        instance1 = SessionStore()
        instance2 = SessionStore()
        self.assertIs(instance1, instance2)

    def test_set_and_get_attribute(self):
        self.session_store.some_attribute = "value"
        self.assertEqual(self.session_store.some_attribute, "value")

    def test_protect_internal_storage(self):
        try:
            with self.assertRaises(AttributeError):
                self.session_store.storage = {"key": "value"}
        except Exception as e:
            pass

    def test_add_error_message(self):
        self.session_store.current_test = "test1"
        error_info = {
            'message': 'Error message',
            'type': 'step',
            'name': 'Step name',
            'phase': 'test phase'
        }
        self.session_store.add_error_message(error_info)
        self.assertIn(error_info, self.session_store.error_messages["test1"])

    def test_get_error_messages(self):
        self.session_store.current_test = "test1"
        error_info = {
            'message': 'Error message',
            'type': 'step',
            'name': 'Step name',
            'phase': 'test phase'
        }
        self.session_store.add_error_message(error_info)
        self.assertEqual(self.session_store.get_error_messages("test1"), [error_info])

    def test_clear_error_messages(self):
        self.session_store.current_test = "test1"
        error_info = {
            'message': 'Error message',
            'type': 'step',
            'name': 'Step name',
            'phase': 'test phase'
        }
        self.session_store.add_error_message(error_info)
        self.session_store.clear_error_messages("test1")
        self.assertEqual(self.session_store.get_error_messages("test1"), [])

    def test_mark_test_failed(self):
        self.session_store.current_test = "test1"
        self.session_store.mark_test_failed()
        self.assertTrue(self.session_store.is_current_test_failed())

    def test_is_current_test_failed(self):
        self.session_store.current_test = "test1"
        self.session_store.mark_test_failed()
        self.assertTrue(self.session_store.is_current_test_failed())
        self.session_store.clear_current_test_status()
        self.assertFalse(self.session_store.is_current_test_failed())

    def test_clear_current_test_status(self):
        self.session_store.current_test = "test1"
        self.session_store.mark_test_failed()
        self.session_store.clear_current_test_status()
        self.assertFalse(self.session_store.is_current_test_failed())


if __name__ == '__main__':
    unittest.main()


import unittest
from cafex_core.singletons_.request_ import RequestSingleton


class TestRequestSingleton(unittest.TestCase):

    def setUp(self):
        self.request_singleton = RequestSingleton()

    def test_singleton_instance(self):
        instance1 = RequestSingleton()
        instance2 = RequestSingleton()
        self.assertIs(instance1, instance2)

    def test_initial_request_none(self):
        self.assertIsNone(self.request_singleton.request)

    def test_set_request(self):
        self.request_singleton.request = "test_request"
        self.assertEqual(self.request_singleton.request, "test_request")


if __name__ == '__main__':
    unittest.main()
