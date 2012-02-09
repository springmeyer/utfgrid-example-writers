import glob
import subprocess
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

grid_cols = []
title_cols = []
time_cols = []
for f in glob.glob("*_renderer.py"):
    print f
    start = datetime.now()
    proc = subprocess.Popen(['python',f], shell=False, stdout=subprocess.PIPE)
    proc.wait()
    end = datetime.now() 
    totaltime = (end - start)
    elapsed = totaltime.seconds + totaltime.microseconds/1000000.0
    print elapsed
    j = json.loads(proc.communicate()[0])
    grid = j['grid']
    grid_txt = '\n'.join([str(row) for row in grid])
    grid_cols.append("<td><pre>%s</pre></td>" % grid_txt)
    title_cols.append("<td>%s</td>" % f)
    time_cols.append("<td>%s sec</td>" % elapsed)

ofh = open("output.html",'w')
ofh.write("""<html>
<head>
    <style>
      pre {font-size: 8px; border: 1px grey solid; margin: 5px; line-height:8px; letter-spacing:2px; }
    </style>
</head>
<body>
<h1> Comparison of available UTFGrid renderers </h1>
<table>
<tr>%s</tr>
<tr>%s</tr>
<tr>%s</tr>
</table>
</body>
</html>""" % ('\n'.join(title_cols), 
              '\n'.join(time_cols),
              '\n'.join(grid_cols)
))
ofh.close()
