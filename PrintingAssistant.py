### Wishlist:
# Different types of supports, or maybe just a 'breakable platform' at the top
# Is there some magical way to detect if there's any geo below it and move the base around it?

import maya.mel as mel
import maya.cmds as mc
import math
import re

try:
    mel.eval("source \"createAndAssignShader.mel\";")
except:
    pass

def PH_RotateShape(Axis):
    SelObjs = mc.ls(sl=True)

    for o in SelObjs:
        mc.select(cl=True)

        ###first, select the shape for the picked object(s)
        TheShapeArray = mc.listRelatives(o, c=True, s=True)
        for TheShape in TheShapeArray:
            mc.select(TheShape + ".cv[0:999999]", add=True)

        if Axis == "X":
            mc.rotate(90, 0, 0)

        if Axis == "Y":
            mc.rotate(0, 90, 0)

        if Axis == "Z":
            mc.rotate(0, 0, 90)

    mc.select(SelObjs)

def PH_MakeBarbell(RotateAmount=(0,0,0)):  ##used for the shoulder rotator
    TheObj = mc.curve(n="BarbellCurve", d=1, p=((0,2.738649,-18.166659),(0.846289,2.60461,-18.158651),(1.609738,2.215614,-18.166659),(2.215614,1.609738,-18.158651),(2.604611,0.846289,-18.158651),(2.738648,0,-18.166659),(2.604609,-0.846289,-18.166659),(2.215613,-1.609737,-18.158651),(1.609737,-2.215613,-18.166659),(0.846289,-2.604609,-18.166659),(-8.16181e-008,-2.738648,-18.166659),(-0.846289,-2.604609,-18.166659),(-1.609737,-2.215613,-18.166659),(-2.215613,-1.609737,-18.166659),(-2.604609,-0.846289,-18.166659),(-2.738648,0,-18.166659),(-2.604609,0.846289,-18.166659),(-2.215613,1.609737,-18.166659),(-1.609737,2.215613,-18.166659),(-0.846289,2.60461,-18.166659),(0,2.738649,-18.166659),(0,0,-18.166659),(2.738648,0,-18.166659),(-2.738648,0,-18.166659),(0,0,-18.166659),(-8.16181e-008,-2.738648,-18.158651),(0,0,-18.166659),(0,0,21.08801),(-8.16181e-008,-2.738648,21.08801),(-0.846289,-2.604609,21.08801),(-1.609737,-2.215613,21.08801),(-2.215613,-1.609737,21.08801),(-2.604609,-0.846289,21.08801),(-2.738648,0,21.08801),(-2.604609,0.846289,21.08801),(-2.215613,1.609737,21.08801),(-1.609737,2.215613,21.08801),(-0.846289,2.60461,21.08801),(0,2.738649,21.08801),(0.846289,2.60461,21.08801),(1.609738,2.215614,21.08801),(2.215614,1.609738,21.08801),(2.604611,0.846289,21.08801),(2.738648,0,21.08801),(2.604609,-0.846289,21.08801),(2.215613,-1.609737,21.08801),(1.609737,-2.215613,21.08801),(0.846289,-2.604609,21.08801),(-8.16181e-008,-2.738648,21.08801),(0,0,21.08801),(2.738648,0,21.08801),(-2.738648,0,21.08801),(0,0,21.08801),(0,2.738649,21.08801),(0,0,21.08801)), k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54))
    if RotateAmount != (0,0,0):
        mc.setAttr (TheObj+".rx",RotateAmount[0])
        mc.setAttr (TheObj+".ry",RotateAmount[1])
        mc.setAttr (TheObj+".rz",RotateAmount[2])
        mc.makeIdentity(TheObj,apply=True,t=1,r=1,s=1,n=0)


def ReplaceCircleWithBarbell():
    SelObjs=mc.ls(sl=True)
    NewTransforms = []

    for TheControl in SelObjs:
        TheControlShape=mc.listRelatives(TheControl,s=True)[0]
        if mc.nodeType( TheControlShape ) == "nurbsCurve":
            PH_MakeBarbell()
            NewObj = "BarbellCurve"
            ####now replace the circle with this object
            PH_ReplaceCurve(TheControl,NewObj,True)

    for o in NewTransforms:
        if mc.objExists(o):
            mc.delete(o) ### if any objects were imported, delete them here
    mc.select(SelObjs)


def PH_ReplaceCurve(OldObj, NewObj, RescaleCurve, ScaleOverride=1.0, MoveOverride=[0, 0, 0], DoThePos=True, DoTheRot=True, DoTheScale=True):
    ######################################################
    ##This function will replace one object's curve with another object's curve, then delete the 2nd object. It will also optionally resize the curve to fit the new obj
    ##
    ## Current limitations: donor curve must be at 0,0,0.   Rotation is not currently supported
    #######################################################
    TheOldBBox = mc.exactWorldBoundingBox(OldObj)
    TheNewBBox = mc.exactWorldBoundingBox(NewObj)

    if RescaleCurve == True:
        ##now lets rescale the new obj to match the old object's size. In case the obj has a child we'll have to copy it first, and get its copy's size (bad maya. no cookie)
        TargetObjShape = mc.listRelatives(OldObj, c=True, s=True)[0]
        TempCurve = mc.duplicateCurve(TargetObjShape, l=True)

        TheTempBBox = mc.exactWorldBoundingBox(TempCurve)

        mc.delete(TempCurve[0])

        TheNewXSize = (TheNewBBox[3] - TheNewBBox[0])
        TheOldXSize = (TheTempBBox[3] - TheTempBBox[0])

        TheNewYSize = (TheNewBBox[4] - TheNewBBox[1])
        TheOldYSize = (TheTempBBox[4] - TheTempBBox[1])

        TheNewZSize = (TheNewBBox[5] - TheNewBBox[2])
        TheOldZSize = (TheTempBBox[5] - TheTempBBox[2])

        if (TheOldXSize >= TheOldYSize) and (TheOldXSize >= TheOldZSize):
            TheOldAxis = "X"
            TheOldSize = TheOldXSize
        if (TheOldYSize >= TheOldXSize) and (TheOldYSize >= TheOldZSize):
            TheOldAxis = "Y"
            TheOldSize = TheOldYSize
        if (TheOldZSize >= TheOldXSize) and (TheOldZSize >= TheOldYSize):
            TheOldAxis = "Z"
            TheOldSize = TheOldZSize

        if (TheNewXSize >= TheNewYSize) and (TheNewXSize >= TheNewZSize):
            TheNewAxis = "X"
            TheNewSize = TheNewXSize
        if (TheNewYSize >= TheNewXSize) and (TheNewYSize >= TheNewZSize):
            TheNewAxis = "Y"
            TheNewSize = TheNewYSize
        if (TheNewZSize >= TheNewXSize) and (TheNewZSize >= TheNewYSize):
            TheNewAxis = "Z"
            TheNewSize = TheNewZSize

        if TheOldAxis == "X":
            if TheNewAxis == "Z":
                mc.rotate(90, 0, 0, NewObj, r=True)

        if TheOldAxis == "Y":
            if TheNewAxis == "Z":
                mc.rotate(-90, 0, 0, NewObj, r=True)
            if TheNewAxis == "X":
                mc.rotate(90, 180, 0, NewObj, r=True)

        if TheOldAxis == "Z":
            if TheNewAxis == "Z":
                mc.rotate(0, 180, 0, NewObj, r=True)
            if TheNewAxis == "X":
                mc.rotate(0, 180, 0, NewObj, r=True)

        TheDiff = (TheOldSize / TheNewSize) * ScaleOverride

        mc.scale(TheDiff, TheDiff, TheDiff, NewObj, relative=True)

    ##move the New obj to overlap with the Old. Maya's PH_Align commmand sucks since it screws up if an object has a child, so i wrote my own.
    # ~ PH_AlignToCenter(NewObj,OldObj)
    # ~ PH_AlignToCenter(NewObj,OldObj)
    # ~ PH_AlignToCenter(NewObj,OldObj)
    # ~ mc.move(MoveOverride[0],MoveOverride[1],MoveOverride[2],NewObj,r=True)
    PH_Align(OldObj, NewObj, DoPos=DoThePos, DoRot=DoTheRot, DoScale=DoTheScale)

    ##now we're going to parent the new shape to the old one, then reset its transforms. We parent it in case the goal obj we're replacing has children...if we diedn't maya would stick the obj in the wrong place because of the f'd up way it handles parenting. bad maya. no cookie again.
    mc.parent(NewObj, OldObj)

    mc.makeIdentity(NewObj, apply=True, t=1, r=1, s=1, n=0)

    ##now we need to delete OldObj's shape
    TheChildrenArray = []
    TheChildrenArray = mc.listRelatives(OldObj, c=True)
    if len(TheChildrenArray) != 0:
        for c in TheChildrenArray:
            childType = mc.nodeType(c)
            if childType == "nurbsCurve":
                OldShapeName = c
                mc.delete(c)

    ##now we need to get the name of the new shape, and parent it to the new transform
    TheChildrenArray = []
    TheChildrenArray = mc.listRelatives(NewObj, c=True)
    if len(TheChildrenArray) != 0:
        for c in TheChildrenArray:
            childType = mc.nodeType(c)
            if childType == "nurbsCurve":
                NewCurve = c
                mc.parent(NewCurve, OldObj, s=True, r=True)
                mc.rename(c, (OldObj + "Shape"))

    mc.delete(NewObj)


