import warnings
import pty
import subprocess
import shlex
import pathlib
import os
import sys
from code import InteractiveConsole
from codeop import CommandCompiler 
from utils import is_python_statement



class PsuedoTerminal:
  def __init__(self):
    #master, slave = pty.openpty()
    #print(type(master), type(slave))
    #self.cwd = str(pathlib.Path.home())
    process_id, id =  pty.fork()
    print(process_id, id)
    print(type(process_id), type(id))
    print("The Process ID for the Current process is: " + str(os.getpid()))
    print("The Process ID for the Child process is: " + str(process_id))
    print('Name of the Slave: ' + str(os.ttyname(process_id)))


  

class Python_REPL(PsuedoTerminal):
  def __init__(self):
    super().__init__()

  def run_cmd(self, cmd:str):
    '''
    cmd = shlex.split(cmd)
    stream = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    ret = ''.join([b.decode('utf-8') for b in stream.communicate() if b])
    print(ret)
'''
    cmd = shlex.split(cmd)
    match cmd:
      case cmd if cmd[0] == 'python':
        cmd[0] = '/usr/bin/python3' 
      case ['cd', *args]:
        pass
      case _:
        pass
    print(cmd)
    subprocess.call(cmd, shell=True, cwd=self.cwd)
    ret = subprocess.check_output(cmd, shell=True, cwd=self.cwd)
    return ret
  def cd(self):
    os.chdir('..')



class PythonREPL2(InteractiveConsole):

  def __init__(self):
    super().__init__()
    self.ret_msg = None

  def write(self, data) -> None: #overwrite the write function in class InteractiveInterpreter:
    self.ret_msg = data

  def runcode(self, code, source) -> None: #overwrite the runcode function in class InteractiveInterpreter:
    try:
      exec(code, self.locals)
      print(self.locals.keys())
      print(self.locals['__builtins__'].keys())
      default_ret = self.locals['__builtins__'].get('_')
      #print(f'source: {source} source_type: {type(source)}')
      if default_ret and source.isalpha():
        self.ret_msg = default_ret
    except SystemExit:
      raise
    except:
      self.showtraceback()

  

  


class PythonREPL_CODE(InteractiveConsole):

  def __init__(self):
    super().__init__()
    self.ret_msg = None
    #self.compile = CustomCommandCompiler()

  def write(self, data) -> None: #overwrite the write function in class InteractiveInterpreter:
    self.ret_msg = data

  def runcode(self, code, source) -> None: #overwrite the runcode function in class InteractiveInterpreter:
    try:
      exec(code, self.locals)
      print(self.locals.keys())
      print(self.locals['__builtins__'].keys())
      default_ret = self.locals['__builtins__'].get('_')
      #print(f'source: {source} source_type: {type(source)}')
      if default_ret and source.isalpha():
        self.ret_msg = default_ret
    except SystemExit:
      raise
    except:
      self.showtraceback()

  def runsource(self, source, filename="<input>", symbol="single"):
    try:
      code = self.compile(source, filename, symbol)
    except (OverflowError, SyntaxError, ValueError):
        # Case 1
      self.showsyntaxerror(filename)
      return False

    if code is None:
      # Case 2
      return True

    # Case 3
    self.runcode(code, source)
    return False

  def push(self, line):
    self.ret_msg = None
    self.buffer.append(line)
    source = "\n".join(self.buffer)
    more = self.runsource(source, self.filename)
    if not more:
      self.resetbuffer()
    return more

class CustomCommandCompiler(CommandCompiler):
  def __init__(self):
    super().__init__()
  def __call__(self, source, filename="<string>", symbol="single"):
      r"""Compile a command and determine whether it is incomplete.

      Arguments:

      source -- the source string; may contain \n characters
      filename -- optional filename from which source was read;
                  default "<input>"
      symbol -- optional grammar start symbol; "single" (default) or
                "eval"

      Return value / exceptions raised:

      - Return a code object if the command is complete and valid
      - Return None if the command is incomplete
      - Raise SyntaxError, ValueError or OverflowError if the command is a
        syntax error (OverflowError and ValueError can be produced by
        malformed literals).
      """
      return _maybe_compile(self.compiler, source, filename, symbol)

def _maybe_compile(compiler, source, filename, symbol):
    # Check for source consisting of only blank lines and comments.
    for line in source.split("\n"):
        line = line.strip()
        if line and line[0] != '#':
            break               # Leave it alone.
    else:
        if symbol != "eval":
            source = "pass"     # Replace it with a 'pass' statement
    print(f'source: {source}')

    # Disable compiler warnings when checking for incomplete input.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", (SyntaxWarning, DeprecationWarning))
        try:
            compiler(source, filename, symbol)
        except SyntaxError:  # Let other compile() errors propagate.
            try:
                compiler(source + "\n", filename, symbol)
                return None
            except SyntaxError as e:
                if "incomplete input" in str(e):
                    return None
                # fallthrough

    return compiler(source, filename, symbol)

if __name__ == '__main__':
  pt1 = PsuedoTerminal()