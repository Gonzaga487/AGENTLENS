import os
base = r'C:\Users\User\Documents\AGENTLENS\agentlens'
dirs = ['agents','api','models','services','dataset','tests','static/css','static/js','templates']
for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)
# walk and print
for root, d_names, f_names in os.walk(base):
    level = root.replace(base, '').count(os.sep)
    indent = '  ' * level
    print(f'{indent}{os.path.basename(root)}/')
    for f in f_names:
        print(f'{indent}  {f}')
print('\nDone!')