def PH_Align(src, tgt, SetKey=False, pivotOnly=False, DoPos=True, DoRot=True, DoScale=True):  ###originally based on zooPH_AlignFast
    RotOrderStrings = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]

    ####these two lines check to make sure the objects to be PH_Aligned are both transform (or joint) nodes, otherwise, it quits
    if ((not mc.objExists(src)) or (not mc.objExists(src))): return
    if ((not mc.objExists(src + ".t")) or (not mc.objExists(src + ".t"))): return

    pos = mc.xform(src, q=True, ws=True, rp=True)
    rot = mc.xform(src, q=True, ws=True, ro=True)

    if pivotOnly:  ####just move the pivot (doesn't do rotation)
        if DoPos: mc.move(pos[0], pos[1], pos[2], (tgt + ".rp"))
        if DoRot: mc.move(pos[0], pos[1], pos[2], (tgt + ".sp"))

    else:
        ###so if the rotation orders are different, we need to deal with that because the xform cmd doesn't
        if DoRot:
            src_OrignalRotOrder = mc.getAttr(src + ".ro")
            tgt_OrignalRotOrder = mc.getAttr(tgt + ".ro")
            if (src_OrignalRotOrder != tgt_OrignalRotOrder):  ###If they're not the same rotation order, make them the same temporarily
                mc.setAttr((tgt + ".ro"), src_OrignalRotOrder)

        if DoPos: mc.move(pos[0], pos[1], pos[2], tgt, a=True, ws=True, rpr=True)
        if DoRot: mc.rotate(rot[0], rot[1], rot[2], tgt, a=True, ws=True)

        ###now restore the original rotation order, while preserving the new position and rotation
        if DoRot:
            mc.xform(p=1, roo=RotOrderStrings[tgt_OrignalRotOrder])

    if SetKey:  ###set a key, if desired
        if DoPos: mc.setKeyframe(tgt, at="t")
        if DoRot: mc.setKeyframe(tgt, at="r")


def PH_GetNumCVs(Curve):
    NumSpans = mc.getAttr(Curve + ".spans")
    Degree = mc.getAttr(Curve + ".degree")
    Form = mc.getAttr(Curve + ".form")

    NumCVs = NumSpans + Degree
    if Form == 2:
        NumCVs -= Degree
    return NumCVs


def PH_WireDeformThisObj(ControlThickness=1, ChangeLastControlToBarbell=True):
    ErrorOut = False
    SelObjs = mc.ls(sl=True)

    if len(SelObjs) != 2:
        ErrorOut = True
    else:
        FoundGeo = False
        FoundNurbsCurve = False

        if mc.nodeType(mc.listRelatives(SelObjs[0], s=True)[0]) == "nurbsCurve":
            Curve = SelObjs[0]
            FoundNurbsCurve = True
        if mc.nodeType(mc.listRelatives(SelObjs[1], s=True)[0]) == "nurbsCurve":
            Curve = SelObjs[1]
            FoundNurbsCurve = True
        if mc.nodeType(mc.listRelatives(SelObjs[0], s=True)[0]) == "bezierCurve":
            Curve = SelObjs[0]
            FoundNurbsCurve = True
        if mc.nodeType(mc.listRelatives(SelObjs[1], s=True)[0]) == "bezierCurve":
            Curve = SelObjs[1]
            FoundNurbsCurve = True

        if mc.nodeType(mc.listRelatives(SelObjs[0], s=True)[0]) == "mesh":
            Geo = SelObjs[0]
            FoundGeo = True
        if mc.nodeType(mc.listRelatives(SelObjs[1], s=True)[0]) == "mesh":
            Geo = SelObjs[1]
            FoundGeo = True

        if mc.nodeType(mc.listRelatives(SelObjs[0], s=True)[0]) == "nurbsSurface":
            Geo = SelObjs[0]
            FoundGeo = True
        if mc.nodeType(mc.listRelatives(SelObjs[1], s=True)[0]) == "nurbsSurface":
            Geo = SelObjs[1]
            FoundGeo = True

        if not (FoundNurbsCurve and FoundGeo):
            ErrorOut = True

    if ErrorOut:
        mc.confirmDialog(m="Please select one nurbs curve and one mesh or nurbsSurface for this to work and try again.", button=["OK"],  title="3D Printing Assistant")
        return
    Controls = PH_ClusterAndMakeControls(Curve, ControlThickness=ControlThickness)
    if ChangeLastControlToBarbell:
        mc.select([Controls[0],Controls[2]])
        if mc.upAxis(q=True, axis=True) =="y":
            PH_RotateShape("X")
        mc.select([Controls[1],Controls[3],Controls[4]])
        ReplaceCircleWithBarbell()
    else:
        mc.select([Controls[0],Controls[2]],Controls[4])
        if mc.upAxis(q=True, axis=True) =="y":
            PH_RotateShape("X")
        mc.select([Controls[1],Controls[3]])
        ReplaceCircleWithBarbell()

    Wire = "Wire_" + Curve

    TheWire = mc.wire(Geo, w=Curve, n=Wire, dds=[0, 1000.0])[0]  ###maybe we should find some numeric reason for this size? Like the thickness of the geo or something?

