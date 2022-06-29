from rb_base_command import RbBaseCommand

class RclassExtCommand(RbBaseCommand):
    program = "rclass_ext"
    help_string = "retrieves and prints the rb_classext_struct for the VALUE pointer passed in"

    def __init__(self, debugger, internal_dict):
        self.internal_dict = internal_dict

    def __call__(self, debugger, command, exe_ctx, result):
        super().__call__(debugger, command, exe_ctx, result)
        target, _process, _thread, frame = self.build_environment(debugger)

        uintptr_t = target.FindFirstType("uintptr_t")
        rclass_t = target.FindFirstType("struct RClass")
        rclass_ext_t = target.FindFirstType("rb_classext_t")

        rclass_addr = target.EvaluateExpression(command).Cast(uintptr_t)
        rclass_ext_addr = (rclass_addr.GetValueAsUnsigned() + rclass_t.GetByteSize())
        debugger.HandleCommand("p *(rb_classext_t *)%0#x" % rclass_ext_addr)
