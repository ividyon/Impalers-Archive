# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 01:33:31 2022

@author: Asterisk
"""
import xml.etree.ElementTree as ET
import markdown

from pathlib import Path

npcOverloads = {}

def loadNPCNames(root,lang="engUS"):
    path = str(root/(r"GR\data\INTERROOT_win64\msg\%s\NpcName_dlc01.fmg.xml"%(lang)))
    npcNames = loadTextFile(path)
    remapping = {}
    for ids in npcNames:
        if str(ids)[0] == "1":
            remapping[int(str(ids)[1:-1])] = npcNames[ids]
    for key in npcOverloads:
        remapping[key] = npcOverloads[key]
    return remapping

def parseNPCDialogue(path, npcNames = {},output = print):
    l_npc = 0
    l_section = 0
    data = loadTextFile(path)
    for identifier in data:
        step = identifier%1000
        section = (identifier//1000)%100
        npc = (identifier//100000)
        if npc != l_npc:
            if npc in npcNames:
                output("### %s [%04d]"%(npcNames[npc],npc))
            else:
                output("### %04d"%(npc))
            l_npc = npc
            l_section = -1
        if section != l_section:
            output("#### Section %02d"%section)
            l_section = section
        if data[identifier]:
            output("[%d] "%(identifier) + data[identifier]+"  ")
    return

def loadTextFile(path):
    tree = ET.parse(path)
    root = tree.getroot()
    textElements = list(list(root)[4])
    elements = {}
    for element in textElements:
        identifier = int(element.items()[0][1])
        text = element.text
        if "%null%" not in text:
            elements[identifier] = text
    return elements

def pairedTextFiles(path0,path1):
    merged = {}
    l,r = map(loadTextFile,[path0,path1])
    for key in l:
        if key in r:
            merged[key] = (l[key],r[key])
        else:
            merged[key] = (l[key],"")
    for key in r:
        if key not in merged:
            merged[key] = ("",r[key])
    return merged

def singleTextFiles(path):
    l = loadTextFile(path)
    m = {}
    for key in l:
        m[key] = ("",l[key])
    return m

def loadFromChunk(glob):
    knownPairs = {
        "TutorialTitle_dlc01":"TutorialBody_dlc01",
        "LoadingTitle_dlc01":"LoadingText_dlc01",
        "AccessoryName_dlc01":"AccessoryCaption_dlc01",
        "ArtsName_dlc01":"ArtsCaption_dlc01",
        "GemName_dlc01":"GemCaption_dlc01",
        "GoodsName_dlc01":"GoodsCaption_dlc01",
        "MagicName_dlc01":"MagicCaption_dlc01",
        "ProtectorName_dlc01":"ProtectorCaption_dlc01",
        "WeaponName_dlc01":"WeaponCaption_dlc01",
        "TutorialTitle_dlc02":"TutorialBody_dlc02",
        "LoadingTitle_dlc02":"LoadingText_dlc02",
        "AccessoryName_dlc02":"AccessoryCaption_dlc02",
        "ArtsName_dlc02":"ArtsCaption_dlc02",
        "GemName_dlc02":"GemCaption_dlc02",
        "GoodsName_dlc02":"GoodsCaption_dlc02",
        "MagicName_dlc02":"MagicCaption_dlc02",
        "ProtectorName_dlc02":"ProtectorCaption_dlc02",
        "WeaponName_dlc02":"WeaponCaption_dlc02",
    }
    knownPairs = {k+".fmg":t+".fmg" for k,t in knownPairs.items()}
    pairTargets = {knownPairs[p]:p for p in knownPairs}
    master = []
    duplicates = set()
    for file in glob:
        if "ToS" in file.stem:
            continue
        if file.stem in knownPairs:
            text = pairedTextFiles(str(file),
                                   str(file).replace(file.stem,
                                                     knownPairs[file.stem]))
        elif file.stem in pairTargets:
            continue
        else:
            text = singleTextFiles(str(file))
        master.append("\n\n## %s\n"%file.stem)
        if file.stem == "TalkMsg_dlc01.fmg":
            parseNPCDialogue(file, {},master.append)
        else:
            for key,(title,description) in text.items():
                if description in duplicates:
                    continue
                duplicates.add(description)
                if title:
                    master.append("\n### %s [%d]"%(title,key))
                    master.append(description)
                else:
                    master.append("[%d] %s\n"%(key,description))
    text = "\n".join(master)
    return text

def loadFromChunkDual(globEn, globJp):
    knownPairs = {"TutorialTitle_dlc01":"TutorialBody_dlc01",
                  "LoadingTitle_dlc01":"LoadingText_dlc01",
                  "AccessoryName_dlc01":"AccessoryCaption_dlc01",
                  "ArtsName_dlc01":"ArtsCaption_dlc01",
                  "GemName_dlc01":"GemCaption_dlc01",
                  "GoodsName_dlc01":"GoodsCaption_dlc01",
                  "MagicName_dlc01":"MagicCaption_dlc01",
                  "ProtectorName_dlc01":"ProtectorCaption_dlc01",
                  "WeaponName_dlc01":"WeaponCaption_dlc01",
                  }
    knownPairs = {k+".fmg":t+".fmg" for k,t in knownPairs.items()}
    pairTargets = {knownPairs[p]:p for p in knownPairs}
    master = []
    # npcIds = loadNPCNames(chunk)
    duplicates = set()
    for file in globEn:
        fileJp = globJp[globEn.index(file)]
        if "ToS" in file.stem:
            continue
        if file.stem in knownPairs:
            text = pairedTextFiles(str(file),
                                   str(file).replace(file.stem,
                                                     knownPairs[file.stem]))
            textJp = pairedTextFiles(str(fileJp),
                                     str(fileJp).replace(fileJp.stem,
                                                         knownPairs[fileJp.stem]))
        elif file.stem in pairTargets:
            continue
        else:
            text = singleTextFiles(str(file))
            textJp = singleTextFiles(str(fileJp))
        master.append("\n\n## %s\n"%file.stem)
        if file.stem == "TalkMsg_dlc01.fmg":
            parseNPCDialogue(file, {},master.append)
        else:
            for key,(title,description) in text.items():
                (jpTitle, jpDescription) = textJp.items()
                if description in duplicates:
                    continue
                duplicates.add(description)
                if title:
                    master.append("\n### %s | %s [%d]"%(title,jpTitle,key))
                    master.append(description)
                else:
                    master.append("[%d] %s | %s\n"%(key,description,jpDescription))
    text = "\n".join(master)
    return text

chunkEn = Path(r".\GameText")
chunkJp = Path(r".\GameTextJP")
globEn = chunkEn.rglob("*.xml")
globJp = chunkJp.rglob("*.xml")

text = loadFromChunk(globEn)
with open("Master.html","w",encoding = "utf8") as outf:
    outf.write(markdown.markdown(text))

text = loadFromChunk(globJp)
with open("MasterJP.html","w",encoding = "utf8") as outf:
    outf.write(markdown.markdown(text))

text = loadFromChunkDual(globEn, globJp)
with open("MasterDual.html","w",encoding = "utf8") as outf:
    outf.write(markdown.markdown(text))