def PH_ClusterAndMakeControls(Curve, FKStyleControlParenting=False, ObjToParentControlsTo="", PinCurveSoItCantMove=True, ControlThickness=10, MakeSelSet=False):
    mc.select(Curve)
    NumCVs = PH_GetNumCVs(Curve)

    ClusterHandles = []
    CVs = []
    Controls = []

    Before = mc.ls()

    mel.eval("ClusterCurve")

    After = mc.ls()

    NewObjs = list(set(After).difference(Before))  ###compare the before and after lists to find the cluster handles

    for o in NewObjs:  ### first find all the CVs
        if mc.objExists(o):
            if mc.nodeType(o) == "transform":
                CVs.append(o)
                # ~ ClusterHandles.append(CV)
    # ~ ### for some stupid reason, some curves cluster with random handles. we find the number of cvs and ignore any cluster handles with a highter number than that
    CVNums = []
    for CV in CVs:  #### sort all the CVs' current numbers since the lower the number the lower it is on the curve (but doesnt necessary start at 0. Gee, thanks Autodesk! #$@#$@#%)
        Start = CV.index("cluster") + 7
        End = CV.index("Handle")
        CVNum = int(CV[Start:End])
        CVNums.append(CVNum)
    CVNums.sort()
    n = 1
    for CVNum in CVNums:  #### now go through each CV and add the handles in the correct order, based on their number. limit it to only the correct number of total CVs
        if n <= NumCVs:
            for CV in CVs:
                Start = CV.index("cluster") + 7
                End = CV.index("Handle")
                ThisCVNum = int(CV[Start:End])
                if ThisCVNum == CVNum:
                    ClusterHandles.append(CV)
                    n += 1

    n = 1
    LastControl = ""
    for Handle in ClusterHandles:

        Control = mc.circle(r=ControlThickness, n=Curve.replace(":", "_") + "_" + str(n) + "_CNTRL")[0]  ### maybe we should find some numeric reason for this size? Like the thickness of the geo or something?
        mc.select(Control)

        PH_Align(Handle, Control)

        #### tag the object as a controller, with a parent

        if LastControl != "":
            mc.select(Control, LastControl)
            mel.eval("TagAsControllerParent;")

        ### should we parent each CV to its parent? If so, heres the place to do it
        if FKStyleControlParenting:
            if LastControl != "":
                mc.parent(Control, LastControl)
            else:
                if ObjToParentControlsTo != "":
                    mc.parent(Control, ObjToParentControlsTo)
        else:
            if ObjToParentControlsTo != "":
                mc.parent(Control, ObjToParentControlsTo)

        mc.makeIdentity(Control, apply=True, t=1, r=1, s=1)  ###0 out the handle
        mc.pointConstraint(Control, Handle, mo=True)

        mc.setAttr(Handle + ".t", lock=True)
        mc.setAttr(Handle + ".r", lock=True)
        # mc.setAttr(Handle + ".s", lock=True)
        mc.setAttr(Handle + ".v", 0)
        mc.setAttr(Handle + ".v", lock=True)

        # mc.setAttr(Control + ".s", lock=True)
        # mc.setAttr(Control + ".s", cb=False, k=False)
        mc.setAttr(Control + ".v", k=False)
        LastControl = Control
        Controls.append(Control)
        n += 1


    if PinCurveSoItCantMove:  ### we dont want double translating happening, so pin the curve using a parent constraint so it cant move, since its now being moved by clusters. dis there a better way to do this?
        if not mc.objExists("ClusterCurveConstrainer"):
            mc.select(cl=True)
            mc.group(n="ClusterCurveConstrainer", em=True)
            mc.parentConstraint("ClusterCurveConstrainer", Curve, mo=True)
            mc.setAttr("ClusterCurveConstrainer.v", False)  ### hide the group
            mc.setAttr("ClusterCurveConstrainer.v", lock=True)
    mc.select(Controls)

    SelSetName = "SELSET_TLTendril_" + Curve.replace(":", "_")  ### includes a whitespace override, remove for future projects
    if MakeSelSet:
        if mc.objExists(SelSetName):
            mc.delete(SelSetName)
        mc.sets(n=SelSetName)
    return Controls


def Slerp(FirstNum, LastNum, Percent):
    Diff = LastNum - FirstNum
    Num= FirstNum + (Diff * Percent)
    return Num

def PosArrayAsString(PosArray):
    UpAxis = mc.upAxis(q=True, axis=True)

    # return ("-p "+str(PosArray[0]) +" " + str(PosArray[1]) +" " + str(PosArray[2]) +" ")
    if UpAxis == "y":
        return ("-p 0 "+ str(PosArray[1]) +" 0")
    else:
        return ("-p 0 0 "+ str(PosArray[2]))

def CreateCylinderSupport(Name, Pos, Thickness=1, Height=10, BaseScale = 4, BaseWidth=1):
    UpAxis = mc.upAxis(q=True, axis=True)

    if UpAxis =="y":
        SupportMesh, SupportShape = mc.polyCylinder(n=Name, ch=True, o=True, ax=(0, 1, 0), r=Thickness, h=Height, sc=1, cuv=3)
    else:
        SupportMesh, SupportShape = mc.polyCylinder(n=Name, ch=True, o=True, ax=(0, 0, 1), r=Thickness, h=Height, sc=1, cuv=3)
    mc.setAttr(SupportShape + ".subdivisionsHeight", 8)
    mc.setAttr(SupportShape + ".subdivisionsAxis", 8)
    mc.setAttr(SupportMesh + ".tx", Pos[0])
    if UpAxis =="y":
        mc.setAttr(SupportMesh + ".ty", (.5 * Pos[1]))
        mc.setAttr(SupportMesh + ".tz", Pos[2])
    else:
        mc.setAttr(SupportMesh + ".ty", Pos[1])
        mc.setAttr(SupportMesh + ".tz", (.5 * Pos[2]) )
    mc.setAttr(SupportMesh + ".overrideEnabled", 1)
    mc.setAttr(SupportMesh + ".overrideColor", 4)

    #### the cylinder has a base thats a blend shape, as well as a blend shape top. Create them now.

    Dup = mc.duplicate(SupportMesh, rr=True)
    WideTop = mc.rename(Dup,"BS_WideTop")

    ScaleType = "-xz"
    if UpAxis =="z": ScaleType = "-xy"

    mel.eval("SelectToggleMode;  select -r "+SupportMesh+".vtx[64:71] "+SupportMesh+".vtx[73] ; scale -ocp "+ScaleType+" 0.0 0.0 0.0 ;  SelectToggleMode")


    Dup = mc.duplicate(SupportMesh, rr=True)
    WideBase = mc.rename(Dup,"BS_WideBase")



    mel.eval("SelectToggleMode;  select -r "+WideBase+".vtx[0:7] "+SupportMesh+".vtx[72] ; scale -ocp "+ScaleType+" " + str(BaseScale) +" " + str(BaseScale) +" " + str(BaseScale) +" " + ";  SelectToggleMode")
    mc.select([WideTop,WideBase,SupportMesh])
    BlendShapeModifier = mc.blendShape(automatic=True)[0]
    mc.delete([WideTop,WideBase])

    mc.addAttr(SupportMesh, ln="TopWidth", at="double", dv=0)
    mc.addAttr(SupportMesh, ln="BaseWidth", at="double", dv=0)
    mc.setAttr(SupportMesh+".TopWidth",cb=True,k=True)
    mc.setAttr(SupportMesh+".BaseWidth",cb=True,k=True)



    mc.connectAttr(SupportMesh+".TopWidth",BlendShapeModifier+".BS_WideTop")
    mc.connectAttr(SupportMesh+".BaseWidth",BlendShapeModifier+".BS_WideBase")

    mc.setAttr(SupportMesh+".BaseWidth",BaseWidth)


    mc.addAttr(SupportMesh, ln="Thickness", at="double", dv=0)
    mc.setAttr(SupportMesh+".Thickness",cb=True,k=True)
    mc.setAttr(SupportMesh+".Thickness",Thickness)
    mc.setAttr(SupportMesh+".TopWidth",.4)
    mc.connectAttr(SupportMesh+".Thickness",SupportShape+".radius")

    return SupportMesh

