import numpy as np
import validations
import Error_collector

class MultiCoord(object):

  def __init__(self, dim=None):
    self._dim = dim if validations.isNumeric(dim) else 1
    self._coords_labels = []
    self._coords = []

  def AddData(self, data_list):
    if validations.isList(data_list):
      for idx in data_list:

        if validations.isList(idx):
          if self._coords != [] and len(idx) <> self._dim:
            pass
            #Error - coord_set not same size
          elif not self._coords:
            self._dim = len(idx)
            self._coords = [[] for i in xrange(len(idx))]


          [self._coords[i].append(idx[i]) for i in xrange(len(idx))]







class RollingList(object):
  """A List that has a maximum number of indexes.

  Newest additions are added to the end of the list until list_limit value
  is reached.  At that point, the zero-index is removed as new values continue
  to be added to the end.
  """
  _DEFAULT_MAX_LIST_LENGTH = 50

  _error = Error_collector.Errors()
  _copyableFields = ['base_error_key','list_name','list_description','list_label','_rollinglist','_listlimit',
                     '_only_numerical','_high', '_low','periods']
  def __init__(self, input_data=None, error_key= None):
    self._base_error_key = error_key

    self.list_name = None
    self.list_description = None
    self.list_label = None

    self._rollinglist = []
    self._listlimit = self._DEFAULT_MAX_LIST_LENGTH
    self._only_numerical = True
    self.periods = 0


    self._high = None
    self._low = None
    self._range = None

    # Accept Default values and add initial value/value-set
    if input_data:
      self.Add(input_data)

  def __len__(self):
    return len(self._rollinglist)

  def __repr__(self):
    this_repr = {}
    for item in vars(self):
      if not item.startswith('_') and item[0] == item[0].lower():
        this_repr[item] = getattr(self, item)
    return '<RollingList({0})>'.format(this_repr)

  @property
  def get(self):
    if len(self):
      return self._rollinglist[-1]
    else:
      return None

  @property
  def limit(self):
    return self._listlimit

  @property
  def list(self):
    return self._rollinglist

  @property
  def high(self):
    if self._only_numerical:
      return self._high
    else:
      return None

  @property
  def low(self):
    if self._only_numerical:
      return self._low
    else:
      return None

  @property
  def range(self):
    if self._only_numerical and self.high and self.low:
      return self.high - self.low
    else:
      return None

  @property
  def high_curr(self):
    if len(self) and self._only_numerical:
      return np.max(self._rollinglist)
    else:
      return None

  @property
  def low_curr(self):
    if len(self) and self._only_numerical:
      return np.min(self._rollinglist)
    else:
      return None

  @property
  def range_curr(self):
    if len(self) and self._only_numerical:
      return self.high_curr - self.low_curr


  def _Add(self, val):
    if (self._only_numerical and validations.isNumeric(val)) or not self._only_numerical :
      self._rollinglist.append(val)
      self.periods += 1

      if self._only_numerical and validations.isNumeric(val):
        self._high = val if val > self._high or self._high is None else self._high
        self._low = val if val < self._low or self._low is None  else self._low
        self._range = self.high - self.low if self.high and self.low else None

      if len(self) > self._listlimit:
        self._Delete(0)
    else:
      # Add Error handling here
      pass

  def Add(self, val):
     if self._only_numerical and validations.isNumeric(val):
       if validations.isList(val):
         for x in val:
           self._Add(x)
       else:
         self._Add(val)
     elif not self._only_numerical:
       self._Add(val)
     else:
       pass
       # Add Error Handling Here

  add = Add
  def _Delete(self, idx):
    if validations.isNumeric(idx):
      if idx < len(self):
        self._rollinglist.pop(idx)

  def AllowAllValues(self):
    self._only_numerical = False
    self._high = None
    self._low = None
    self._range = None

  def AllowOnlyNum(self, cleanse = True):
    self._only_numerical = True
    if validations.isNumeric(self._rollinglist):
      if cleanse:
        for i, val in enumerate(self._rollinglist):
          if not validations.isNumeric(val):
            self._rollinglist.pop(i)

      self._high = np.max(self._rollinglist)
      self._low = np.max(self._rollinglist)
      self._range = self.high - self.low
    else:
      self._high = None
      self._low = None
      self._range = None

  def SetLimit(self, val):
    if validations.isNumeric(val):
      self._listlimit = val

  def Reset(self):
    self._rollinglist = []

  def ResetLV(self):
    self._high = None
    self._low = None
    self._range = None

  def ResetAll(self):
    self.Reset()
    self.ResetLV()

  def Copy(self):
    temp = RollingList()
    for field in self._copyableFields:
      setattr(temp, field, getattr(self, field))
    return temp
  copy = Copy

class MovingAverage(RollingList):
  """Specialized RollingList object used for Moving Averages."""

  _DEFAULT_SCOPES = {
    '9-period MA':9,
    '15-period MA':15,
    '26-period MA': 26
  }

  def __init__(self, error_key=None):
    super(MovingAverage, self).__init__()
    self._scopes = self._DEFAULT_SCOPES
    self._only_numerical = False
    self.base_error_key = error_key

  @property
  def maxscope(self):
    return np.max(self._scopes.values())

  def AddScope(self, label=None, value=None):
    if label and validations.isNumeric(value):
      self._scopes[label] = value
    else:
      pass # Error exception handling here

  def DelScope(self, val):
    if validations.isNumeric(val):
      for k, v in self._scopes.iteritems():
        if val == v:
          self._scopes.pop(k, None)
    elif isinstance(val, str):
      self._scopes.pop(val, None)

  def AddData(self, RL_obj):
    """Receives RollingList object to calculate trailing MA values as per
    scope definitions.

    """
    if issubclass(type(RL_obj), RollingList):
      data_set = RL_obj.list
      new_data = []
      for label, scope_factor in self._scopes.iteritems():
        if len(data_set) >= scope_factor and validations.isNumeric(data_set):
          subset = data_set[-1 * scope_factor:]
          avg = np.mean(subset)
        else:
          avg = "NA"
        new_data.append((label, scope_factor, avg))
      self.Add(tuple(new_data))


