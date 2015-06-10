from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


class Component(object):
    '''Components provide units of functionality for MouseTrap. Components
    communicate with eachother through events.

    Each component is in one of three states: stopped. running. or paused. A
    component is initially in the stopped state. A component only receives or
    fires events from other components in the running state (it may still
    receive events from the system). A component in the stopped state uses
    minimal resources, whereas a component in the paused state retains
    resources in anticipation of being resumed.

    To implement a component, inherit from Component and override init(),
    start(), pause(), resume(), and stop() as needed. You may also call
    Component's on() method to register callbacks for events. These will
    automatically be registered and unregistered when your component's state is
    changed. For example when your component transitions from stopped to
    running, all callbacks that you registered using the component's on() are
    automatically registered for the events. When your component is paused,
    they will automatically be unregistered. You can also use component's off()
    to unregister callbacks for events.

    Methods starting with _ are not intended to be overriden.
    '''

    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, service):
        '''Do not override. Instead override init().'''
        self._service = service
        self._state = self.STATE_STOPPED
        self._event_registrations = []
        self._service.call(self._start, on='start_components')
        self.init()

    def init(self):
        '''Initialize the component. Override this instead of __init__().
        Do not perform resource intensive initialization here.
        '''
        pass

    def _start(self, event):
        '''Start the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._start, on='start_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._pause, on='pause_components')
        for registration in self._event_registrations:
            registration.register(bus=self._service)
        self._state = self.STATE_RUNNING
        self.start()

    def start(self):
        '''Start the component. Perform any resource intensive initialization.
        Since the configuration may have changed, also check and adjust the
        configuration.
        '''
        pass

    def _stop(self, event):
        '''Stop the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._stop, on='stop_components')
        self._service.dont_call(self._pause, on='pause_components')
        self._service.call(self._start, on='start_components')
        for registration in self._event_registrations:
            registration.unregister(bus=self._service)
        self._state = self.STATE_STOPPED
        self.stop()

    def stop(self):
        '''Stop the component and free resources.'''
        pass

    def _pause(self, the_event):
        '''Event callback that pauses the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._pause, on='pause_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._resume, on='resume_components')
        for registration in self._event_registrations:
            registration.unregister(bus=self._service)
        self._state = self.STATE_PAUSED
        self.pause()

    def pause(self):
        '''Pause the component without freeing resources.'''
        pass

    def _resume(self, the_event):
        '''Resume the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._resume, on='resume_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._pause, on='pause_components')
        for registration in self._event_registrations:
            registration.register(bus=self._service)
        self._state = self.STATE_RUNNING
        self.resume()

    def resume(self):
        '''Start the component after having been paused. Since the
        configuration may have changed, check and adjust to the
        current configuration. Unless a change in configuration indicates
        otherwise, the component does not need to perform resource intensive
        initialization.  However, if a change in configuration warrents
        reinitialization, then the component may do so.
        '''
        pass

    def call(self, callback, on, optional=False):
        '''Register callback for event_name.'''
        registration = EventRegistration(callback, on, optional)
        self._event_registrations.append(registration)
        if self._state == self.STATE_RUNNING:
            registration.register(self._service)

    def dont_call(self, callback, on):
        '''Unregister callback for event_name.'''
        registration = EventRegistration(callback, on)
        self._event_registrations.remove(registration)
        self._service.dont_call(callback, on)

    def fire(self, event_name, **data):
        '''Fire event_name with keyword parameters as data.'''
        self._service.fire(event_name, data, source=self)

    def may_fire(self, event_name):
        self._service.may_fire(self, event_name)

    def wont_fire(self, event_name):
        self._service.wont_fire(self, event_name)

    def logger(self):
        return self._service.logger(self)

    def config(self):
        return self._service.config(self)

    def config_full(self):
        return self._service.config()


class EventRegistration(object):
    '''Represents a callback being registered for an event.'''
    def __init__(self, callback, event_name, optional=False, trace=None):
        import traceback
        self.trace = trace if trace is not None else traceback.extract_stack()
        self.event_name = event_name
        self.callback = callback
        self.optional = optional
        self.trace = trace

    def register(self, bus):
        bus.call(self.callback, self.event_name, self.optional, self.trace)

    def unregister(self, bus):
        bus.dont_call(self.callback, on=self.event_name)

    def __eq__(self, other):
        return self.event_name == other.event_name and \
                self.callback == other.callback