def PH_GetUniqueName(Name): ### if there's an object with this name already, get a new name where the number increments in a good spot
    if not mc.objExists(Name): return Name
    NameExists = True
    while NameExists:
        Name = PH_IncrementName(Name)
        if not mc.objExists(Name): return Name


def PH_IncrementName(Name):
    #### first scan through the name and see if there's any part thats digits, separated by underscores. If so, increment that
    FoundIt = False
    PartArray = Name.split("_")

    Index = 0
    for Part in PartArray:
        try:
            if Part == str(int(Part)).zfill(len(Part)):
                PartArray[Index] = str(int(Part)+1).zfill(len(Part))
                FoundIt = True
        except:
            pass
        finally:
            Index +=1
    if FoundIt:
        Index=0
        Name=""
        for Part in PartArray:
            if Index != 0: Name+="_"
            Name +=Part
            Index+=1
        return Name

    if not FoundIt: #### maybe the last few characters are the numbers? try that.
        try:
            LastDigit = int(Name[-1])
        except:
            return Name+"_1" #### if there's no number at the end, add one; we're done here.

        StillGoing = True
        DigitString = ""
        Num = -1
        while StillGoing:
            try:
                Temp  = str( int(Name[Num]) ) +DigitString
                DigitString  = str ( int(Name[Num]) ) +DigitString
                Num -= 1

            except:
                StillGoing = False

        NewDigits  = str(int(DigitString)+1).zfill(len(DigitString))
        Name = Name.replace(DigitString,NewDigits)
        return Name


def AssignShader(Objs, Shader = "Support_Shader", Color=[.3,.1,.1]):
    try:
        ShaderGroup = Shader + "SG"

        if not mc.objExists(Shader):
            mel.eval("shadingNode -asShader lambert -n " + Shader + ";")
            mel.eval("sets -renderable true -noSurfaceShader true -empty -name " + ShaderGroup + ";")
            mel.eval("connectAttr -f " + Shader + ".outColor " + ShaderGroup + ".surfaceShader;")
        for Obj in Objs:
            mel.eval("assignCreatedShader \"lambert\" \"\" " + Shader + " \"" + Obj + "\";")
            mel.eval("sets -e -forceElement " + ShaderGroup + ";")
            mc.setAttr(Shader + ".color", Color[0], Color[1], Color[2], type="double3")
    except:
        pass ### if Autodesk changes their function names at least the whole script wont crash...


def DoAddSupport(Pos, Thickness=1, BaseScale=2, ChangeLastControlToBarbell=True, BaseWidth=1):
    UpAxis = mc.upAxis(q=True, axis=True)

    OldRootTransforms = [o for o in mc.ls(typ="transform") if mc.listRelatives(o,p=True) == None]

    if UpAxis == "y":
        FloorPos = [Pos[0],0,Pos[2]]
        MidPoint1 = [Pos[0], Slerp(0,Pos[1],.25), Pos[2]]
        MidPoint2 = [Pos[0], Slerp(0,Pos[1],.5), Pos[2]]
        MidPoint3 = [Pos[0], Slerp(0,Pos[1],.75), Pos[2]]

    else:
        FloorPos = [Pos[0],Pos[1],0]
        MidPoint1 = [Pos[0], Pos[1], Slerp(0,Pos[2],.25)]
        MidPoint2 = [Pos[0], Pos[1], Slerp(0,Pos[2],.5)]
        MidPoint3 = [Pos[0], Pos[1], Slerp(0,Pos[2],.75)]

    if UpAxis =="y":
        Height = Pos[1]
    else:
        Height = Pos[2]
    SupportMesh = CreateCylinderSupport( PH_GetUniqueName("SupportMesh_1"), Pos, Thickness=Thickness, Height=Height, BaseScale=BaseScale, BaseWidth=BaseWidth)
    try:
        AssignShader([SupportMesh])
    except:
        pass
    OldTransforms = mc.ls(typ="transform", l=True)
    OldNurbsCurves = mc.ls(typ="nurbsCurve",l=True)
    CurveCmd = "curve -n \""+ PH_GetUniqueName("SupportCurve_1") + "\" -d 4 " + PosArrayAsString(FloorPos) + PosArrayAsString(MidPoint1) + PosArrayAsString(MidPoint2) + PosArrayAsString(MidPoint3) + PosArrayAsString(Pos) +"-k 0 -k 0 -k 0 -k 0 -k 1 -k 1 -k 1 -k 1;"
    mel.eval(CurveCmd)

    SupportCurve = [o for o in mc.ls(typ="transform", l=True) if o not in OldTransforms][0].split("|")[-1]
    NewNurbsCurve = [Curve for Curve in mc.ls(typ="nurbsCurve", l=True) if Curve not in OldNurbsCurves][0]
    mc.rename(NewNurbsCurve,SupportCurve+"Shape")
    if UpAxis == "y":
        mc.setAttr(SupportCurve+".tx", Pos[0])
        mc.setAttr(SupportCurve+".tz", Pos[2])
    else:
        mc.setAttr(SupportCurve+".tx", Pos[0])
        mc.setAttr(SupportCurve+".ty", Pos[1])

    mc.select([SupportMesh, SupportCurve])
    OldControls = mc.ls("*CNTRL")
    OldCurves = mc.ls(typ="nurbsCurve")
    OldTransforms = mc.ls(typ="transform")


    PH_WireDeformThisObj(ControlThickness=Thickness*1.4, ChangeLastControlToBarbell=ChangeLastControlToBarbell)
    Controls = [Obj for Obj in mc.ls("*CNTRL") if Obj not in OldControls]
    for o in (mc.ls(typ="nurbsCurve") + mc.ls(typ="transform") ):
        if o not in OldCurves and o not in OldTransforms:
            if o.startswith("SupportCurve") and o.count("CNTRL")==0:
                try:
                    mc.setAttr(o+".visibility",False)
                    mc.setAttr(o+".visibility",lock=True)
                except:
                    pass


    ### set parenting for controls. There's a group system to divorce scale from pos\rot
    ParenterGrps = []
    for Control in Controls:
        ParenterGrp ="ParenterGrp_"+Control
        mc.group(n=ParenterGrp, em=True)
        PH_Align(Control,ParenterGrp)
        if Control in  [Controls[0], Controls[2]]:
            ConnectWithPMAAndStaticNode(SupportMesh+".Thickness",Control+".sx",2)
            ConnectWithPMAAndStaticNode(SupportMesh+".Thickness",Control+".sy",2)
            ConnectWithPMAAndStaticNode(SupportMesh+".Thickness",Control+".sz",2)
        else:
            mc.connectAttr(SupportMesh+".Thickness",Control+".sx")
            mc.connectAttr(SupportMesh+".Thickness",Control+".sy")
            mc.connectAttr(SupportMesh+".Thickness",Control+".sz")
        mc.setAttr(Control+".sx", lock=True)
        mc.setAttr(Control+".sy", lock=True)
        mc.setAttr(Control+".sz", lock=True)
        ParenterGrps.append(ParenterGrp)


    mc.parent(Controls[4],ParenterGrps[2])
    mc.parent(Controls[3],ParenterGrps[2])
    mc.parent(Controls[1],ParenterGrps[0])

    mc.parentConstraint(Controls[0],ParenterGrps[0], mo=True)
    mc.parentConstraint(Controls[1],ParenterGrps[1], mo=True)
    mc.parentConstraint(Controls[2],ParenterGrps[2], mo=True)
    mc.parentConstraint(Controls[3],ParenterGrps[3], mo=True)


    NewRootTransforms = [o for o in mc.ls(typ="transform") if (mc.listRelatives(o,p=True) == None and o not in OldRootTransforms)]
    mc.select(NewRootTransforms)
    mc.group(n=SupportMesh+"_Grp")
    return SupportMesh

