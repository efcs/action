import re
from typing import Tuple, Union
from pydantic import BaseModel, Field
import os, sys, re
from enum import Enum
import rich
from typing import Any, Optional
import re

clang_error_re = re.compile(r"^(# \||)(?P<file>.*):(?P<line>\d+):(?P<column>\d+): error: (?P<text>.*)$", re.MULTILINE)

class ClangError(BaseModel):
  file: str
  line: int
  column : int
  text : str

  @staticmethod
  def try_parse(text):
    m = clang_error_re.match(text)
    if m is None:
      return None
    else:
      return ClangError.model_validate({
        'file': m.group('file'),
        'line': int(m.group('line')),
        'column': int(m.group('column')),
        'text': m.group('text')})


class TryParseResult:
  def __init__(self, success: bool, value: Any, raw : str = None):
    self.success = success
    self._value = value
    self._raw = raw if raw is not None else value

  @property
  def value(self):
    assert self.success
    return self._value

  @property
  def raw(self):
    assert self.success
    return self._raw

  def raise_if_failed(self):
    if not self.success:
      raise ValueError("TryParseResult failed")
    return self

  def __bool__(self):
    return self.success

  def __str__(self):
    return f"TryParseResult(success={self.success}, value={self.value})"

class StatusBlock(BaseModel):
  exit_code : int
  stdout : str
  groups : list[Any] = Field(default_factory=list)
  clang_diagnostics : list[ClangError] = Field(default_factory=list)


# A command block is a block of output text from LLVM's test suite defined as:
# either:
#  (A) One or more comment lines (the header), followed by one or more non-comment
# lines
class CommandBlock(BaseModel):
    header: str = ''
    body: str = ''


TEST_CASES = [
'''
Exit Code: 0

Command Output (stdout):
--
# COMPILED WITH
/usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/runs.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings  -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir/t.tmp.exe
# executed command: /usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/runs.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir/t.tmp.exe
# EXECUTED AS
/home/eric/.pyenvs/idea/bin/python3 /home/eric/llvm-project/libcxx/utils/run.py --execdir /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir --  /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir/t.tmp.exe
# executed command: /home/eric/.pyenvs/idea/bin/python3 /home/eric/llvm-project/libcxx/utils/run.py --execdir /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir -- /home/eric/llvm-project/build/libcxx/test/std/example/Output/runs.pass.cpp.dir/t.tmp.exe

--
''',
'''
Exit Code: 250

Command Output (stdout):
--
# COMPILED WITH
/usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/fails-to-run.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings  -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir/t.tmp.exe
# executed command: /usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/fails-to-run.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir/t.tmp.exe
# EXECUTED AS
/home/eric/.pyenvs/idea/bin/python3 /home/eric/llvm-project/libcxx/utils/run.py --execdir /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir --  /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir/t.tmp.exe
# executed command: /home/eric/.pyenvs/idea/bin/python3 /home/eric/llvm-project/libcxx/utils/run.py --execdir /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir -- /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-run.pass.cpp.dir/t.tmp.exe
# .---command stderr------------
# | t.tmp.exe: /home/eric/llvm-project/libcxx/test/std/example/fails-to-run.pass.cpp:4: int main(): Assertion `false && "shit"' failed.
# `-----------------------------
# error: command failed with exit status: 250

--
''',
'''
Exit Code: 1

Command Output (stdout):
--
# COMPILED WITH
/usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings  -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-compile.pass.cpp.dir/t.tmp.exe
# executed command: /usr/local/bin/clang++ /home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp -pthread --target=x86_64-unknown-linux-gnu -nostdinc++ -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/build/libcxx/include/c++/v1 -I /home/eric/llvm-project/libcxx/test/support -std=c++26 -Werror -Wall -Wctad-maybe-unsupported -Wextra -Wshadow -Wundef -Wunused-template -Wno-unused-command-line-argument -Wno-attributes -Wno-pessimizing-move -Wno-noexcept-type -Wno-atomic-alignment -Wno-reserved-module-identifier -Wdeprecated-copy -Wdeprecated-copy-dtor -Wno-user-defined-literals -Wno-tautological-compare -Wsign-compare -Wunused-variable -Wunused-parameter -Wunreachable-code -Wno-unused-local-typedef -Wno-local-type-template-args -Wno-c++11-extensions -Wno-unknown-pragmas -Wno-pass-failed -Wno-mismatched-new-delete -Wno-redundant-move -Wno-self-move -D_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER -D_LIBCPP_ENABLE_EXPERIMENTAL -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -Werror=thread-safety -Wuser-defined-warnings -lc++experimental -nostdlib++ -L /home/eric/llvm-project/build/libcxx/lib -Wl,-rpath,/home/eric/llvm-project/build/libcxx/lib -lc++ -o /home/eric/llvm-project/build/libcxx/test/std/example/Output/fails-to-compile.pass.cpp.dir/t.tmp.exe
# .---command stderr------------
# | /home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp:6:7: error: no viable overloaded '+='
# |     6 |     S += V;
# |       |     ~ ^  ~
# | /home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp:12:5: note: in instantiation of function template specialization 'foo<std::vector<int>>' requested here
# |    12 |     foo(s, v);
# |       |     ^
# | /home/eric/llvm-project/build/libcxx/include/c++/v1/string:1216:71: note: candidate function not viable: no known conversion from 'const std::vector<int>' to 'const string' for 1st argument
# |  1216 |     _LIBCPP_HIDE_FROM_ABI _LIBCPP_CONSTEXPR_SINCE_CXX20 basic_string& operator+=(const basic_string& __str) {
# |       |                                                                       ^          ~~~~~~~~~~~~~~~~~~~~~~~~~
# | /home/eric/llvm-project/build/libcxx/include/c++/v1/string:1225:5: note: candidate template ignored: requirement '__can_be_converted_to_string_view<char, std::char_traits<char>, std::vector<int, std::allocator<int>>>::value' was not satisfied [with _Tp = std::vector<int>]
# |  1225 |     operator+=(const _Tp& __t) {
# |       |     ^
# | /home/eric/llvm-project/build/libcxx/include/c++/v1/string:1229:71: note: candidate function not viable: no known conversion from 'const std::vector<int>' to 'const value_type *' (aka 'const char *') for 1st argument
# |  1229 |     _LIBCPP_HIDE_FROM_ABI _LIBCPP_CONSTEXPR_SINCE_CXX20 basic_string& operator+=(const value_type* __s) {
# |       |                                                                       ^          ~~~~~~~~~~~~~~~~~~~~~
# | /home/eric/llvm-project/build/libcxx/include/c++/v1/string:1233:71: note: candidate function not viable: no known conversion from 'const std::vector<int>' to 'value_type' (aka 'char') for 1st argument
# |  1233 |     _LIBCPP_HIDE_FROM_ABI _LIBCPP_CONSTEXPR_SINCE_CXX20 basic_string& operator+=(value_type __c) {
# |       |                                                                       ^          ~~~~~~~~~~~~~~
# | /home/eric/llvm-project/build/libcxx/include/c++/v1/string:1240:19: note: candidate function not viable: no known conversion from 'const std::vector<int>' to 'initializer_list<value_type>' (aka 'initializer_list<char>') for 1st argument
# |  1240 |     basic_string& operator+=(initializer_list<value_type> __il) { return append(__il); }
# |       |                   ^          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# | 1 error generated.
# `-----------------------------
# error: command failed with exit status: 1
--
'''
]


