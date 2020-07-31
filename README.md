
# terraform-0.12-replacer

### WARNING: I AM IN NO WAY RESPONSIBLE IF YOU RUN THIS WITHOUT VERSION CONTROL AND THEN BREAK YOUR INFRASTRUCTURE.

#### Who this is for:
Anyone who needs to upgrade a large amount of Terraform <= 0.11 into 0.12-compliant HCL, but doesn't want to manually find and rename variables, specifically within modules. If you haven't used `count` as a variable name for modules, you can just use standard search-and-replace within your editor.

#### What it does do:
1. Replaces [reserved word\[s\]](https://www.terraform.io/docs/configuration/variables.html#declaring-an-input-variable) in Terraform files in preparation for 0.12.
2. Pulls variables out of any .tf file not named variables.tf, and places them in variables.tf

#### What it does not do:
1. Actually perform the 0.12 upgrade. Hashicorp's own 0.12upgrade tool does a wonderful job at that.
2. Work in all edge cases. If you find one, please submit a PR.
3. Pull variables out if they are not in a contiguous block.
4. Alpha-sort the variables.tf file. It could be done with a clever regex.
5. Use a regex to find variables. There is a lengthy comment block around line 100 detailing a wonderfully complex regex that does in fact work for many cases, but not all. As such, I opted to not use it, and instead use readlines() and look for strings starting with "variable." If you can improve the regex, again, please submit a PR.
6. Pretty up the resultant .tf files. There may be newlines or lack thereof. 0.12upgrade may handle some of those; I know it splits out one-line variables with definitions into multi-line.

#### Requirements:
1. Version - Python 3.x. Tested with 3.7.7, but it should probably work with anything 3.5+, as I'm using type hints. If you want to strip those out, it will probably work with 3.x, maybe 2.7. I have no interest in backporting it to 2.7 if it doesn't work.
2. OS - It _should_ work on *nix and Windows. UNC paths on Windows would probably cause issues with os.path, but if you're accessing local files it should be fine. Developed on a Mac.