def MakeStaticNode(Value=5):
    StaticNode = "Static_"+str(Value)
    if not mc.objExists(StaticNode):
        StaticNode = mc.shadingNode("multiplyDivide", asUtility=True, n=StaticNode)
    mc.setAttr(StaticNode + ".input1X", Value)
    return StaticNode

def ConnectWithPMAAndStaticNode(FromAttr,ToAttr,Value):
    StaticNode = MakeStaticNode(Value)
    PMANode = mc.shadingNode("plusMinusAverage", asUtility=True)
    mc.connectAttr(FromAttr, PMANode+".input1D[0]")
    mc.connectAttr(StaticNode+".outputX", PMANode+".input1D[1]")
    mc.connectAttr(PMANode+".output1D", ToAttr)


def AddSupport():
    OldSel = mc.ls(sl=True)
    ComponentSelectionModeWasActive  = mc.selectMode( q=True, co=True )


    SoftSelectWasEnabled = mc.softSelect(q=True, softSelectEnabled=True)
    mc.softSelect(e=True, softSelectEnabled=False)

    UpAxis = mc.upAxis(q=True, axis=True)


    SupportMeshes=[]
    SelObjs= mc.ls(sl=True,fl=True)
    if len(SelObjs) ==0:
        mc.confirmDialog(m="No vertexes or objects selected! Select something to show where the support should be created at.", button=["Oops"], title="3D Printing Assistant 1.0")
        return

    BBox = mc.exactWorldBoundingBox()

    XDiff = BBox[3] - BBox[0]
    YDiff = BBox[4] - BBox[1]
    ZDiff = BBox[5] - BBox[2]
    YMax =max ([BBox[4],BBox[1]])
    ZMax =max ([BBox[5],BBox[2]])

    AvgX = (BBox[3] + BBox[0])/2.0
    AvgY = (BBox[4] + BBox[1])/2.0
    AvgZ = (BBox[5] + BBox[2])/2.0

    MinY = min(BBox[4],BBox[1])
    MinZ = min(BBox[5],BBox[2])

    if mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection", q=True, v=True):
        if UpAxis =="y":
            SquaredDiff = (XDiff * XDiff) + (ZDiff * ZDiff)
        else:
            SquaredDiff = (XDiff * XDiff) + (YDiff * YDiff)

        Hypot = math.sqrt(SquaredDiff)

        Radius =  Hypot / 2.0
        Thickness = max([ ConvertUnit(1), Radius])


    else:
        Thickness =  ConvertUnit( mc.floatField("UI_FloatField_Thickness", q=True, v=True) )

    if mc.checkBox("UI_CBox_Calculate_base_size_based_on_height_of_support", q=True, v=True):
        BaseScale = (max(Thickness + (YMax/20.0), 2) / (Thickness * .75) )
    else:
        BaseScale = ConvertUnit( mc.floatField("UI_FloatField_BaseSize", q=True, v=True) )

    if mc.checkBox("UI_CBox_Build_one_support_per_selected_object_or_vert",q=True,v=True):
        SelObjs = mc.ls(sl=True,fl=True)
        if len(SelObjs) > 20:
            TheResult = mc.confirmDialog(m="Really create "+str(len(SelObjs)) +" supports?", button=["Yes","Oops! No!"]  , title="3D Printing Assistant")
            if TheResult != "Yes": return

        for o in mc.ls(sl=True,fl=True):
            mc.select(o)
            SupportMeshes.append( DoAddSupport( mc.exactWorldBoundingBox(), Thickness=Thickness, BaseScale=BaseScale) )
    else:
        SupportMeshes.append(  DoAddSupport([AvgX,MinY,AvgZ], Thickness=Thickness, BaseScale=BaseScale) )
    mc.select(SupportMeshes)
    if not mc.objExists("Printing_Supports"):
        mc.createDisplayLayer(name="Printing_Supports", number=1, empty=True)

    for o in SupportMeshes:
        while o != None and o.count("_Grp") == 0:
            o = mc.listRelatives(o, p=True)
            if o != None: o = o[0]
        if o != None:
            if o.startswith("Support") and o.endswith("_Grp"):
                mc.editDisplayLayerMembers("Printing_Supports",o, noRecurse=True)
    mc.select(OldSel)
    if SoftSelectWasEnabled:  mc.softSelect(e=True, softSelectEnabled=True)
    if ComponentSelectionModeWasActive:
        mc.selectMode(co=True)
    else:
        mc.selectMode(o=True)


def ConnectVertsUsingASupport():
    OldSel = mc.ls(sl=True)
    ComponentSelectionModeWasActive  = mc.selectMode( q=True, co=True )

    SoftSelectWasEnabled = mc.softSelect(q=True, softSelectEnabled=True)
    mc.softSelect(e=True, softSelectEnabled=False)

    SelObjs = mc.ls(sl=True, fl=True)

    ### There are more than two verts selected. We'll use the first vert as a branch point and connect each of the other verts to this one.
    for n in range(0,len(SelObjs)):
        mc.select( [ SelObjs[0] , SelObjs[n] ])
        ConnectTwoVertsUsingASupport(Silent=True)

    mc.select(OldSel)
    if SoftSelectWasEnabled:  mc.softSelect(e=True, softSelectEnabled=True)
    if ComponentSelectionModeWasActive:
        mc.selectMode(co=True)
    else:
        mc.selectMode(o=True)


