"""Synthetic recorder unit tests; no materials model or physical evaluation."""
import torch
from capture_helpers import capture_method

def test_direct_forward_bypasses_hook_but_wrapper_captures_unchanged_result():
    class Toy(torch.nn.Module):
        def forward(self,x): return {'e':x+1}
        def predict(self,x): return self.forward(x)
    model=Toy();hooks=[];captured=[]
    model.register_forward_hook(lambda *args: hooks.append(True))
    capture_method(model,'forward',captured.append)
    result=model.predict(torch.tensor([2.]))
    assert hooks==[] and len(captured)==1
    assert captured[0] is result and result['e'].item()==3

def test_neighbor_wrapper_observes_actual_query_once_without_reordering():
    class ToyNeighbors:
        def __init__(self):self.calls=0
        def get_neighbor_list(self,**kwargs):
            self.calls+=1
            return ([2,0,1],[0,1,2])
    obj=ToyNeighbors();captured=[]
    capture_method(obj,'get_neighbor_list',captured.append)
    result=obj.get_neighbor_list(r=6)
    assert obj.calls==1 and len(captured)==1
    assert captured[0] is result and result==([2,0,1],[0,1,2])
