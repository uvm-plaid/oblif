from inspect import getframeinfo, stack

from .iterators import orange, ObliviousIterator, IteratorWrapper
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
#        vals0 = values_new()
#        vals0["__guard"] = 1
        self.contexts = {}

    def get(self, var):
#        print_ctx("calling get on", var, "with", self.vals)
        return self.vals[var]

    def set(self, val, var):
        print_ctx("calling set var=", var, "val=", val, "with", self.vals)
        self.vals[var] = val
            
    def label(self, label, nstack):
        print_ctx("entering label", label, "with context", self.vals)
            
        if label in self.contexts and self.contexts[label] is not None:
            print("executing code", self.contexts[label])
#            print_ctx("executing code under guard", self.vals["__guard"])
            self.vals = self.contexts[label]
            del self.contexts[label]
            if nstack:
                ret = tuple([self.vals["__stack"+str(i)] for i in range(nstack-1,-1,-1)])
                for i in range(nstack): del self.vals["__stack"+str(i)]
                return ret
            else:
                return True
        else:
            print_ctx("no reason to execute code, skipping")
            return False
    
    def pjif(self, stack, labelnext, labeljump):
        print_ctx("calling pjif, stack=", stack, "label=", labelnext, "/", labeljump, "guard", stack[-1])
        self.stack(stack[:-1])
        guard = trytobool(stack[-1])
        guari = not guard if isinstance(guard,bool) else 1-guard
        self.contexts[labelnext] = apply_to_label(self.contexts.get(labelnext), self.vals, guard)
        self.contexts[labeljump] = apply_to_label(self.contexts.get(labeljump), self.vals, guari)
        self.vals = None
            
    def pjit(self, stack, labelnext, labeljump):
        print_ctx("calling pjif, stack=", stack, "label=", labelnext, "/", labeljump, "guard", stack[-1])
        self.stack(stack[:-1])
        guard = trytobool(stack[-1])
        guari = not guard if isinstance(guard,bool) else 1-guard
        self.contexts[labelnext] = apply_to_label(self.contexts.get(labelnext), self.vals, guari)
        self.contexts[labeljump] = apply_to_label(self.contexts.get(labeljump), self.vals, guard)
        self.vals = None
        
    def stack(self, stack):
#        print("stacking", stack)
        for i in range(len(stack)): self.vals["__stack"+str(i)] = stack[i]
        
    def jmp(self, stack, label):
        print("jmp", stack, label)
        self.stack(stack)
        self.contexts[label] = apply_to_label(self.contexts.get(label), self.vals, True)
        self.vals = None

    def ret(self, arg, label): # same as jmp
        print("calling ret", arg, label)
        guard = self.vals["__guard"]
        self.vals.clear()
        self.vals["__guard"] = guard
        self.stack((arg,))
        self.contexts[label] = apply_to_label(self.contexts.get(label), self.vals, True)
        
    def retlabel(self, label):
        print("retlabel", label, self.contexts)
        return self.contexts[label]["__stack0"]
        
    def range(self, *args):
        return orange(*args)
    
    def getiter(self, it):
        return iter(it) if isinstance(it, ObliviousIterator) else IteratorWrapper(iter(it))
        