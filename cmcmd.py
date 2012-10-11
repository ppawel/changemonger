#!/usr/bin/env python

import changemonger
import helpers
import os.path
import sys

id = os.path.split(sys.argv[1])[1][:-4]
cset = helpers.get_changeset_or_404(id)
sentence = changemonger.changeset_sentence(cset)
print sentence
