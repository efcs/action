import json
from pathlib import Path
import os

LOC_KEYS = ['file', 'line', 'col', 'endLine', 'endCol', 'title']

WorkflowCommandKeys = {

  'notice': LOC_KEYS,
  'warning': LOC_KEYS,
  'error': LOC_KEYS,
  'group': [],
}

class WorkflowCommands:

  def _formatMessage(self, key, msg, **kwargs):
    arg_str = ''
    if kwargs:
      arg_str = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
      msg = msg.format(**kwargs)
    return json.dumps({key: msg})
  def warning(self, msg, file=None, line=None, endLine=None, title=None):
    self._add_message('warning', msg, file, line, endLine, title)
