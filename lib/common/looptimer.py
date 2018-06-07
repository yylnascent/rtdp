import logging
import traceback

from threading import Timer

log = logging.getLogger('LoopTimer')

class LoopTimer(Timer):

    def __init__(self, interval, function, args=None, kwargs=None):
      self._exception_handler = None
      super().__init__(interval, function, args=None, kwargs=None)

    def run(self):
        while True:  
            self.finished.wait(self.interval)  
            if self.finished.is_set():  
                self.finished.set()  
                break
            
            try:
                self.function(*self.args, **self.kwargs)
            except Exception as exc:
                msg = traceback.format_exc()
                context = {
                    'message': msg,
                    'exception': exc
                }
                self.call_exception_handler(context)

    def get_exception_handler(self):
        """Return an exception handler, or None if the default one is in use.
        """
        return self._exception_handler

    def set_exception_handler(self, handler):
        if handler is not None and not callable(handler):
              raise TypeError('A callable object or None is expected, '
                              'got {!r}'.format(handler))
        self._exception_handler = handler

    def call_exception_handler(self, context):
      """Call the current event loop's exception handler.
      The context argument is a dict containing the following keys:
      - 'message': Error message;
      - 'exception' (optional): Exception object;
      - 'future' (optional): Future instance;
      - 'handle' (optional): Handle instance;
      - 'protocol' (optional): Protocol instance;
      - 'transport' (optional): Transport instance;
      - 'socket' (optional): Socket instance;
      - 'asyncgen' (optional): Asynchronous generator that caused
                               the exception.
      New keys maybe introduced in the future.
      Note: do not overload this method in an event loop subclass.
      For custom exception handling, use the
      `set_exception_handler()` method.
      """
      if self._exception_handler:
          try:
              self._exception_handler(context)
          except Exception as exc:
              # Exception in the user set custom exception handler.
              log.error('Exception in default exception handler '
                           'while handling an unexpected error '
                           'in custom exception handler',
                           exc_info=True)