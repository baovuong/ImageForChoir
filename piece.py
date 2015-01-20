import Image
import math

from random import randint 
from midiutil.MidiFile import MIDIFile


# function that converts musical note to value
# C4 = 60

def note_to_value(note,octave):
    notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B","B#"]
    value = (octave+1)*12
    value += notes.index(note)
    return value 

def key_value(note):
    return note_to_value(note,-1)


class Piece:
    
    def __init__(self,image_file,midi_file,singers,scale,key,bpm):
        #self.max_singers = singers
        #self.current_singers = 0 
        
        self.singers = []
        
        self.red = []
        self.blue = []
        self.green = []
        
        self.score = MIDIFile(singers)
        self.scale = scale 
        self.key = key
        self.midi_file = midi_file
        self.movements = []
        self.matrix = []
        self.bpm = bpm
        
        
        image = Image.open(image_file)
        image = image.convert("RGB")
        
        pixels = image.load()
        
        width,height = image.size
        
        for y in range(height):
            self.matrix.append(range(width))
        
        for x in range(width):
            for y in range(height):
                
                self.matrix[y][x] = (pixels[x,y][0],pixels[x,y][1],pixels[x,y][2])
                self.red.append(pixels[x,y][0])
                self.green.append(pixels[x,y][1])
                self.blue.append(pixels[x,y][2])
    
    def prepare_movement(self,minutes):
        
        # calculate dimension for n x n matrix
        pixels = minutes * len(self.singers) * self.bpm
        dimension = int(math.sqrt(pixels))
        
        # now that we have the dimension,
        # we allocate the space for
        # the movement
        x = 0
        y = 0
        chosen = False
        while not chosen:
            x = randint(0,len(self.matrix[0])-dimension)
            y = randint(0,len(self.matrix)-dimension)
            #print "finding possible part at",str(x),str(y)
            if len(self.movements) > 0:
                for movement in self.movements:
                    inx = (x <= movement.coord[0] + movement.dimension) or (x + dimension >= movement.coord[0])
                    iny = (y <= movement.coord[1] + movement.dimension) or (y + dimension >= movement.coord[1])
                    chosen = True #not (inx and iny)
                    #print "intersection with movement?",chosen
                    if not chosen:
                        break 
            
            else:
                chosen = True
        
        submatrix = []
        for i in range(dimension):
            row = []
            for j in range(dimension):
                row.append(self.matrix[i+y-1][j+x-1])
            submatrix.append(row)
            
        movement = Movement(submatrix,(x,y),dimension,minutes * self.bpm)
        self.movements.append(movement)
    
    def write_movement(self,index):
        movement = self.movements[index]
        
        # now use that movement for writing notes into the score
        
        for singer in self.singers:
            singer.elapsed_time = 0
        
        for i in range(len(movement.sequence)):
            si = i % len(self.singers)
            singer = self.singers[si]
            accepted_notes = singer.singable_notes(self.scale,self.key)
            pitch = accepted_notes[movement.sequence[i][0] % len(accepted_notes)] # red value
            duration = singer.durations[movement.sequence[i][1] % len(singer.durations)] # green value
            duration_options = [i for i in singer.durations if i <= duration]
            note_duration = duration_options[movement.sequence[i][2] % len(duration_options)] # blue value
            time = self.singers[si].time 
            
            # score.addNote(track,channel,pitch,time,duration,volume)
            if self.singers[si].elapsed_time <= movement.beats:
                self.score.addNote(si,si,pitch,self.singers[si].current_time,note_duration,90)
                self.singers[si].current_time += duration
                self.singers[si].elapsed_time += duration
        # now that the movement is finish, transition to next measure for everyone
        for i in range(len(self.singers)):
            self.singers[i].current_time = (self.singers[i].current_time - (self.singers[i].current_time % 4)) + 4
    
    def add_singer(self,singer):
        singer.time = 0
        self.score.addTrackName(len(self.singers),len(self.singers),singer.name)
        self.singers.append(singer)
        
    
    def create_track(self,singer,durations,max_time):
        if self.current_singers >= self.max_singers:
            return 1
        


        
        track = self.current_singers
        channel = self.current_singers
        pitch = 60
        time = 0
        
        
        # Duration value
        # 1 = quarter note
        # 0.5 = half note 
        duration = 0
        volume = 100
        
        # red for pitch
        # green for duration
        # blue for... volume?
        current = self.current_singers
        self.score.addTrackName(current,0,singer.name)
        accepted_notes = singer.singable_notes(self.scale,self.key)

        """
        midifile.addNote(current_data["track"],
            current_data["channel"],
            current_data["pitch"],
            current_data["time"],
            current_data["duration"],
            current_data["volume"])

        """

        
        while current < len(self.red) and time < max_time:
            pitch = accepted_notes[self.red[current] % len(accepted_notes)]
            duration = durations[self.green[current] % len(durations)]
            #volume = self.blue[current] % 100
            volume = 60
            self.score.addNote(track,channel,pitch,time,duration,volume)
            
            
            time += duration
            current += self.max_singers
            print current,len(self.red)
        self.current_singers += 1
        return 0
        
        
    def publish(self):
        binfile = open(self.midi_file, 'wb')
        self.score.writeFile(binfile)
        binfile.close()


