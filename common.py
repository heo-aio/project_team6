from typing import Any, List, TypedDict

from langgraph.graph import StateGraph

class State(TypedDict):
    question:str 
    generation:str
    data:str 
    context:List[Any]

def get_state():
    return StateGraph(State)