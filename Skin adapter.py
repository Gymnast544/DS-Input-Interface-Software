f = open("skin.xml", "r")
xmlfile = f.read()
f.close()

replacements = [('b0', 'a'), ('b1', 'b'), ('b2', 'x'), ('b3', 'y'), ('b4', 'left'), ('b5', 'right'), ('b6', 'up'), ('b7', 'down'), ('b8', 'l'), ('b9', 'r'), ('b10', 'start'), ('b11', 'select'), ('generic', 'snes')]

choice = input("Would you like to \nA: Convert an existing SNES skin for use with the DS&RetroSpy \nB: Convert a DS&RetroSpy skin back to SNES (rarely used)\n")

if choice.strip().lower()=="b":
    new = 1
    old = 0
else:
    new = 0
    old = 1

for i in replacements:
    xmlfile=xmlfile.replace('"'+i[old]+'"', '"'+i[new]+'"')

print(xmlfile)

f = open("skin.xml", "w")
f.write(xmlfile)
f.close()
