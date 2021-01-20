# Update this with the number of map files in Data (e.g. Map263.rxdata)
NUMBER_OF_MAPS = 263

require 'json'

# Stubs to permit importing modules from MKXP
class Sprite
end

class Table
  def self._load(foo)
  end
end

class Color
  def self._load(foo)
  end
end

class Tone
  def self._load(foo)
  end
end

require_relative './mkxp-oneshot/scripts/RPG.rb'
require_relative './mkxp-oneshot/binding-mri/module_rpg1.rb'

output = {
    info: [],
    maps: []
}

dd = './Data/'
mapinfo = Marshal.load(open(dd + 'MapInfos.rxdata', 'rb'))

(1..NUMBER_OF_MAPS).each {|n|
    m = Marshal.load(open(dd + "Map%03d.rxdata" % n, 'rb'))

    map = {events: []}
    map[:index] = n
    map[:name] = mapinfo[n].name
    map[:order] = mapinfo[n].order
    map[:parent_id] = mapinfo[n].parent_id
    
    puts m.events.class
    m.events.each {|ei, e|
        event = {index: ei, id: e.id, name: e.name, pages: []}
        e.pages.each {|p|
            page = {list: []}
            p.list.each {|l|
                command = {code: l.code, indent: l.indent, parameters: []}
                l.parameters.each {|a|
                    if a.class != String and a.class != Integer and a.class != Float and a.class != NilClass
                        a = a.inspect
                    end
                    
                    puts command
                    command[:parameters].push(a)
                }
                
                page[:list].push(command)
            }
            
            event[:pages].push(page)
        }
        
        map[:events].push(event)
    }
    
    output[:maps].push(map)
}

open('extracted.json', 'w').write(JSON.dump(output))
puts 'done!'