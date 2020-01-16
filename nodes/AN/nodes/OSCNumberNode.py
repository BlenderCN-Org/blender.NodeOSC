import bpy
from bpy.props import *
from collections import defaultdict
from animation_nodes.sockets.info import toIdName
from animation_nodes.base_types import AnimationNode

from ....utils.utils import *

dataByIdentifier = defaultdict(None)

class OSCNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OSCNumberNode"
    bl_label = "OSCNumber"
    bl_width_default = 160

    osc_address: bpy.props.StringProperty(name="Osc address", 
        default="/an/number", 
        update = AnimationNode.refresh)
    osc_type: bpy.props.StringProperty(
        name="Type", 
        default="fff")
    osc_index: bpy.props.StringProperty(
        name="Argument indices. Indicate in which order the arguments will be handled inside blender. Have to be in the format \'() or (0 [, 1, 2])\' with 0...n integers, separated by a comma, and inside two parantheses \'()\'. There should be no more indices than arriving arguments, otherwise the message will be ignored", 
        default="()",
        update = AnimationNode.refresh)
    osc_direction: bpy.props.EnumProperty(
        name = "RX/TX", 
        default = "INPUT", 
        items = dataNodeDirectionItems, 
        update = AnimationNode.refresh)
    data_path: bpy.props.StringProperty(
        name="data path", 
        default="")
    id: bpy.props.StringProperty(
        name="id", 
        default="")
    node_data_type: bpy.props.EnumProperty(
        name="NodeDataType", 
        default="SINGLE", 
        items = nodeDataTypeItems)
    node_type: bpy.props.IntProperty(
        name="NodeType", 
        default=1)

    createList: BoolProperty(name = "Create List", default = False,
        description = "Create a list of numbers",
        update = AnimationNode.refresh)

    def create(self):
        self.data_path = 'bpy.data.node_groups[\'' + self.nodeTree.name + '\'].nodes[\'' + self.name +'\']'
        if self.createList:
            self.node_data_type = "LIST"
            self.setValue([0] * 1)
        else:
            self.node_data_type = "SINGLE"
            self.setValue(0)
        
        if self.osc_direction == "OUTPUT":
            self.id = "value"
            if self.createList:
                self.newInput("Float List", "Numbers", "numbers")
            else:
                self.newInput("Float", "Number", "number")
                
        if self.osc_direction == "INPUT":
            self.id = "setValue"
            if self.createList:
                self.newOutput("Float List", "Numbers", "numbers")
            else:
                self.newOutput("Float", "Number", "number")                

    def draw(self, layout):
        layout.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")
        layout.prop(self, "osc_address", text = "")
        layout.prop(self, "osc_index", text = "")
        layout.prop(self, "osc_direction", text = "")

    def getExecutionCode(self, required):
        if self.osc_direction == "OUTPUT":
            if self.createList:
                yield "self.setValue(numbers)"
            else:
                yield "self.setValue(number)"                
        if self.osc_direction == "INPUT":
            if self.createList:
                yield "numbers = self.getValue()"
            else:
                yield "number = self.getValue()"

    def setValue(self, value):
        dataByIdentifier[self.identifier] = value

    def getValue(self):
        return dataByIdentifier.get(self.identifier)

    @property
    def value(self):
        return self.getValue()

    @value.setter
    def value(self, value):
        self.setValue(value)
