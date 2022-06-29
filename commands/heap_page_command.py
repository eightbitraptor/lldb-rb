import lldb

from constants import *
from rb_base_command import RbBaseCommand

class HeapPageCommand(RbBaseCommand):
    program = "heap_page"
    help_string = "prints out 'struct heap_page' for a VALUE pointer in the page"

    def __init__(self, debugger, _internal_dict):
        self.internal_dict = _internal_dict

    def __call__(self, debugger, command, exe_ctx, result):
        super().__call__(debugger, command, exe_ctx, result)
        target, _process, _thread, frame = self.build_environment(debugger)

        self.tHeapPageBody = target.FindFirstType("struct heap_page_body")
        self.tHeapPagePtr = target.FindFirstType("struct heap_page").GetPointerType()

        page = self._get_page(target, frame.EvaluateExpression(command))
        page.Cast(self.tHeapPagePtr)

        self._append_command_output(debugger, "p (struct heap_page *) %0#x" % page.GetValueAsUnsigned(), result)
        self._append_command_output(debugger, "p *(struct heap_page *) %0#x" % page.GetValueAsUnsigned(), result)

    def get_short_help(self):
        return self.__class__.help_string

    def _get_page_body(self, target, val):
        addr = val.GetValueAsUnsigned()
        page_addr = addr & ~(HEAP_PAGE_ALIGN_MASK)
        address = lldb.SBAddress(page_addr, target)
        return target.CreateValueFromAddress("page", address, self.tHeapPageBody)

    def _get_page(self, target, val):
        body = self._get_page_body(target, val)
        return body.GetValueForExpressionPath("->header.page")