def ConnectTwoVertsUsingASupport(Silent=False):
    OldSel = mc.ls(sl=True)
    ComponentSelectionModeWasActive  = mc.selectMode( q=True, co=True )

    SoftSelectWasEnabled = mc.softSelect(q=True, softSelectEnabled=True)
    mc.softSelect(e=True, softSelectEnabled=False)
    SelObjs = mc.ls(sl=True, fl=True)
    if len(SelObjs) < 2:
        if not Silent:
            mc.confirmDialog(m="Select two verts and try again.", button=["Oops"],  title="3D Printing Assistant")
        return

    if len(SelObjs) > 2:
        ConnectVertsUsingASupport()
        return

    mc.select(SelObjs[0])
    FirstPos = mc.exactWorldBoundingBox()
    mc.select(SelObjs[1])
    SecondPos = mc.exactWorldBoundingBox()
    mc.select(SelObjs)
    UpAxis = mc.upAxis(q=True, axis=True)
    AxisNum=1
    if UpAxis == "z": AxisNum =2
    if FirstPos[AxisNum] > SecondPos[AxisNum]:
        FirstObj = SelObjs[1]
        SecondObj = SelObjs[0]
    else:
        FirstObj = SelObjs[0]
        SecondObj = SelObjs[1]


    BBox = mc.exactWorldBoundingBox()


    #### figure out the distance between the two verts.
    XDiff = BBox[3] - BBox[0]
    YDiff = BBox[4] - BBox[1]
    ZDiff = BBox[5] - BBox[2]

    SquaredDiff = (XDiff * XDiff) + (YDiff*YDiff) + (ZDiff * ZDiff)
    Hypot = math.sqrt(SquaredDiff)

    ### get the start pos
    mc.select(FirstObj)
    BBox = mc.exactWorldBoundingBox()

    StartLoc = mc.spaceLocator()[0]
    mc.setAttr(StartLoc+".tx",BBox[0])
    mc.setAttr(StartLoc+".ty",BBox[1])
    mc.setAttr(StartLoc+".tz",BBox[2])

    mc.select(SecondObj)
    BBox = mc.exactWorldBoundingBox()
    EndLoc = mc.spaceLocator()[0]
    mc.setAttr(EndLoc+".tx",BBox[0])
    mc.setAttr(EndLoc+".ty",BBox[1])
    mc.setAttr(EndLoc+".tz",BBox[2])
    if UpAxis == "y":
        mc.aimConstraint(EndLoc,StartLoc,aimVector=(0,1,0),upVector=(1,0,0))
    else:
        mc.aimConstraint(EndLoc,StartLoc,aimVector=(0,0,1),upVector=(1,0,0))


    #### create a support on the ground, at 0,0,0, Use 0 size base width and base height and the hypot amount as the height
    TempLoc = mc.spaceLocator()[0]
    if UpAxis == "y":
        mc.setAttr(TempLoc+".ty",Hypot)
    else:
        mc.setAttr(TempLoc+".tz",Hypot)

    mc.select(TempLoc)
    #### compute the positions where the controls ought to be, move (and rotate?) them as needed
    OldTransforms = mc.ls(typ="transform")
    if UpAxis == "y":
        SupportMesh = DoAddSupport([0,Hypot,0], Thickness=1, BaseScale=2, ChangeLastControlToBarbell=False, BaseWidth=-.75)
    else:
        SupportMesh = DoAddSupport([0,0,Hypot], Thickness=1, BaseScale=2, ChangeLastControlToBarbell=False, BaseWidth=-.75)
    mc.select(SupportMesh)
    mc.delete(TempLoc)


    Controls = [o for o in mc.ls(typ="transform") if (o.startswith("Support") and o not in OldTransforms and o.endswith("_CNTRL")) ]
    OldParent = mc.listRelatives(Controls[2],p=True)[0]
    PC = mc.parentConstraint(Controls[0],Controls[2],mo=True) ### temporarily parent like this
    PH_Align(StartLoc,Controls[0],DoScale=False)

    mc.delete(PC) ### parent it back how it was
    mc.parent(Controls[-1],OldParent) ### parent this to the group

    if not mc.objExists("Printing_Supports"):
        mc.createDisplayLayer(name="Printing_Supports", number=1, empty=True)


    for o in [SupportMesh]:
        while o != None and o.count("_Grp") == 0:
            o = mc.listRelatives(o, p=True)
            if o != None: o = o[0]
        if o != None:
            if o.startswith("Support") and o.endswith("_Grp"):
                mc.editDisplayLayerMembers("Printing_Supports",o, noRecurse=True)

    mc.delete(StartLoc)
    mc.delete(EndLoc)
    mel.eval("SelectToggleMode;")
    mc.select(OldSel)
    if SoftSelectWasEnabled:  mc.softSelect(e=True, softSelectEnabled=True)
    if ComponentSelectionModeWasActive:
        mc.selectMode(co=True)
    else:
        mc.selectMode(o=True)

def RemoveSupport():
    SupportWasDeleted=False
    SelObjs = mc.ls(sl=True)
    if SelObjs != None and SelObjs != []:
        SelObjs = [o.split("[")[0].split(".")[0] for o in SelObjs]

    if len(SelObjs) ==0:
        mc.confirmDialog(m="No supports selected.",button="Oops",  title="3D Printing Assistant")
        return

    for o in SelObjs:
        if mc.objExists(o):
            if o.startswith("FinalSupportMesh"):
                mc.delete(o)
                SupportWasDeleted = True
            else:
                while o != None and o.count("_Grp")==0:
                    o = mc.listRelatives(o,p=True)
                    if o !=None: o = o[0]
                if o !=None:
                    if o.startswith("Support") and o.endswith("_Grp"):
                        SupportWasDeleted = True
                        mc.delete(o)
    if not SupportWasDeleted:
        mc.confirmDialog(m="No supports selected.",button="Oops",  title="3D Printing Assistant")
        return



def CombineSupportsAndDeleteRigs():
    SupportGroups=[]
    SupportMeshes=[]
    for o in mc.ls(sl=True):
        if o.startswith("Support"):
            while o != None and o.count("_Grp") == 0:
                o = mc.listRelatives(o, p=True)
                if o != None: o = o[0]
            if o != None:
                if o.startswith("Support") and o.endswith("_Grp"):
                    SupportMesh = [Obj for Obj in mc.listRelatives(o,c=True) if Obj.count("Mesh")][0]
                    if SupportMesh not in SupportMeshes: SupportMeshes.append(SupportMesh)
                    if o not in SupportGroups: SupportGroups.append(o)
        else:
            if o.startswith("FinalSupportMesh"):
                if o not in SupportMeshes: SupportMeshes.append(o)

    if SupportMeshes == []:
        mc.confirmDialog(m="No support meshes picked! Please pick at least 1 support mesh and try again.",button=["Oops"],  title="3D Printing Assistant")
        return


    if len(SupportMeshes) == 1:
        ResultingMesh = mc.duplicate(SupportMeshes[0], n="FinalSupportMesh_1")[0]
        mc.parent(ResultingMesh,w=True)
        mc.deleteAttr(ResultingMesh+".TopWidth")
        mc.deleteAttr(ResultingMesh+".BaseWidth")
        mc.deleteAttr(ResultingMesh+".Thickness")
        SupportMeshes = [ResultingMesh]

    while len(SupportMeshes) >1:
        for o in SupportMeshes:
            FirstTwo = SupportMeshes[:2]
            if mc.optionMenu("UI_OMenu_BooleanMethod", q=True, v=True).count("Legacy"):
                ResultingMesh = mc.polyBoolOp(FirstTwo[0], FirstTwo[1], op=True, ch=False, useThresholds=True, preserveColor=False,n="FinalSupportMesh_1")
            else:
                ResultingMesh = mc.polyCBoolOp(FirstTwo[0], FirstTwo[1], op=True, ch=False, classification=2, preserveColor=False,n="FinalSupportMesh_1")

            SupportMeshes.append(ResultingMesh)
            SupportMeshes.remove(FirstTwo[0])
            SupportMeshes.remove(FirstTwo[1])

    if SupportGroups !=[]: mc.delete(SupportGroups)
    try:
        mc.editDisplayLayerMembers("Printing_Supports", ResultingMesh, noRecurse=True)
    except:
        pass

def BuildOneSupportPer_Changed():
    BuildOnePer = mc.checkBox("UI_CBox_Build_one_support_per_selected_object_or_vert",q=True,v=True)
    if BuildOnePer:
        mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection",e=True,v=False)
        mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection",e=True, vis=False)
        mc.text("UI_Txt_Thickness__Group", e=True, vis=True)
        mc.floatField("UI_FloatField_Thickness", e=True, vis=True)

    else:
        mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection",e=True, vis=True)
        mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection",e=True, v=True)
        ComputeThickness_Changed()



def ComputeThickness_Changed():
    ComputeIt = mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection", q=True, v=True)
    if ComputeIt:
        mc.text("UI_Txt_Thickness__Group", e=True, vis=False)
        mc.floatField("UI_FloatField_Thickness", e=True, vis=False)
    else:
        mc.text("UI_Txt_Thickness__Group", e=True, vis=True)
        mc.floatField("UI_FloatField_Thickness", e=True, vis=True)


def CalcBaseSize_Changed():
    ComputeIt = mc.checkBox("UI_CBox_Calculate_base_size_based_on_height_of_support", q=True, v=True)
    if ComputeIt:
        mc.text("UI_Txt_Base_Size__Group", e=True, vis=False)
        mc.floatField("UI_FloatField_BaseSize", e=True, vis=False)
    else:
        mc.text("UI_Txt_Base_Size__Group", e=True, vis=True)
        mc.floatField("UI_FloatField_BaseSize", e=True, vis=True)

