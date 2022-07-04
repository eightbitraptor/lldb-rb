# lldb-rb

This repository contains LLDB helper functions for working on MRI/CRuby. It is an extraction of the code in the CRuby repository at `misc/lldb_cruby.py`

# Why

`lldb_cruby.py` manages lldb custom commands using functions. The file is a large list of functions, and an init handler that then aliases some of those functions to `lldb` commands so that they can be used during a debugging session. This has some advantages and disadvantages:

## Advantages

- Easy to see where to add new code: just create a function and write another line in the handler function to call `command script add -f`
- All the code is self contained and searchable.

## Disadvantages

- It's hard to see what's a usable lldb function and what's a utility function, everything exists in the same file with little visible organisation.
- The previous point also means that it's tough to work out what helpers are available to you, as someone authoring an lldb command
- Lots of duplication: Most lldb functions we write tend to need access to similar things (get the target, frame and thread, get the `RVALUE *` type, or a reference to `uintptr_t`) but because of the lack of discoverable structure, there's a lot of duplicated code.

### What are we doing here?

This repo attempts, rather grandiosely, to fix the disadvantages of the current approach and maintain, or enhance, the benefits. Some things that we're doing are:

- Class based API: We no longer use the function based api that `lldb` supports. We use the class based API instead. This means that there's a bit more boilerplate to write when we're implementing a new command, and in return for this it means that we can lean on inheritance, mix-ins, and composition, to share code between helpers to improve structure and readability.
- Auto-discovery of new commands: Each command class knows how to insert itself into the running `lldb` debugger, so as a command author you don't need to write `command script import -c my_package.MyClass my_command_name` or anything like that. If your class defines the correct variable and sticks to a simple naming convention then it will be available in `lldb` sessions automatically.


## How do I use this repository

Clone the repository somewhere onto your machine and then add the following line to your `~/.lldbinit`.

```
command script import /path/to/lldb-rb/lldb_cruby.py
```

## How do I implement a new command

In order to be automatically loaded a command has to fulfil the following criteria:

- The package file must exist inside the `commands` directory
- The package name must end in `_command.py`
- The package must implement a class whose name ends in `Command`
- The class must implement the `lldb` API (at minimum this means defining `__init__` and `__call__`)
- The class must have a class variable `package` that is a String. This is the name of the command you'll call in the `lldb` debugger.

### Example: The `test` command

Let's implement an `lldb` debugger command called `test`, so that when we type `test` in the debugger session it prints out `sizeof(rb_classext_t)`.

1. Create the file `commands/test_command.py` and open it in an editor.
2. Implement the following class:
   ```
   class TestCommand:
       program = "test"
       
       def __init__(self, debugger, _internal_dict):
           pass
       
       def __call__(self, debugger, command, exe_ctx, result):
           # do stuff here
    ```
    This is the bare minimum we need to implement in order to have our `test` command registered and working. But we need a little more in order to print out the output that we're looking for.
3. We need access to the local debugger in order to analyse data structures from the target thread, and write results back. There is a base class defined in `lldb-rb` to configure most of this for us, so let's change our `TestCommand` to inherit from `RbBaseCommand` and call the environment building functions[1]
   ```
   class TestCommand(RbBaseCommand):
       ...
       
       def __call__(self, debugger, command, exe_ctx, result):
           super().__call__(self, debugger, command, exe_ctx, result)
           target, process, thread, frame = self.build_environment(debugger)
   ```
4. Now that we've set up our superclass successfully we should now be able to access our globals and start printing stuff back to our lldb session.
   ```
       def __call__(self, debugger, command, exe_ctx, result):
           super().__call__(self, debugger, command, exe_ctx, result)
           tRbClassExtT = target.FindFirstType("rb_classext_t").GetByteSize()
           print(f"rb_classext_t is {rval_size} bytes long", file=result)
    ```
   And we're done! If we run the `test` command inside an `lldb` session we should see the output "rb_classext_t is 125 bytes long".


[1]: TODO: The debugger passed to `__call__` is different to the one passed to `__init__` - and attempting to store one in an ivar and use it later doesn't work for me. This means I can't call super in the initialiser to setup the thread variables, and have them exist and work by the time the function is called.
       
