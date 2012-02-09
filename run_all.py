import glob
import subprocess
try:
    import json
except ImportError:
    import simplejson as json

grid_cols = []
title_cols = []
for f in glob.glob("*_renderer.py"):
    print f
    proc = subprocess.Popen(['python',f], shell=False, stdout=subprocess.PIPE)
    j = json.loads(proc.communicate()[0])
    grid = j['grid']
    grid_txt = '\n'.join([str(row) for row in grid])
    grid_cols.append("<td><pre>%s</pre></td>" % grid_txt)
    title_cols.append("<td>%s</td>" % f)

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
</table>
</body>
</html>""" % ('\n'.join(title_cols), '\n'.join(grid_cols)))
ofh.close()