def DisplayWebsite():
    mc.launch(web="http://www.filmworksfx.com")

def Donate():
    mc.launch(web="https://www.paypal.me/mranim8or")

def Display_ContactUs():
    mc.confirmDialog(m="3D Printing Assistant was written by Michael McReynolds at Filmworks FX in Los Angeles, CA.\n\nEmail me at mranim8or@aol.com for questions and feature suggestions.\n\nTo support further development of this tool, please send donations via paypal to https://www.paypal.me/mranim8or", button="OK", title="3D Printing Assistant")

def Display_About():
    Msg = "3D Printing Assistant was written by Michael McReynolds at Filmworks FX in Los Angeles, CA.\n\nEmail me at mranim8or@aol.com for questions and feature suggestions.\n\nTo support further development of this tool, please send donations via paypal to https://www.paypal.me/mranim8or\n"
    Msg += "\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
    mc.confirmDialog(m=Msg, button="OK", title="3D Printing Assistant")


def ConvertUnit(Value, Reverse=False):
    if Reverse:
        String = (mc.convertUnit(Value, fromUnit=mc.currentUnit(q=True, linear=True), toUnit='cm')    )
    else:
        String = ( mc.convertUnit(Value, fromUnit='cm', toUnit=mc.currentUnit(q=True,linear=True)) )
    return float(re.sub('[^0-99999.]+', '', String) )

def ExportSTL():
    ExportSupportsSeparately = mc.checkBox("UI_CBox_Export_supports_separately",q=True,v=True)

    try:
        mc.loadPlugin('stlTranslator')
    except:
        pass

    FileTypes="STL Files (*.stl)"
    try:
        STLFile=mc.fileDialog2(cap="Export STL File",fileFilter=FileTypes,ds=1,fm=0)[0]
    except:
        return
    if STLFile == "" or STLFile == None: return

    STLFilesExported = []
    if ExportSupportsSeparately:
        MeshSTLFile = STLFile
        SupportSTLFile = STLFile.replace(".","_Supports.")

        ### select all meshes
        MeshesAndSupports = [mc.listRelatives(Shape, p=True)[0] for Shape in mc.ls(type="mesh")]
        Supports = [o for o in MeshesAndSupports if (o.startswith("SupportMesh_") or o.startswith("FinalSupportMesh_"))]
        Meshes = [o for o in MeshesAndSupports if o not in Supports]

        mc.select(Meshes)
        mc.file(MeshSTLFile, force=True, options="Binary=1", typ="STLExport",pr=True , es=True)
        STLFilesExported.append(MeshSTLFile)

        mc.select(Supports)
        mc.file(SupportSTLFile, force=True, options="Binary=1", typ="STLExport",pr=True , es=True)
        STLFilesExported.append(SupportSTLFile)

    else:
        ### select all meshes
        Meshes = [mc.listRelatives(Shape, p=True)[0] for Shape in mc.ls(type="mesh")]
        mc.select(Meshes)
        mc.file(STLFile, force=True, options="Binary=1", typ="STLExport", pr=True, es=True)
        STLFilesExported.append(STLFile)


    if mc.checkBox("UI_CBox_Rotate_to_be_Z_Up",q=True,v=True):
        UpAxis = mc.upAxis(q=True, axis=True)
        if UpAxis != "z": ### uh oh, axis is incorrect. we will fix by re-importing our exported stl, rotating it, then re-exporting it
            for STLFile in STLFilesExported:
                OldTrans = mc.ls(typ="transform")
                mc.file(STLFile, i=True, type="STLImport", ignoreVersion=True, mergeNamespacesOnClash=False , rpr="ImportedSTL")
                Trans = [Trans for Trans in mc.ls(typ="transform") if Trans not in OldTrans][0]
                mc.select(Trans)
                mc.setAttr(Trans+".rx",90)
                mc.file(STLFile, force=True, options="Binary=1", typ="STLExport", pr=True, es=True)
                mc.delete(Trans)


def ImportPrintBed():
    UpAxis = mc.upAxis(q=True, axis=True)

    
    if not mc.objExists("Print_Bed"):
        mc.createDisplayLayer(name="Print_Bed", number=1, empty=True)




    if mc.objExists("Max_Build_Height"): mc.delete("Max_Build_Height")
    if mc.objExists("Max_Build_L"): mc.delete("Max_Build_L")
    if mc.objExists("Max_Build_R"): mc.delete("Max_Build_R")
    if mc.objExists("Build_Plate"): mc.delete("Build_Plate")

    Width = ConvertUnit( mc.floatField("UI_FloatField_Width",q=True,v=True))
    Depth = ConvertUnit(mc.floatField("UI_FloatField_Depth",q=True,v=True))
    Height = ConvertUnit(mc.floatField("UI_FloatField_Height",q=True,v=True))
    
    if UpAxis =="y":
        Axis = [0,1,0]
    else:
        Axis = [0,0,1]
    mc.nurbsPlane(n="Build_Plate", ch=True, o=True,po=0, ax=Axis, w=Width, lr=(Depth/Width))
    mc.nurbsSquare(n="Max_Build_Height", ch=True, o=True, nr=Axis, sl1=Width, sl2=Depth)
    if UpAxis == "y":
        mc.setAttr("Max_Build_Height"+".ty",Height)
    else:
        mc.setAttr("Max_Build_Height"+".tz",Height)
        mc.setAttr("Max_Build_Height"+".rz",90)


    mc.nurbsSquare(n="Max_Build_L", ch=True, o=True, nr=Axis, sl1=Height, sl2=Depth)
    mc.nurbsSquare(n="Max_Build_R", ch=True, o=True, nr=Axis, sl1=Height, sl2=Depth)

    if UpAxis == "y":
        mc.setAttr("Max_Build_L"+".tx",(Width/2.0))
        mc.setAttr("Max_Build_L"+".ty",(Height/2.0))
        mc.setAttr("Max_Build_L"+".rz",90)

        mc.setAttr("Max_Build_R"+".tx",-1*(Width/2.0))
        mc.setAttr("Max_Build_R"+".ty",(Height/2.0))
        mc.setAttr("Max_Build_R"+".rz",90)
    else:
        mc.setAttr("Max_Build_L" + ".tx", (Width / 2.0))
        mc.setAttr("Max_Build_L" + ".tz", (Height / 2.0))
        mc.setAttr("Max_Build_L" + ".ry", 90)

        mc.setAttr("Max_Build_R" + ".tx", -1 * (Width / 2.0))
        mc.setAttr("Max_Build_R" + ".tz", (Height / 2.0))
        mc.setAttr("Max_Build_R" + ".ry", 90)



    mc.parent("Max_Build_Height","Build_Plate")
    mc.parent("Max_Build_L","Build_Plate")
    mc.parent("Max_Build_R","Build_Plate")
    mel.eval("fitPanel -all;")

    BedParts = ["Max_Build_Height","Max_Build_L","Max_Build_R","Build_Plate"]

    for o in BedParts:
        mc.editDisplayLayerMembers("Print_Bed",o, noRecurse=True)
    mc.setAttr("{}.displayType".format("Print_Bed"), 2) # Change layer to reference.

