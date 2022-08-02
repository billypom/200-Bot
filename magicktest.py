import os
import subprocess

mmr_table_string = '<span foreground="chartreuse">heyy</span>'
correct = subprocess.run(['convert', '-background', 'gray21', 'pango:', '<tt><span foreground="white">{mmr_table_string}</span></tt>', f'testmmr.png'], check=True, text=True)