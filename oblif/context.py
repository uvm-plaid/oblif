from inspect import getframeinfo, stack

from .iterators import orange, ObliviousRange
from .values import apply_to_label, values_new
    
def print_ctx(*args):
    myfilename =  getframeinfo(stack()[0][0]).filename
    ix = 1
    while getframeinfo(stack()[ix][0]).filename == myfilename: ix+=1
    caller = getframeinfo(stack()[ix][0])
    print("["+caller.filename+":"+str(caller.lineno)+"]", *args)
  
def trytobool(val):
    try:
        return bool(val)
    except:
        return val
    
def boolneg(val):
    if val is True: return False
    if val is False: return True
    return 1-val

class Ctx:
    def __init__(self):
        self.vals = values_new()
        self.vals["__guard"] = 1
        self.contexts = {}

    def get(self, var):
#        print_ctx("calling get on", var, "with", self.vals)
        return self.vals[var]

    def set(self, var, val):
#        print_ctx("calling set", var, val, "with", self.vals)
        self.vals[var] = val
            
    def label(self, label):
#        print_ctx("entering label", label, "with context", self.vals)
        if self.vals: self.vals = apply_to_label(self.contexts, self.vals, True, label)
            
        if label in self.contexts:
#            print_ctx("executing code under guard", self.vals["__guard"])
            self.vals = self.contexts[label]
            del self.contexts[label]
            return True
        else:
#            print_ctx("no reason to execute code, skipping")
            return False
        
    def pjif(self, stack, label):
#        print_ctx("calling pjif, stack=", self.vals.dic["__stack"], "guard=", guard, "label=", label)
        self.vals["__stack"] = tuple(stack[:-1])
        guard = trytobool(stack[-1])
        self.vals = apply_to_label(self.contexts, self.vals, not guard if isinstance(guard,bool) else 1-guard, label)
            
    def pjit(self, stack, label):
#        print_ctx("calling pjit, stack=", self.vals.dic["__stack"], "guard=", guard, "label=", label)
        self.vals["__stack"] = tuple(stack[:-1])
        guard = trytobool(stack[-1])
        self.vals = apply_to_label(self.contexts, self.vals, guard, label)
        
    def stack(self, stack):
#        print("stacking", stack)
        self.vals["__stack"] = stack
        
    def unstack(self):
#        print("calling unstack", self.vals.dic["__stack"])
        ret = tuple(reversed(self.vals["__stack"]))
        del self.vals["__stack"]
        return ret
            
    def jmp(self, stack, label):
#        print("jmp", stack, label)
        self.vals["__stack"] = stack
        self.vals = apply_to_label(self.contexts, self.vals, True, label)

    def ret(self, arg, label): # same as jmp
        guard = self.vals["__guard"]
        self.vals.clear()
        self.vals["__guard"] = guard
        self.vals["__stack"] = (arg,)
        self.vals = apply_to_label(self.contexts, self.vals, True, label)
        
    def range(self, *args):
        return orange(self, *args)
            
    def foriter(self, arg, label):
        if isinstance(arg, ObliviousRange): arg.foriter(label)

        