import lldb
from pydoc import locate

class RbBaseCommand:
    @classmethod
    def register_lldb_command(cls, debugger, module_name):
        # Add any commands contained in this module to LLDB
        print(f"registering {module_name}.{cls.__name__} to {cls.program}")
        command = f"command script add -c {module_name}.{cls.__name__} {cls.program}"
        debugger.HandleCommand(command)


    def __call__(self, debugger, command, exe_ctx, result):
        if not ('RUBY_Qfalse' in globals()):
            self._lldb_init(debugger)


    def build_environment(self, debugger):
        target = debugger.GetSelectedTarget()
        process = target.GetProcess()
        thread = process.GetSelectedThread()
        frame = thread.GetSelectedFrame()

        return (target, process, thread, frame)


    def _append_command_output(self, debugger, command, result):
        output1 = result.GetOutput()
        debugger.GetCommandInterpreter().HandleCommand(command, result)
        output2 = result.GetOutput()
        result.Clear()
        result.write(output1)
        result.write(output2)

    def _lldb_init(self, debugger):
        target = debugger.GetSelectedTarget()
        global SIZEOF_VALUE
        SIZEOF_VALUE = target.FindFirstType("VALUE").GetByteSize()

        value_types = []
        g = globals()

        imemo_types = target.FindFirstType('enum imemo_type')

        for member in imemo_types.GetEnumMembers():
            g[member.GetName()] = member.GetValueAsUnsigned()

        for enum in target.FindFirstGlobalVariable('ruby_dummy_gdb_enums'):
            enum = enum.GetType()
            members = enum.GetEnumMembers()
            for i in range(0, members.GetSize()):
                member = members.GetTypeEnumMemberAtIndex(i)
                name = member.GetName()
                value = member.GetValueAsUnsigned()
                g[name] = value

                if name.startswith('RUBY_T_'):
                    value_types.append(name)
        g['value_types'] = value_types
