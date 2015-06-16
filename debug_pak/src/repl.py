from io import StringIO
import sys
import logging

logger = logging.getLogger(__name__)


class DebugInterpreter:
    def __init__(self):
        self.locals = dict()
        self.globals = dict()

    def run_code(self, code):
        out = StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = [out, out]
        try:
            exec(code, self.globals, self.locals)
        except Exception as ex:
            out.write("[[b;red;]{}] [[;#FFF;]{}]".format(type(ex).__name__, str(ex)))
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

        out.seek(0)
        return out.read().strip()

    def run_repl(self, code):
        if code[0] == '@':
            repl_tpl = code[1:]
        else:
            repl_tpl = ("__result__ = (%s)\n"
                        "if __result__:\n"
                        "    print('::', __result__)\n"
                        "del __result__") % code

        return self.run_code(repl_tpl)
