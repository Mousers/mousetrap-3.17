from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import unittest
from unittest.mock import Mock

from ..bus import Bus, Event


class test_Event(unittest.TestCase):

    def test_name(self):
        event = Event('event_name')
        self.assertEqual('event_name', event.name)

    def test_dict_data(self):
        event = Event('event_name', {'x':3})
        self.assertEqual('event_name', event.name)
        self.assertEqual(3, event['x'])

    def test_keyword_data(self):
        event = Event('event_name', x=3)
        self.assertEqual('event_name', event.name)
        self.assertEqual(3, event['x'])

    def test_data_keyword_data(self):
        event = Event('event_name', data=3)
        self.assertEqual('event_name', event.name)
        self.assertEqual(3, event['data'])

    def test_dict_keyword_data(self):
        event = Event('event_name', {'x':3}, data=4)
        self.assertEqual('event_name', event.name)
        self.assertEqual(3, event['x'])
        self.assertEqual(4, event['data'])

    def test_dict_keyward_data_override(self):
        event = Event('event_name', {'x':3}, x=4)
        self.assertEqual('event_name', event.name)
        self.assertEqual(4, event['x'])


class test_Bus(unittest.TestCase):

    def setUp(self):
        self.bus = Bus()

    def test_call_fire(self):
        def foo(event):
            self.assertEqual('event_name', event.name)
        self.bus.call(foo, on='event_name')
        self.bus.fire('event_name')

    def test_passing_data(self):
        def foo(event):
            self.assertEqual('event_name', event.name)
            self.assertEqual(3, event['x'])
        self.bus.call(foo, on='event_name')
        self.bus.fire('event_name', x=3)

    def test_multicall(self):
        mock = Mock()
        self.bus.call(mock, on='event_name')
        self.bus.call(mock, on='event_name')
        self.bus.call(mock, on='different_name')
        self.bus.fire('event_name', x=3)
        self.assertEqual(2, mock.call_count)

    def test_different_events(self):
        foo = Mock()
        bar = Mock()
        self.bus.call(foo, on='event_name')
        self.bus.call(bar, on='different_name')
        self.bus.fire('event_name', x=3)
        self.assertTrue(foo.called)
        self.assertFalse(bar.called)
        self.bus.fire('different_name', x=3)
        self.assertTrue(bar.called)
        self.assertEqual(1, foo.call_count)

    def test_dont_call(self):
        foo = Mock()
        bar = Mock()
        self.bus.call(foo, on='event_name')
        self.bus.call(bar, on='event_name')
        self.bus.dont_call(foo, on='event_name')
        self.bus.fire('event_name', x=3)
        self.assertFalse(foo.called)
        self.assertTrue(bar.called)

    def test_has_publisher(self):
        self.assertFalse(self.bus.has_publisher('event_name'))
        self.bus.might_fire(self, 'event_name')
        self.assertTrue(self.bus.has_publisher('event_name'))

    def test_get_unpublished_required_registrations(self):
        self.assertEqual(0, len(self.bus.get_unpublished_required_registrations()))
        foo = Mock()
        self.bus.call(foo, on='event_name')
        unpublished = self.bus.get_unpublished_required_registrations()
        self.assertEqual(1, len(unpublished))
        self.assertTrue('event_name' in unpublished)
        registration_information = unpublished['event_name']


if __name__ == '__main__':
    unittest.main()
