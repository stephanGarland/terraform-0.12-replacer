#!/usr/bin/env python
"""
Author:         Stephan Garland, stephan.marc.garland@gmail.com
Purpose:        Prepares files for terraform 0.12upgrade
Description:    Converts `count` in Terraform modules to `num`
                Shifts any variables into their own file
                Replaces all instances of `var.count` with `var.num`

License:
This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, 
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import glob
import os
import re
import sys
import typing

from pathlib import Path

COUNT_REPLACEMENT_WORD = "num"

# Count regex explanation
# Group 1: Lines beginning with "module", followed by 1+ of any character except
#          a linebreak, followed by 1+ linebreak
# Group 2: 1+ of any character
# Group 3: 1+ of a whitespace character with a positive lookahead of "count"
# Group 4: The word "count"
# Example:
#
# module "security-groups" {                                                                                <-- Group 1
#     source = "./path"                                                                                     <-- Group 2
#     literally_just_gibberish                                                                              <-- Group 2
#     count  = "${var.count}"                                                                        <-- Groups 3 and 4
# }

def rename_count_regex(f: typing.TextIO) -> None:
    count_regex = r"(^module.+\n+)([\S\s]+)(\s+(?=count))(count)"
    count_regex_sub = r"\1\2\3" + COUNT_REPLACEMENT_WORD
    count_var_regex = r"var\.count"
    count_var_regex_sub = "var." + COUNT_REPLACEMENT_WORD
    tf_file = f.read()
    repl_count = re.sub(count_regex, count_regex_sub, tf_file, 0, re.MULTILINE)
    repl_count_var = re.sub(count_var_regex, count_var_regex_sub, repl_count, 0, re.MULTILINE)
    f.seek(0)
    f.write(repl_count_var)
    f.truncate()

def strip_vars(f: typing.TextIO) -> list:
    tmp_lst = []
    i = 0
    count_var_regex = r"\bcount\b"
    count_var_regex_sub = COUNT_REPLACEMENT_WORD
    f.seek(0)
    try:
        for line in f.readlines():
            # Changes var.count, but not var.count_of_consul, for example
            repl_count_var = re.sub(count_var_regex, count_var_regex_sub, line, 0)
            tmp_lst.append(repl_count_var)
            if line.startswith(tuple(ignore)):
                # This assumes your .tf files have a contiguous block of variables
                tmp_lst.pop()
                break
        for line in "".join(tmp_lst).splitlines():
            if line.startswith("variable"):
                break
            while not line.startswith("variable"):
                i += 1
                break
        del tmp_lst[:i]
        # Remove trailing newline if it got pulled in
        if "".join(tmp_lst[-1:]).isspace():
            del tmp_lst[-1:]
        # And add a newline to the head for any existing entries
        if not "".join(tmp_lst[0]).isspace():
            tmp_lst.insert(0, "\n")
    except IndexError:
        print("INFO: No variables found in " + f.name)
    return tmp_lst

def write_var_file(f: typing.TextIO, var_lst: list) -> None:
    with open(os.path.dirname(os.path.realpath(f.name)) + "/variables.tf", "a+") as var_file:
        var_file.write("".join(var_lst))

def rename_count_regex_in_var_file(f: typing.TextIO) -> None:
    with open(os.path.dirname(os.path.realpath(f.name)) + "/variables.tf", "r+") as var_file:
        tmp_file = var_file.read()
        count_var_regex = r"variable \"count\""
        count_var_regex_sub = "variable \"" + COUNT_REPLACEMENT_WORD + "\""
        repl_count_var = re.sub(count_var_regex, count_var_regex_sub, tmp_file, 0, re.MULTILINE)
        var_file.seek(0)
        var_file.write(repl_count_var)
        var_file.truncate()

def remove_vars_from_main(f: typing.TextIO, var_lst: list) -> None:
    # With variables written to a new file, remove them from the main file
    with open(f.name) as tmp_file:
        tf_file = tmp_file.read()
    if "".join(var_lst) in tf_file:
        tf_file = tf_file.replace("".join(tf_vars), "")
        f.seek(0)
        # Trim leading whitespace if it exists
        if tf_file[0] == "\n":
            tf_file = tf_file[1:]
        f.write(tf_file)
        f.truncate()
    else:
        print("ERROR: Unable to move variables out of " + f.name)

def remove_required_version_regex(f: typing.TextIO) -> None:
    with open(f.name) as tmp_file:
        tf_file = tmp_file.read()
    version_regex = r".*required_version.*<.*0\.12.*"
    if re.findall(version_regex, tf_file):
        repl_version = re.sub(version_regex, "", tf_file, 0, re.MULTILINE)
        f.seek(0)
        f.write(repl_version)
        f.truncate()

# NOTE: This is not implemented, as it - as regexes are wont to do - fails on edge cases
# Variable regex explanation
# Group 1: 0+ of any character, with a negative lookahead of the word "variable" at a line's start
#          This is used to discard anything prior to a variable block
# Group 2: The word "variable" at a line's start, followed by 1+ of any character
# Group 3: Either the string "{}" or "{" followed by 1+ a linebreak or whitespace character, followed by
#          1+ of any character except linebreaks, followed by a linebreak or whitespace, followed by
#          "}" at a line's end
# Group 4: 1+ of any character

# Example:
# provider "aws" {                                                                                          <-- Group 1
#   alias = "accepter"                                                                                      <-- Group 1
# }                                                                                                         <-- Group 1
#                                                                                                           <-- Group 1
# variable "name" {}                                                                                        <-- Group 2
# variable "count" {}                                                                                       <-- Group 2
# variable "long_string" {                                                                           <-- Groups 2 and 3
#     default = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod                    <-- Group 3
#                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,               <-- Group 3
#                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat..."      <-- Group 3
# }                                                                                                         <-- Group 3                                                                                 
# data "aws_route_tables" "requester" {                                                                     <-- Group 4
#    provider = "aws.requester"                                                                             <-- Group 4
#    vpc_id = "${var.requester_vpc_id}"                                                                     <-- Group 4
# }                                                                                                         <-- Group 4

#var_regex = r"((?!^variable)[\s\S])*(^variable[\s\S]+)({}$|{[\n\s].+[\n\s]}$)([\s\S]*)"
#var_regex_sub = r"\2\3"

# You can glob a Path object
cwd = Path(os.getcwd())

ignore = ["data", "locals", "module", "output", "provider", "resource"]
tf_files = [x for x in cwd.glob("**/*.tf") if not x.name.startswith("variables")]
for tf_file in tf_files:
    # Regex modules and write the file
    try:
        with open(tf_file, "r+") as f:
            if ((".terraform" not in f.name) and (".terragrunt-cache" not in f.name)) :
                rename_count_regex(f)
                tf_vars = strip_vars(f)
                remove_required_version_regex(f)
                # User is already informed in strip_vars() if a file doesn't have variables to move
                if tf_vars:
                    # Trim leading whitespace if it exists
                    if tf_vars[0] == "\n":
                        del tf_vars[0]
                    write_var_file(f, tf_vars)
                    remove_vars_from_main(f, tf_vars)
                try:
                    rename_count_regex_in_var_file(f)
                except IOError:
                    print("ERROR: No variable file found in " + os.path.dirname(os.path.realpath(f.name)))

    except IOError:
        raise
        sys.exit(1)
