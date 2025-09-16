#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union, Dict
import re
 
SSMLNode = Union["SSMLText", "SSMLTag"]
 
@dataclass
class SSMLTag:
    name: str
    attributes: Dict[str, str]
    children: List[SSMLNode]
 
    def __init__(self, name: str, attributes: Dict[str, str] = None, children: List[SSMLNode] = None):
        self.name = name.strip()
        self.attributes = attributes if attributes is not None else {}
        self.children = children if children is not None else []
 
    def __eq__(self, other):
        return (
            isinstance(other, SSMLTag)
            and self.name == other.name
            and self.attributes == other.attributes
            and self.children == other.children
        )
 
@dataclass
class SSMLText:
    text: str
 
    def __init__(self, text: str):
        self.text = text
 
    def __eq__(self, other):
        return isinstance(other, SSMLText) and self.text == other.text
 
 
def parse_attributes(tag_str: str) -> Dict[str, str]:
    if "'" in tag_str:
        raise Exception("Single-quoted attributes not allowed")
    attributes = {}
    tag_name = tag_str.strip().split()[0]
    attr_str = tag_str[len(tag_name):].strip()
    if not attr_str:
        return attributes
    # regex matches key="value"
    attr_regex = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
    matches = list(attr_regex.finditer(attr_str))
    covered_spans = set()
    for match in matches:
        start, end = match.span()
        covered_spans.update(range(start, end))
    for i, char in enumerate(attr_str):
        if not char.isspace() and i not in covered_spans:
            raise Exception("Malformed attribute")
    for match in matches:
        key, val = match.groups()
        attributes[key] = val
    return attributes
 
 
def parseSSML(ssml: str) -> SSMLNode:
    i = 0
    stack = []
    root = None
    seen_top_level = False
 
    while i < len(ssml):
        if ssml[i] == '<':
            j = ssml.find('>', i)
            if j == -1:
                raise Exception("Missing closing angle bracket")
            tag_content = ssml[i+1:j].strip()
            if tag_content.startswith('/'):
                closing_name = tag_content[1:].strip()
                if not stack:
                    raise Exception("Unmatched closing tag")
                top = stack.pop()
                if top.name != closing_name:
                    raise Exception("Mismatched closing tag")
                if stack:
                    stack[-1].children.append(top)
                else:
                    if root is not None:
                        raise Exception("Multiple top-level tags")
                    root = top
                    seen_top_level = True
                i = j + 1
            elif tag_content.endswith('/'):
                name = tag_content[:-1].strip().split()[0]
                attributes = parse_attributes(tag_content[:-1])
                if not stack:
                    raise Exception("Self-closing tag outside of root")
                stack[-1].children.append(SSMLTag(name, attributes, []))
                i = j + 1
            else:
                name = tag_content.split()[0]
                attributes = parse_attributes(tag_content)
                new_tag = SSMLTag(name, attributes, [])
                if not stack and seen_top_level:
                    raise Exception("Multiple top-level tags")
                stack.append(new_tag)
                i = j + 1
        else:
            j = ssml.find('<', i)
            if j == -1:
                j = len(ssml)
            text = ssml[i:j]
            if text.strip():
                if not stack:
                    raise Exception("Text outside root tag")
                stack[-1].children.append(SSMLText(unescapeXMLChars(text)))
            i = j
 
    if stack:
        raise Exception("Unclosed tags remaining")
    if root is None or root.name != "speak":
        raise Exception("Root tag must be <speak>")
    return root
 
 
def ssmlNodeToText(node: SSMLNode) -> str:
    if isinstance(node, SSMLText):
        return escapeXMLChars(node.text)
    elif isinstance(node, SSMLTag):
        attrs = ' '.join([f'{k}="{v}"' for k, v in node.attributes.items()])
        children = ''.join(ssmlNodeToText(child) for child in node.children)
        if not children and not attrs:
            return f"<{node.name}/>"
        elif not children:
            return f"<{node.name} {attrs}/>"
        return f"<{node.name} {attrs}>{children}</{node.name}>" if attrs else f"<{node.name}>{children}</{node.name}>"
    return ""
 
 
def unescapeXMLChars(text: str) -> str:
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
 
def escapeXMLChars(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")