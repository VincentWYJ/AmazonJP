import re



def weightx(weight_temp):
    packet_weight = 150
    if re.search(r".*Kg.*", weight_temp) != None:
        weight_factor = 1000
        packet_total_weight = int(float(weight_temp.replace(u'Kg', '').strip()) *weight_factor) + packet_weight
    elif re.search(r".*kg.*", weight_temp) != None:
        weight_factor = 1000
        packet_total_weight = int(float(weight_temp.replace(u'kg', '').strip()) * weight_factor) + packet_weight
    elif re.search(r".*キロ.*", weight_temp) != None:
        weight_factor = 1000
        packet_total_weight = int(float(weight_temp.replace(u'キロ', '').strip()) * weight_factor) + packet_weight
    elif re.search(r".*g.*", weight_temp) != None:
        weight_factor = 1
        packet_total_weight = int(float(weight_temp.replace(u'g', '').strip()) * weight_factor) + packet_weight
    elif re.search(r".*グラム.*", weight_temp) != None:
        weight_factor = 1
        packet_total_weight = int(float(weight_temp.replace(u'グラム', '').strip()) * weight_factor) + packet_weight
    else:
        packet_total_weight = 10000

    print(packet_total_weight)

if __name__ == '__main__':
    weight_temp = str('146 キロ')
    weightx(weight_temp)