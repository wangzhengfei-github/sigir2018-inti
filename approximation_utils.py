import os
import shutil
from xml.dom import minidom
from xml.etree.ElementTree import ElementTree


def change_traffic_light(configuration, process_id):
    xmlfile = ElementTree()
    xmlfile.parse('tmp/di-tech-' + str(process_id) + '.net.xml')
    nodes = xmlfile.findall("tlLogic")
    for node in nodes:
        if node.get('id') == 'tl1':
            node.set('offset', str(configuration[0][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[0][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[0][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[0][3]))
                if phase.get('id') == '4':
                    phase.set('duration', str(configuration[0][4]))
        if node.get('id') == 'tl2':
            node.set('offset', str(configuration[1][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[1][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[1][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[1][3]))
                if phase.get('id') == '4':
                    phase.set('duration', str(configuration[1][4]))
        if node.get('id') == 'tl3':
            node.set('offset', str(configuration[2][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[2][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[2][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[2][3]))
        if node.get('id') == 'tl4':
            node.set('offset', str(configuration[3][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[3][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[3][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[3][3]))
                if phase.get('id') == '4':
                    phase.set('duration', str(configuration[3][4]))
                if phase.get('id') == '5':
                    phase.set('duration', str(configuration[3][5]))
        if node.get('id') == 'tl5':
            node.set('offset', str(configuration[4][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[4][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[4][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[4][3]))
        if node.get('id') == 'tl6':
            node.set('offset', str(configuration[5][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[5][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[5][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[5][3]))
                if phase.get('id') == '4':
                    phase.set('duration', str(configuration[5][4]))
                if phase.get('id') == '5':
                    phase.set('duration', str(configuration[5][5]))
        if node.get('id') == 'tl7':
            node.set('offset', str(configuration[6][0]))
            phases = node.findall("phase")
            for phase in phases:
                if phase.get('id') == '1':
                    phase.set('duration', str(configuration[6][1]))
                if phase.get('id') == '2':
                    phase.set('duration', str(configuration[6][2]))
                if phase.get('id') == '3':
                    phase.set('duration', str(configuration[6][3]))
    if os.path.exists('tmp/di-tech-' + str(process_id) + '.rou.xml') is not True:
        shutil.copy('di-tech.rou.xml', 'tmp/di-tech-' + str(process_id) + '.rou.xml')
    xmlfile.write('tmp/di-tech-' + str(process_id) + '.net.xml', encoding='utf-8', xml_declaration=True)


def calculate_waitsteps(process_id):
    total_loss = 0.0
    n_vehicles = 0
    dom = minidom.parse('tmp/tripinfo-' + str(process_id) + '.xml')
    root = dom.documentElement
    tripinfos = root.getElementsByTagName('tripinfo')
    for tripinfo in tripinfos:
        time_loss = float(tripinfo.getAttribute('waitSteps'))
        total_loss += time_loss
        n_vehicles += 1
    return total_loss / n_vehicles