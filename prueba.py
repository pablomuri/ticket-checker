string = open("prueba.txt", "r").read()
lines = string.splitlines()


def get_value(line):
    return line.replace(" ", "").split("=")[1].replace("[","").replace("]","").replace('"','').rstrip(";").split(",")


for index in range(len(lines)):
    if "if (fechas) {" in lines[index]:
        days_vars = lines[index+1].replace(" ", "").split("=")
        days_off_var = days_vars[0]
        days_var = days_vars[1].rstrip(".")
        break

days_offs = dict()
for index in range(len(lines)):
    if "var " + days_off_var in lines[index]:
        days_offs[days_off_var] = get_value(lines[index])
        if len(days_offs) >= 2:
            break

    elif "var " + days_var in lines[index]:
        days_offs[days_var] = get_value(lines[index])
        if len(days_offs) >= 2:
            break

days_off = days_offs[days_off_var]
days_all = days_offs[days_var]

if len(days_all) != len(days_off):
    for day in days_all:
        if day not in days_off:
            print("fecha disponible " + day)
