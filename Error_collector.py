"""Data structure for collecting error messages."""

import collections
import json
import pprint

class Errors(object):
  """Data structure for collecting error messages.

  Usage:

  >>> errors = Errors()

  # Add an error message
  >>> errors.Add('a key', 'a message')

  # Or add multiple messages at once
  >>> errors.Add('some key', 'some message', 'another message')

  # Use None to specify "generic" errors
  >>> errors.Add(None, 'generic message')

  # Or, explicitly
  >>> errors.Add(errors.DEFAULT_KEY, 'generic message')

  # Errors are "truthy"
  >>> if errors:
  ...   DoSomethingWith(errors)

  # Get a JSON string
  >>> errors.AsJson()
  '{"some key": "some message\\nanother message",
    "__generic__": "generic message", "a key": "a message"}'
  """

  DEFAULT_KEY = '__generic__'

  DEFAULT_FMT = '\n'.join

  def __init__(self):
    self._errors = collections.defaultdict(list)

  def __nonzero__(self):
    return bool(self._errors)

  def __contains__(self, key):
    return key in self._errors

  def __len__(self):
    return sum(len(messages) for messages in self._errors.itervalues())

  def __iter__(self):
    return iter(self._errors)

  def __repr__(self):
    return '<Errors: %s>' % pprint.pformat(dict(self._errors))

  def Clear(self):
    self._errors.clear()

  def Get(self, key):
    """Gets error messages by key.

    Args:
      key: str, the key whose messages to retrieve. If omitted, the messages
          associated with the default key are retrieved.

    Returns:
      A list of messages for the given key, or None if the key is not present.
    """
    if not key:
      key = self.DEFAULT_KEY
    messages = self._errors.get(key)
    if messages:
      return list(messages)
    return None

  def GetAll(self):
    """Gets a copy of the internal errors dictionary."""
    return self._errors.copy()

  def Add(self, key, message, *messages):
    """Associates one or more messages with a given key.

    Args:
      key: str, the key to associate with a message. If omitted, the messages
          are associated with the default key.
      message: str, the message to associate with the key.
      *messages: additional messages to associate with the key.
    """
    if not key:
      key = self.DEFAULT_KEY
    messages = map(str, (message,) + messages)
    self._errors[key].extend(messages)

  def AsJson(self, format_func=DEFAULT_FMT):
    """Gets a JSON string representation of the error object.

    Args:
      format_func: function, used to format the list of messages for each key
          before transforming to JSON. The function should accept a list of
          strings and return a value that is JSON-serializable. The default
          behavior is to join each list of messages with a newline character.

    Returns:
      A JSON string of key/messages pairs.
    """
    errors = {k: format_func(v) for k, v in self._errors.iteritems()}
    return json.dumps(errors)

  def Merge(self, other):
    """Adds all errors from another Errors object to this one.

    Args:
      other: an Errors instance to merge into this one.
    """
    for key, messages in other.GetAll().iteritems():
      self.Add(key, *messages)

  def Raise(self, exception, key, message, *messages):
    """Adds error message(s) and raises the given exception."""
    self.Add(key, message, *messages)
    raise exception(self.AsJson())

  def RaiseIfAny(self, exception):
    """Raises the given exception with the errors as the message, if any."""
    if self:
      raise exception(self.AsJson())

  def LogIfAny(self, logging_func):
    """Logs the errors using the given logging_func."""
    if self:
      logging_func(self.AsJson())


class NullErrors(Errors):
  """Error collector that does nothing."""

  def Add(self, unused_key, unused_message, *unused_messages):
    pass
