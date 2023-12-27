data = {'Training Videos': {'Setting up for Stinson hall Assemblies ': {'files': ['VID_20230421_151744289.mp4']}, 'Setting up for Sports Hall': {'files': ['Sports hall Tutorial.mov']}, 'Health and Safety': {'Another ONE': {'files': ['AGS-SL-Logo (3).png']}, 'files': ['Health and Safety Demonstration.mp4']}, 'Setting up at Back': {'files': ['SetupAtBack.mp4']}, 'files': []}, 'Misc': {'files': ['dbTimetable.png']}, 'Rotas': {'files': ['Current rota.pdf']}, 'Private Study Periods': {'files': ['AGS Sound and Lighting Free Periods 2023-2024.docx']}, 'Troubleshooting': {'files': []}, 'Manuals': {'files': ['Qu-Mixer-Reference-Guide-AP9372_10.pdf', 'lightingboardManual.pdf', 'Qu-Mixer-Getting-Started-Guide-AP10025_2-V1.9.pdf']}, 'Health and Safety': {'files': ['Complaints about health and safety.docx']}, 'files': ['RAHAHH.txt']}

def insertField(data):
    if isinstance(data, list):
        for i in data:
             print(i, '!!!!!!')

    else:
        for key, value in data.items():
            #print(key)
            print('MIDDLE', key, value, '\n')
            insertField(value)

for key, value in data.items():
            #print(key, value)
            print('START', key, value, '\n')
            insertField(value)