class ExecutedCommandBlock(BaseModel):
  command : str
  stdout : Optional[str] = None
  stderr : Optional[str] = None
  error_message : Optional[str] = None

class LineLexer:
  def __init__(self, lines, n):
    self.lines = lines
    self.n = n

  def peek(self):
    if self.n < len(self.lines):
      return self.lines[self.n]
    else:
      return None

  def ignore_blank(self, one = False):
    while self.peek() and self.peek().strip() == '':
      self.n += 1
      if one:
        return


  def untake(self):
    self.n -= 1

  def take_if(self, pred):
    if pred(self.peek()):
      return self.take()
    else:
      return None

  def take_if_prefix(self, prefix, remove_prefix = True):
    if self.peek().startswith(prefix):
      if remove_prefix:
        return TryParseResult(True, self.take().value[len(prefix):])
      else:
        return self.take()
    else:
      return TryParseResult(False, None)

  def take_while(self, pred):
    while self.__bool__() and pred(self.peek()):
      yield self.take()

  def take_matching(self, pattern, group = None):
    r = re.compile(pattern)
    m = r.match(self.peek())
    if m is None:
      return TryParseResult(False, None)
    self.take()
    if group is None:
      return TryParseResult(True, m.group())
    else:
      return TryParseResult(True, m.group(group))


  def take(self):
    if self.n < len(self.lines):
      self.n += 1
      return TryParseResult(True, self.lines[self.n - 1])
    else:
      raise IndexError("No more lines")

  def try_take_comment(self):
    if self.peek().startswith('#'):
      ln = self.take()
      return TryParseResult(True, ln[1:].strip(), raw = ln)
    else:
      return TryParseResult(False, None)

  def try_take_comment_block(self):

    if self.peek().startswith('# '):
      header = self.take()[1:].strip()
      body = ''
      while self.peek() and not self.peek().startswith('#'):
        body += self.take()
      return TryParseResult(True, NestedCommentBlock(header=header, body=body))
    else:
      return TryParseResult(False, None)

  def try_parse_executed_command_block(self):
    ln = self.peek()
    if not ln.startswith('# executed command:'):
      return TryParseResult(False, None)
    else:
      cmd = self.take().value
      cmd = cmd[len('# executed command: '):]
      blocks = {}
      while self.peek() and self.peek().startswith('# .---'):
        cmd_header = self.take_matching(r'# \.---([-]*)(?P<HEADER>[^-]+)[-]+$', 'HEADER')
        rich.print('command header', cmd_header)
        lines = [ln.value[len('# | '):] for ln in self.take_while(lambda x: x.startswith('# |'))]
        end_ln = self.take_if_prefix('# `---').raise_if_failed()
        blocks[cmd_header.value] = '\n'.join(lines)

      res = self.take_matching('# error: (?P<ERROR_MSG>.*)', 'ERROR_MSG').raise_if_failed()
      full =  {
        'command': cmd,
        'stderr': blocks['command stderr'] if 'command stderr' in blocks else None,
        'stdout': blocks['command stdout'] if 'command stdout' in blocks else None,
        'error_message': res.value
      }
      return TryParseResult(True, ExecutedCommandBlock(**full))

  def try_parse_command_block(self):
    ln = self.peek()
    if ln := self.take_matching(r'^# (?P<TITLE>[A-Z\s]+)\s*$', 'TITLE'):
      title = ln.value
      body = ''
      while self.peek() and not self.peek().startswith('#'):
        body += self.take().value
      return TryParseResult(True, CommandBlock(header=title, body=body))
    else:
      return TryParseResult(False, None)

  def try_parse_status_block(self):
    if not self.peek().startswith('Exit Code:'):
      return TryParseResult(False, None)
    exit_code = self.take_matching(r'^Exit Code: (?P<EXIT_CODE>\d+)$', 'EXIT_CODE').raise_if_failed()
    self.ignore_blank()
    self.take_matching(r'^Command Output \(stdout\):$').raise_if_failed()
    self.ignore_blank()
    output = ''
    while self.peek() and not self.peek().startswith('#'):
      output += self.take()
    return TryParseResult(True, StatusBlock(exit_code=exit_code.value, stdout=output))

  def try_parse_block(self):
    if sb := self.try_parse_status_block():
      return sb
    elif eb := self.try_parse_executed_command_block():
      return eb
    elif cb := self.try_parse_command_block():
      return cb
    else:
      return TryParseResult(False, None)


  def take_while(self, pred):
    while self.peek() and pred(self.peek()):
      yield self.take()


