import os
import subprocess

mmr_table_string = '<span foreground="chartreuse">heyy this is my string\nheyheyhey\nhelo\nfjidfodsfodjs</span>'
pango_string = f'pango:"<tt>{mmr_table_string}</tt>"'
correct = subprocess.run(['convert', '-background', 'gray21', pango_string, 'testmmr.png'], check=True, text=True)

# convert -background gray21 -fill white pango:'<tt><span foreground="white">hey</span></tt>' my_test.png