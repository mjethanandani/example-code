import libyang as ly

def load_yang_module(module_name, module_filepath):
    ctx = ly.Context('/Users/mahesh/git/arrcus/arrcus_sw/build/ned/packages/arcos-5.2.1-EFT2-nc-1.6/src/yang')

    try:
        module = ctx.load_module(module_name)
        if module is None:
            print(f"Failed to load the module '{module_name}'")
        else:
            print(f"Module '{module_name}' loaded successfully!")
    except Exception as e:
        print(f"Failed to load the module '{module_name}': {e}")

module_name = "ietf-interfaces"
module_filepath = "ietf-interfaces.yang"

load_yang_module(module_name, module_filepath)