def PrintingAssistant():
    if mc.window("UI_Wndw_Printing_Assistant",ex=True): mc.deleteUI("UI_Wndw_Printing_Assistant")
    mc.window("UI_Wndw_Printing_Assistant",w=491,h=467,title="3D Printing Assistant",menuBar=True)
    TheBase=mc.columnLayout()
    FormLayout_Printing_Assistant=mc.formLayout("FormLayout_Printing_Assistant")


    mc.setParent(TheBase)
    c=mc.frameLayout("UI_FrameLayout_Custom_Supports",cll=True,bv=True,w=491,bgc=(0.3,0.3,0.3),label="Custom Supports",ann="",cc="mc.window(\"UI_Wndw_Printing_Assistant\", e=True, h= mc.window(\"UI_Wndw_Printing_Assistant\", q=True, h=  True)-352   )")
    FormLayout_Custom_Supports = mc.formLayout("FormLayout_Custom_Supports")


    c=mc.button("UI_Btn_Add_Support",bgc=(0.0,1.68,0.0),label="Add Support",w=190,h=49,ann="",c="AddSupport()")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",15),((c,"top",6))])


    c=mc.checkBox("UI_CBox_Build_one_support_per_selected_object_or_vert",label="Build one support per selected object or vert",cc="BuildOneSupportPer_Changed()",ann="",v=True)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",216),((c,"top",8))])


    c=mc.checkBox("UI_CBox_Compute_thickness_based_on_size_of_selection",label="Compute thickness based on size of selection",cc="ComputeThickness_Changed()",ann="",v=True)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",216),((c,"top",28))])


    c=mc.checkBox("UI_CBox_Calculate_base_size_based_on_height_of_support",label="Calculate base size based on height of support",cc="CalcBaseSize_Changed()",ann="",v=True)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",216),((c,"top",48))])


    c=mc.floatField("UI_FloatField_Thickness",w=55,h=20,vis=False,ann="",v=1)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",96),((c,"top",62))])


    c=mc.text("UI_Txt_Thickness__Group",label="Thickness:")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",38),((c,"top",65))])


    c=mc.text("UI_Txt_After_creation__select_a_support_mesh_to_adjust_Group",label="After creation, select a support mesh to adjust")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",218),((c,"top",80))])


    c=mc.floatField("UI_FloatField_BaseSize",w=55,h=20,vis=False,ann="",v=2.5)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",96),((c,"top",86))])


    c=mc.text("UI_Txt_Base_Size__Group",label="Base Size:")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",38),((c,"top",89))])


    c=mc.text("UI_Txt_its_thickness_and_dimensions__Group",label="its thickness and dimensions.")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",218),((c,"top",96))])


    c=mc.separator("UI_Separator_RemoveSupport",w=491,h=3)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",0),((c,"top",113))])


    c=mc.button("UI_Btn_Connect_Two_Verts_Using_a_Support",bgc=(0.31,1.05,0.61),label="Connect Two Verts Using a Support",w=247,h=30,ann="",c="ConnectTwoVertsUsingASupport()")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",19),((c,"top",127))])


    c=mc.text("UI_Txt_Press_F8_and_select_2_verts_to_connect_Group",label="Press F8 and select 2 verts to connect")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",281),((c,"top",133))])


    c=mc.separator("UI_Separator_ConnectTwo",w=491,h=3)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",0),((c,"top",174))])


    c=mc.button("UI_Btn_Remove_Support",bgc=(1.68,0.0,0.0),label="Remove Support(s)",w=190,h=30,ann="",c="RemoveSupport()")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",15),((c,"top",195))])


    c=mc.separator("UI_Separator_Assistant",w=491,h=3)
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",0),((c,"top",243))])


    c=mc.button("UI_Btn_Combine_selected_supports_and_delete_rigs",bgc=(0.5,0.5,0.5),label="Combine selected supports and delete rigs",w=252,h=30,ann="",c="CombineSupportsAndDeleteRigs()")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",15),((c,"top",253))])


    c=mc.text("UI_Txt_Depends_on_the_slicer_if_this_is_needed__Group",label="Depends on the slicer if this is needed.")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",279),((c,"top",264))])


    c=mc.text("UI_Txt_This_relies_on_Maya_booleans__so_save_Group",label="This relies on Maya booleans, so save")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",279),((c,"top",280))])


    c=mc.text("UI_Txt_before_you_try_it__Group",label="before you try it.")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",279),((c,"top",296))])


    c=mc.optionMenu("UI_OMenu_BooleanMethod",label="",w=210,h=20,bgc=(0.39,0.39,0.39),ann="")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",63),((c,"top",312))])


    mc.menuItem("Legacy Algorithm (Recommended)")
    mc.menuItem("Current Algorithm")

    c=mc.text("UI_Txt_Method__Group",label="Method:")
    mc.formLayout(FormLayout_Custom_Supports,e=True,attachForm=[(c,"left",15),((c,"top",314))])


    mc.setParent(TheBase)
    c = mc.frameLayout("UI_FrameLayout_Misc_Tools", cll=True, bv=True, w=491, bgc=(0.3, 0.3, 0.3), label="Misc Tools", ann="", cc="mc.window(\"UI_Wndw_Printing_Assistant\", e=True, h= mc.window(\"UI_Wndw_Printing_Assistant\", q=True, h=  True)-121   )")
    FormLayout_Misc_Tools = mc.formLayout("FormLayout_Misc_Tools")

    c = mc.text("UI_Txt_Width__Group", label="Width:")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 148), ((c, "top", 24))])

    c = mc.text("UI_Txt_Height__Group", label="Height:")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 348), ((c, "top", 24))])

    c = mc.text("UI_Txt_Depth__Group", label="Depth:")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 245), ((c, "top", 24))])

    c = mc.floatField("UI_FloatField_Width", w=51, h=20, ann="",v=250, pre=1)
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 187), ((c, "top", 22))])

    c = mc.floatField("UI_FloatField_Height", w=51, h=20, ann="",v=210, pre=1)
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 389), ((c, "top", 22))])

    c = mc.floatField("UI_FloatField_Depth", w=51, h=20, ann="", v=210, pre=1)
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 283), ((c, "top", 22))])

    c = mc.button("UI_Btn_Import_Print_Bed", bgc=(0.32, 0.32, 0.32), label="Import Print Bed", w=110, h=30, ann="", c="ImportPrintBed()")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 33), ((c, "top", 22))])

    c = mc.button("UI_Btn_Export_STL", bgc=(0.32, 0.32, 0.32), label="Export STL", w=111, h=30, ann="", c ="ExportSTL()")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 33), ((c, "top", 60))])

    c = mc.checkBox("UI_CBox_Rotate_to_be_Z_Up", label="Rotate to be Z Up", ann="", v=True)
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 160), ((c, "top", 67))])

    c = mc.checkBox("UI_CBox_Export_supports_separately", label="Export supports separately", ann="Two STLs will be exported, one for the model and one for the supports. This way, In your slicer you can specify different infill and perimeter settings for the supports.")
    mc.formLayout(FormLayout_Misc_Tools, e=True, attachForm=[(c, "left", 283), ((c, "top", 67))])

    mc.showWindow()

    mc.window("UI_Wndw_Printing_Assistant", e=True,w= mc.window("UI_Wndw_Printing_Assistant",q=True,w=True)-1, h=5)

    mc.frameLayout("UI_FrameLayout_Custom_Supports",e=True,cl=False) ### close all rollouts
    mc.frameLayout("UI_FrameLayout_Misc_Tools",e=True,cl=True) ### close all rollouts


    mc.menu(label='Help', helpMenu=True)
    mc.menuItem('ContactUs', label='"Contact Us', c ="Display_ContactUs()")
    mc.menuItem('Website', label='"Website', c="DisplayWebsite()")
    mc.menuItem('DonateViaPaypal', label='"Donate Via Paypal', c="Donate()")
    mc.menuItem('About', label='"About', c="Display_About()")

    CalcBaseSize_Changed()
    ComputeThickness_Changed()
    BuildOneSupportPer_Changed()

PrintingAssistant()
