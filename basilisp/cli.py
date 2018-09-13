# noinspection PyUnresolvedReferences
import readline  # noqa: F401
import traceback
import types

import click

import basilisp.compiler as compiler
import basilisp.lang.runtime as runtime
import basilisp.main as basilisp
import basilisp.reader as reader


@click.group()
def cli():
    """Basilisp is a Lisp dialect inspired by Clojure targeting Python 3."""
    pass


def eval_file(filename: str, ctx: compiler.CompilerContext, module: types.ModuleType):
    """Evaluate a file with the given name into a Python module AST node."""
    last = None
    for form in reader.read_file(filename, resolver=runtime.resolve_alias):
        last = compiler.compile_and_exec_form(form, ctx, module, filename)
    return last


def eval_str(s: str, ctx: compiler.CompilerContext, module: types.ModuleType):
    """Evaluate the forms in a string into a Python module AST node."""
    last = None
    for form in reader.read_str(s, resolver=runtime.resolve_alias):
        last = compiler.compile_and_exec_form(form, ctx, module, source_filename='REPL Input')
    return last


@cli.command(short_help='start the Basilisp REPL')
@click.option('--default-ns', default=runtime._REPL_DEFAULT_NS, help='default namespace to use for the REPL')
def repl(default_ns):
    basilisp.init()
    ctx = compiler.CompilerContext()
    ns_var = runtime.set_current_ns(default_ns)
    while True:
        ns: runtime.Namespace = ns_var.value
        try:
            lsrc = input(f'{ns.name}=> ')
        except EOFError:
            break
        except KeyboardInterrupt:
            print('')
            continue

        if len(lsrc) == 0:
            continue

        try:
            print(compiler.lrepr(eval_str(lsrc, ctx, ns.module)))
        except reader.SyntaxError as e:
            traceback.print_exception(reader.SyntaxError, e, e.__traceback__)
            continue
        except compiler.CompilerException as e:
            traceback.print_exception(compiler.CompilerException, e,
                                      e.__traceback__)
            continue
        except Exception as e:
            traceback.print_exception(Exception, e, e.__traceback__)
            continue


@cli.command(short_help='run a Basilisp script or code')
@click.argument('file-or-code')
@click.option('-c', '--code', is_flag=True, help='if provided, treat argument as a string of code')
@click.option('--in-ns', default=runtime._REPL_DEFAULT_NS, help='namespace to use for the code')
def run(file_or_code, code, in_ns):
    """Run a Basilisp script or a line of code, if it is provided."""
    basilisp.init()
    ctx = compiler.CompilerContext()
    ns_var = runtime.set_current_ns(in_ns)
    ns: runtime.Namespace = ns_var.value

    if code:
        print(compiler.lrepr(eval_str(file_or_code, ctx, ns.module)))
    else:
        print(compiler.lrepr(eval_file(file_or_code, ctx, ns.module)))


if __name__ == "__main__":
    cli()