import unittest

class TestParse(unittest.TestCase):
  def test_group_blocks(self):
    cmd_block = '''
# executed command: foo bar
# .---command stdout------------
# | hello
# | world
# `-----------------------------
# .---command stderr------------
# | error
# | message
# `-----------------------------
# error: command failed with exit status: 1
'''.strip()
    lexer = LineLexer(cmd_block.splitlines(), 0)
    exe = lexer.try_parse_executed_command_block().raise_if_failed()
    value = exe.value
    self.assertTrue(exe)
    self.assertEqual(value.command, 'foo bar')
    rich.print(value)
    self.assertEqual(value.stdout, 'hello\nworld')

  def test_take_command_block(self):
    cmd_block = '''
# EXECUTED
clang++ foo
# RAN
g++ bar
'''.strip()
    lexer = LineLexer(cmd_block.splitlines(), 0)
    b = lexer.try_parse_command_block().raise_if_failed()
    self.assertTrue(b)
    self.assertEqual(b.value.header, 'EXECUTED')
    self.assertEqual(b.value.body, 'clang++ foo')
    b = lexer.try_parse_command_block().raise_if_failed()
    self.assertTrue(b)
    self.assertEqual(b.value.header, 'RAN')
    self.assertEqual(b.value.body, 'g++ bar')

    lexer = LineLexer(cmd_block.splitlines(), 0)
    b = lexer.try_parse_block()
    self.assertTrue(b)
    self.assertEqual(b.value.header, 'EXECUTED')

  def test_clang_error_re(self):
    test_diags = [
'''
# | /home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp:6:7: error: no viable overloaded '+='
''',
'''
/home/eric/llvm-project/libcxx/test/std/example/fails-to-compile.pass.cpp:6:7: error: no viable overloaded '+='
'''
    ]
    for t in test_diags:
      t = t.strip()
      m = ClangError.parse(t)
      self.assertIsNotNone(m)
      self.assertEqual(m.line, 6)


class LibcxxTestOutput(BaseModel):
  Output : list[Union[ExecutedCommandBlock, CommandBlock, str]] = Field(default_factory=list)

