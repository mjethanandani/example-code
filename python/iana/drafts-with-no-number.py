#!/usr/bin/env python3

from pathlib import Path
import re

# Report all drafts mentioned in IANA registries that do not end with a number

# This is where to find the rsync'd directory of IANA registries
#   FWIW, I get this using the CLI program at
#   https://urldefense.com/v3/__https://github.com/paulehoffman/ietf-cli__;!!PtGJab4!7w7Pvbdxr4BD6DRTPUyC762OnDtay3JPPvfDRfZ1dA3xtTG5IZyuW3UQZYPJ0BMjWx0CcxoLFGe2cOHSOKTS8UfIU5I-DGo$ [github[.]com]>
base_dir = Path("~/LocalMirror/iana").expanduser()

found_drafts = {}  # key is draft name, value is registries that contain it
for (root, dirs, files) in base_dir.walk():
    for this_file in files:
   	if this_file.endswith(".xml"):  # Only look in registries
   	    with open(root / this_file) as f:
   		try:
   		    all_lines_in_f = f.readlines()
   		    for this_line in all_lines_in_f:
   			if 'type="draft"' in this_line:  # The target has a draft
   			    this_match = re.search(r'data="(.*)"', this_line)
   			    if this_match:
   				draft_name = this_match.group(1)
   				# We only care if the draft name does not end in -nn
   				if not re.findall(r'-\d\d$', draft_name):
   				    # ...and is not an XML file (another registry)
   									if not draft_name.endswith(".xml"):
   									    # ...and is not marked as an RFC-to-be
   									    if not draft_name.startswith("RFC-"):
   										# Start a set of registries that have this draft
   										if not found_drafts.get(draft_name):
   										    found_drafts[draft_name]=set()
   										    found_drafts[draft_name].add(this_file)
   		except Exception as e:
   		    print(f"Had a problem with {root / this_file}: {e}")

                    for (this_draft, these_files) in sorted(found_drafts.items()):
                        print(f"{this_draft}:   {'   '.join(these_files)}")

                        print(f"Total number of drafts: {len(found_drafts)}")
