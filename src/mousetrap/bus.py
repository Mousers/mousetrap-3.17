from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

'''Provides an event-based, publish-subscribe implementation that allows
components to communicate with minimal coupling.

Example
-------

Code

    class Publisher:
        def __init__(self, bus):
            self.bus = bus

        def foo(self):
            self.bus.fire('foo_called', x=3)

    class Subscriber:
        def __init__(self, bus):
            bus.call(self.bar, on='foo_called')

        def bar(self, event):
            print(event['x'])

    bus = Bus()
    Subscriber(bus)
    Subscriber(bus)
    publisher = Publisher(bus)
    publisher.foo()


Output

    3
    3


Enforcing required events
-------------------------

As a sanity check, it may be useful to require that every event that has a
registered callback also have a registered publisher. This helps avoid
situations where a subscriber registers a callback for an event that will never
be fired.

To address this, we can ask that all would-be publishers of an event to declare
that they might_fire that event. Of course that doesn't guarentee they will fire
that event, but at least there is a possibility that the event will fire.

    class Publisher:
        def __init__(self, bus):
            bus.might_fire(self, 'some_event')

Now we can imagine an initialization process in which publishers declare the
events they might_fire, and subscribers register callbacks for those events (in
any order). After this initialization process, we can check if there are any
events that do not have a publisher as follows.

    offending_registrations = bus.get_unpublished_required_registrations()

The result is a dict containing registrations for unpublished events (i.e., no
one called might_fire for those events). We might print a warning for each.

    for event, registration in offending_registrations.items():
        callback = registration['callable']
        trace_to_registration = registration['trace']

        callback_name = callback.__name__
        formatted_trace = traceback.format_list(trace_to_registration))

        print('WARNING: %s\nWARNING: %s is registered for an unpublished event %s' %
            (formatted_trace, callback_name, event))

The trace is formatted according to traceback.extract_tb .
'''
import traceback


class Bus(object):
    def __init__(self):
        self._callbacks = {}
        self._required = {}
        self._publishers = {}

    def call(self, callable, on, optional=False):
        '''Register callable for named event (on).

        Example:

            def log_save(event):
                assert type(event) is Event
                ...

            bus.call(log_save, on='saved_file', optional=True)

        Parameters:

            callable -- A callable that accepts a single Event parameter.
            
            on -- A hashable naming an event (typically a str).

            optional -- A bool indicating if the event is optional (True) or
            required (False; default). A required event requires that a
            publisher has declared that it will fire the event. This method does
            not enforce this requirement, it just marks the event as required or
            not making it possible to enforce it using
            get_unpublished_required_registrations.
        '''
        self._get_callbacks(on).append(callable)
        if not optional:
            trace = traceback.extract_stack()
            self._get_required(on).append({'callable':callable, 'trace':trace})

    def dont_call(self, callable, on):
        '''Unregister callable for named event (on).
        
        Example

            bus.dont_call(log_save, on='saved_file')

        Parameters

            callable -- A callable.

            on -- A hashable naming an event (typically a str).
        '''
        self._get_callbacks(on).remove(callable)
        registrations = self._get_required(on)
        self._required[on] = [
                    registration for registration in registrations
                    if registration['callable'] != callable
                ]

    def fire(self, event, data=None, **keyword_args):
        '''Calls callables registered for event named by event.name. The
        parameters for fire are the same as those for Event.__init__.
        '''
        event = Event(event, data, **keyword_args)
        callbacks = self._get_callbacks(event.name)
        for callback in callbacks:
            callback(event)

    def might_fire(self, publisher, event_name):
        '''Declare publisher will fire the named event.
        
        Parameters

            publisher -- Can be any object. Usually it's the object that plans
            to fire events.

            event_name -- A hashable naming an event (typically a str).
        '''
        publishers = self._get_publishers(event_name)
        publishers.append(publisher)

    def wont_fire(self, publisher, event_name):
        '''Declare publisher wont fire the named event.

        Parameters

            publisher -- Can be any object. Usually it's the object that plans
            to fire events.

            event_name -- A hashable naming an event (typically a str).
        '''
        publishers = self._get_publishers(event_name)
        publishers.remove(publisher)

    def get_unpublished_required_registrations(self):
        '''Return registration information for required events without a
        declared publisher.

        Return -- a dict whose keys are the event names and whose values are
        lists of (callable, trace), where callable is the callable that is
        registered for the event, and trace is the stack trace when the callable
        was registered (as returned by traceback.extract_tb).
        '''
        unpublished_required_registrations = {}
        for event_name in self._required:
            if not self.has_publisher(event_name):
                unpublished_required_registrations[event_name] = self._required[event_name]
        return unpublished_required_registrations

    def has_publisher(self, event_name):
        '''Return True if the name event has a declared publisher.'''
        return len(self._get_publishers(event_name)) > 0

    def _get_callbacks(self, event_name):
        self._callbacks[event_name] = self._callbacks.get(event_name, [])
        return self._callbacks[event_name]

    def _get_required(self, event_name):
        self._required[event_name] = self._required.get(event_name, [])
        return self._required[event_name]

    def _get_publishers(self, event_name):
        self._publishers[event_name] = self._publishers.get(event_name, [])
        return self._publishers[event_name]


class Event(dict):
    '''Events are used to transmit data from publishers to subscribers on an
    bus. The name of an event is used to route transmissions to subscribers;
    i.e., only subscribers who have registered for the name of an event will
    receive events with that name.

    Examples

        event = Event('saved_file')
        assert event.name == 'saved_file'

        event = Event('saved_file', x=1, y='hi')
        assert event['x'] == 1
        assert event['y'] == 'hi'

        event = Event('saved_file', {'x':1, 'y':'hi'})
        assert event['x'] == 1
        assert event['y'] == 'hi'

        event = Event('saved_file', {'x':1, 'y':'hi'}, y='bye')
        assert event['x'] == 1
        assert event['y'] == 'bye'
    '''

    def __init__(self, _event_name_, _data_=None, **keyword_args):
        '''Keyword arguments with single underscore, _keyword_, are reserved.

        '''
        if _data_ is not None:
            self.update(_data_)
        self.update(keyword_args)
        self.name = _event_name_