class Movement:
    
    def __init__(self,pixels,coord,dim,beats):
        self.beats = beats
        # how the movement should be read
        self.sequence = []
        self.dimension = dim
        self.coord = coord
        
        # == Linear Sequence ==
        for i in range(len(pixels)):
            for j in range(len(pixels[i])):
                self.sequence.append(pixels[i][j])
    
    def __str__(self):
        result = "Movement:{"
        result += "coord: "
        result += str(self.coord)
        result += ", dimension: "
        result += str(self.dimension) + "}\n"
        for pixel in self.sequence:
            result += str(pixel) + "\n"
        return result 

class Singer:
    
    def __init__(self,name,lowest_note,highest_note,durations):
        self.name = name
        self.lowest_note = lowest_note
        self.highest_note = highest_note 
        self.current_time = 0
        self.durations = durations 
    
    def singable_notes(self,scale,key):
        base_value = key_value(key)
        max_value = note_to_value(key,9)
        if max_value > 127:
            max_value -= 12
        notes = range(base_value,max_value+1)
        scaled_notes = []
        
        i = 0
        n = 0
        while i < len(notes):
            scaled_notes.append(notes[i])
            i += scale[n]
            n += 1
            n %= len(scale)
        #print scaled_notes
        accepted = list(set(scaled_notes) & set(range(self.lowest_note,self.highest_note+1)))
        return accepted


    

# scales
major_scale = [2,2,1,2,2,2,1]
minor_scale = [2,1,2,2,2,1,2]
pentatonic_scale = [2,2,3,2,3]
chromatic_scale = [1,1,1,1,1,1,1,1,1,1,1,1]

# performance tempos
lead = [0.25,0.5,1,2]
chorus = [1,2,4]
chords = [2,4,8]
crazy = [0.0625,0.125,0.25,0.5,1,2,3,4]
normal = [0.5,1,2,3,4]
support = [1,2,4]
piece = Piece("zack_arabic.jpg","piece.mid",4,major_scale,"C",120)

soprano = Singer("Andi",note_to_value("F",4),note_to_value("F",5),normal)
alto = Singer("Megan",note_to_value("C",4),note_to_value("C",5),support)
tenor = Singer("Ritter",note_to_value("G",4),note_to_value("G",5),normal)
bass = Singer("Hassan",note_to_value("G",2),note_to_value("G",3),support)

piece.add_singer(soprano)
piece.add_singer(alto)
piece.add_singer(tenor)
piece.add_singer(bass)


print "preparing first movement"
piece.prepare_movement(2)
print "preparing second movement"
piece.prepare_movement(2)
print "preparing third movement"
piece.prepare_movement(2)


print "writing first movement"
print piece.movements[0]
piece.write_movement(0)
print "writing second movement"
print piece.movements[1]
piece.write_movement(1)
print "writing third movement"
print piece.movements[2]
piece.write_movement(2)

piece.publish()
    
