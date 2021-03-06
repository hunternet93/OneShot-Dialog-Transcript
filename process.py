import datetime
import json
import re
import os

face_files = os.listdir('./Faces')
faces = [f[:-4] for f in face_files if f.endswith('.png')]
print(faces)

types = {
    'show_text': 101,
    'text_continue': 401,
    'show_choices': 102,
    'choice_condition': 402,
    'wait': 106,
    'conditional_branch': 111,
    'else': 411,
    'loop': 112,
    'repeat': 413,
    'break_loop': 113,
    'exit_event': 115,
    'call_common_event': 117,
    'change_items': 126
}

types_rev = {}
for t, c in types.items(): types_rev[c] = t

data = json.load(open('extracted.json'))

# Maps > Events > Pages > List > Commands

current_date = datetime.datetime.now().isoformat()[:10]

templ_main = '''
<html>
    <head>
        <title>OneShot Dialoge Transcript</title>
        <link href="https://fonts.googleapis.com/css?family=Space+Mono" rel="stylesheet"> 
        <link rel="stylesheet" href="dialog.css">
    </head>
    <body>
        <div id="header">
            <h1>OneShot Dialoge Transcript</h1>
            <p><em>Last updated {current_date} &#8212; <a href="https://github.com/hunternet93/OneShot-Dialog-Transcript">project on GitHub</a></em></p>
        </div>
        
        <script>
            function setPlayerName () {{
                var name = document.querySelector('#name').value;
                for (var s of document.querySelectorAll('.playername')) {{
                    s.innerHTML = name;
                }}
            }}
        </script>
        
        <p>
            <input id="name" placeholder="Player">
            <button onclick="setPlayerName();">Set Player Name</button>
        </p>

        <h3>Maps</h3>

        <ul id="mapmenu">{mapmenu}</ol>

        <div id="maps">${maps}</div>
        
        <a id="up" href="#header">Top</a>
    </body>
</html>'''

templ_mapmenu_item = '<li class="maplist-item" style="{indent}"><a href="#map-{index}">{name}</a></li>'

templ_map = '''
<div class="map" id="map-{index}">
    <h2><span class="mapparents">{parents}</span> &gt {name}</h2>
    
    <div class="events">{events}</div>
</div>'''

templ_event = '''
<div class="event">
    <h4>Event: {name}</h4>
    
    <div class="pages">{pages}</div>
</div>'''

templ_page = '''
<div class="page">
    <h4>Page {page}</h4>
    
    <div class="commands">{commands}</div>
</div>'''

templ_command_text = '''
<div class="command command-text" style="{indent}">
    <div class="face">
        {image}
        <p>@{face}</p>
    </div>
    <p>{text}</p>
</div>'''

templ_command_condition = '''
<div class="command command-condition" style="{indent}">
    <p><em>Condition {parameters}</em></p>
</div>'''

templ_command_else = '''
<div class="command command-else" style="{indent}">
    <p><em>Else</em></p>
</div>'''

templ_command_choice = '''
<div class="command command-choice" style="{indent}">
    <p><em>Player choice:</em></p>
    <ul>{choices}</ul>
</div>'''

templ_command_choice_condition = '''
<div class="command command-choice-condition" style="{indent}">
    <p><em>If player choice is <strong>{choice}</strong></em></p>
</div>'''

templ_command_wait = '''
<div class="command command-wait" style="{indent}">
    <p><em>Wait {frames} frames.</em></p>
</div>'''

templ_command_other = '''
<div class="command command-wait" style="{indent}">
    <p><small>{code} {parameters}</small></p>
</div>'''


rend_mapmenu_items = ''
rend_maps = ''

for map in sorted(data['maps'], key = lambda m: m['order']):
    rend_events = ''

    for event in sorted(map['events'], key = lambda e: e['index']):
        event_has_dialog = False
        rend_pages = ''
        
        for pagenum, page in enumerate(event['pages']):
            page_has_dialog = False
            rend_commands = ''
            
            skip = 0
            for ci, command in enumerate(page['list']):
                if skip:
                    skip -= 1
                    continue
            
                rend = ''
                indent = 'padding-left: {}em;'.format(command['indent'] * 2)
                
                if command['code'] == types['show_text']:
                    event_has_dialog = True
                    page_has_dialog = True
                    text = command['parameters'][0]
                    face = 'unknown'
                    image = ''
                    
                    for peek in page['list'][ci + 1:]:
                        if peek['code'] == types['text_continue']:
                            text += peek['parameters'][0]
                            skip += 1
                        else:
                            break
                    
                    if len(text) > 0 and text[0] == '@':
                        face = text.split(' ')[0][1:]
                        text = text[len(face)+1:]
                        
                        if face in faces:
                            image = '<img src="Faces/{}.png">'.format(face)
                    
                    text = re.sub('\\@.*?\s', '', text)                    
                    text = text.replace(r'\p', '<span class="playername">Player</span>')
                    text = text.replace(r'\n', '<br>')
                    text = text.replace(r'\.', '')
                    text = text.replace(r'\>', '')
                    text = text.replace('\\', '')
                    
                    rend = templ_command_text.format(face = face, image = image, text = text, indent = indent)

                elif command['code'] == types['conditional_branch']:
                    # TODO figure out parameter syntax!
                    rend = templ_command_condition.format(parameters = command['parameters'], indent = indent)
                
                elif command['code'] == types['else']:
                    rend = templ_command_else.format(indent = indent)
                
                elif command['code'] == types['show_choices']:
                    rend = templ_command_choice.format(choices = ''.join(('<li>'+c+'</li>' for c in eval(command['parameters'][0]))), indent = indent)
                
                elif command['code'] == types['choice_condition']:
                    rend = templ_command_choice_condition.format(choice = command['parameters'][1], indent = indent)
                
                elif command['code'] == types['wait']:
                    rend = templ_command_wait.format(frames = command['parameters'][0], indent = indent)
                                
                rend_commands += rend
#                rend_commands += templ_command_raw.format(command = command, indent = indent)
                
            if page_has_dialog: rend_pages += templ_page.format(page = pagenum, commands = rend_commands)
        
        if event_has_dialog: rend_events += templ_event.format(name = event['name'], pages = rend_pages)
    
    parents = []
    curr = map
    while True:
        if curr['parent_id'] == 0: break

        for p in data['maps']:
            if p['index'] == curr['parent_id']: curr = p
        parents.insert(0, curr['name'])
        print('parent', curr['name'], curr['index'], curr['parent_id'])
    
    rend_maps += templ_map.format(index = map['index'], name = map['name'],
        parents = ' > '.join(parents), events = rend_events)

    rend_mapmenu_items += templ_mapmenu_item.format(index = map['index'], name = map['name'], indent = 'margin-left: '+str(len(parents)*2)+'em')

open('dialog.html', 'w').write(templ_main.format(mapmenu = rend_mapmenu_items, maps = rend_maps, current_date = current_date))
