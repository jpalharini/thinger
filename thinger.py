#! /usr/bin/env python3
import copy
import json
import logging
import sys
import os
import subprocess
import urllib.parse

# Configuring logging
logFormat = logging.Formatter('[Thinger] %(levelname)s - %(message)s')
rootLogger = logging.getLogger()

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(logFormat)

rootLogger.addHandler(stdoutHandler)

rootLogger.setLevel(logging.DEBUG)

BASE_PROJ_DICT = {"type": "project", "attributes": {"title": "", "items": []}}
BASE_TODO_DICT = {"type": "to-do", "attributes": {"title": ""}}

def create_project(title):
    proj = copy.deepcopy(BASE_PROJ_DICT)
    proj["attributes"]["title"] = title
    return proj

def create_todo(title):
    todo = copy.deepcopy(BASE_TODO_DICT)
    todo["attributes"]["title"] = title
    return todo

def create_todo_in_new_project(title, proj):
    proj["attributes"]["items"].extend(create_todo(title))
    return proj

def create_todo_with_notes(title, notes):
    todo = create_todo(title)
    todo["attributes"]["notes"] = notes

def add_todo_to_project(todo, proj):
    proj["attributes"]["items"].append(todo)

def add_note_to_todo(todo, notes):
    if "notes" in todo["attributes"]:
        notes = "\n" + notes
        todo["attributes"]["notes"] += notes
    else:
        todo["attributes"]["notes"] = notes
    return todo

def parse_list(filename):
    is_proj = False
    is_todo = False
    line_count = 0
    with open(filename, 'r') as fd:
        line = fd.readline()
        while line:
            line_count += 1
            if line_count == 1 and line.startswith('proj '):
                proj_title = line[5:].rstrip()
                rootLogger.debug("Creating project '" + proj_title + "'...")
                is_proj = True
                proj = create_project(proj_title)
            elif is_todo and line.startswith(' '):
                todo_note = line[2:].rstrip()
                rootLogger.debug("Adding note '" + todo_note + "' to to-do")
                todo = add_note_to_todo(todo, todo_note)
            else:
                if is_proj and is_todo:
                    rootLogger.debug("Adding todo " + json.dumps(todo) + " to project " + proj["attributes"]["title"])
                    add_todo_to_project(todo, proj)
                is_todo = False
                if line.startswith('- '):
                    todo_title = line[2:].rstrip()
                    rootLogger.debug("Creating todo '" + todo_title +"'...")
                    is_todo = True
                    todo = create_todo(todo_title)
                    rootLogger.debug("Todo created: " + json.dumps(todo))
            line = fd.readline()
    if is_proj:
        return proj
    else:
        return todo

if sys.argv[1]:
    if os.path.isfile(sys.argv[1]):
        proj = parse_list(sys.argv[1])
        rootLogger.debug("JSON: " + json.dumps(proj))
        encoded_data = urllib.parse.quote(json.dumps(proj))
        url = "things:///json?data=%5B{}%5D&auth-token={}".format(encoded_data, os.environ['THINGS_KEY'])
        # print(url)
        subprocess.Popen(['open', url])
    else:
        rootLogger.error("The argument provided is not a file.")
else:
    rootLogger.error("No file provided")
