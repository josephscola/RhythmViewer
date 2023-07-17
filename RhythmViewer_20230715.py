    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 14:24:15 2023

@author: scola

test js to draw on a canvas. structured no the pong example from transcrypt doc

2023.05.05  No containers in class attributes ? fixed
2023.06.14  migration to RhythmViewer name : operational with one cycle hard written
2023.06.21  Could not make the lines (polygon edges and rays) so commit calls install (slow ?)
            Operational without sound
            resize and graphic engine OK. Sound bugs
            migration to dedicated directory
2023.06.29  SOUND : uses internal oscilator
            SOUND : scheduled beep time with audioContext (Not yet)
2023.07.03  switching from time to audioContext time prevent the animation to go on after page refresh
2023.07.05  use audioContext clock for animation doesn't work
            can't use audioBuffer to load pre-recorded sample -> oscillator
            
"""


__pragma__ ('skip')
document = window = Math = Date = 0 # Prevent complaints by optional static checker
__pragma__ ('noskip')

__pragma__ ('noalias', 'clear')


import GraphParams as gp
from com.fabricjs import fabric
#import {fabric} from 'fabric';



# dimensions en coordonnées de référence, avant possible rescale
orthoWidth = 1000 
orthoHeight = 750
fieldHeight = 650

enter, esc, space = 13, 27, 32

window.onkeydown = lambda event: event.keyCode != space # Prevent scrolldown on spacebar press



class Attribute:    # Attribute in the gaming sense of the word, rather than of an object
    def __init__ (self, game):
        self.game = game                    # Attribute knows game it's part of
        self.game.attributes.append (self)  # Game knows all its attributes
        self.install ()                     # Put in place graphical representation of attribute
        self.reset ()                       # Reset attribute to start position
                
    def reset (self):       # Restore starting positions or score, then commit to fabric
        self.game.t0 = + __new__ (Date) / 1000
        self.commit ()      # Nothing to restore for the Attribute base class
                
    def move (self):
        pass
                
    def interact (self):
        pass
        
    def commit (self):
        pass


class Cycle (Attribute):   # cycle circle and polygon that can move
    def __init__ (self, game, n):
        Attribute.__init__ (self, game)
        self.n = n
        #self.radius = 0.28 * self.game.canvasWidth
        self.radius = self.game.R[self.n]
        C = list (self.game.C[n])
        self.Cx = C[0]
        self.Cy = C[1]
        self.color = self.game.CAMAIEU [self.n]
#        self.game.initialize_main_cycle ()
        self.game.initialize_polygon (self.n)
        
        
            
        
    def install (self):     # The sprite holds an image that fabric can display
        self.circle = __new__ (fabric.Circle ({'radius': self.game.R[self.n],
                                              'originX': 'center', 'originY': 'center',
                                              'angle': 0, 'startAngle': 0, 'endAngle': 2 * Math.PI,
                                              'stroke': self.game.linecolor, 'strokeWidth': 1,
                                              'fill': ''}))
        # install Rays
        self.Rays = []
        S = list (self.game.S[self.n])
        for Sk in S:
            Sk = list (Sk)
            self.Rays_coords = [self.Cx, self.Cy, Sk[0], Sk[1]]
            self.Rays.append (__new__ (fabric.Line (self.Rays_coords, {'stroke': self.color})))
        
        
        # install Edges
        self.Edges = []
        S = list (self.game.S[self.n])
        for k in range (self.game.N[self.n]):
            S1 = list (S[k])
            S2 = list (S[(k+1) % self.game.N[self.n]])
            self.Edge_coords = [S1[0], S1[1], S2[0], S2[1]]
            self.Edges.append (__new__ (fabric.Line (self.Edge_coords, {'stroke': self.color})))
            
# modification of the line properties with set method only works in install method ... why ?
#        self.edge0 = __new__ (fabric.Line ([self.Cx, self.Cy, 10, 20], {'stroke': 'red',
#                                           'x1' : self.Cx,
#                                           'y1' : self.Cy,
#                                           'x2' : 10,
#                                           'y2' : 20}))
#        self.edge0 .set ('x1' : 300)
    
        
        return None
    
    __pragma__ ('kwargs')
    def reset (self, vX = 0, vY = 0, x = 0, y = 0):
        self.vX = vX        # Speed
        self.vY = vY
        
        self.x = x          # moveed position, can be commit, no bouncing initially
        self.y = y
        
        Attribute.reset (self)
    __pragma__ ('nokwargs')
    
    def move (self):     # move position, do not yet commit, bouncing may alter it
        self.x += self.vX * self.game.deltaT
        self.y += self.vY * self.game.deltaT

    def commit (self):      # Update fabric image for asynch draw
        self.install ()
        self.radius = self.game.R[self.n]
        self.circle.radius = self.radius
        if self.n != 0:
            self.game.move_polygon (self.n)
        C = list (self.game.C[self.n])
        self.Cx = C[0]
        self.Cy = C[1]
        self.circle.left = self.Cx
        self.circle.top = self.Cy

        return None
        
    def draw (self):
        drawCircle = ((self.n > 0 and self.game.SecondaryCyclesVisible) or 
                      (self.n == 0 and self.game.MainCycleVisible))
        if drawCircle:            
            self.game.canvas.add (self.circle)
        for r in self.Rays:
            self.game.canvas.add (r)
        for e in self.Edges:
            self.game.canvas.add (e)
        

class Spot (Attribute):
    def __init__ (self, game, n):
        Attribute.__init__ (self, game)
        self.size = self.game.RS_radius
        self.n = n
        self.color = self.game.CAMAIEU [self.n] 
        
    def install (self):
        self.image = __new__ (fabric.Circle ({'radius': self.size,
                                              'originX': 'center', 'originY': 'center',
                                              'angle': 0, 'startAngle': 0, 'endAngle': 2 * Math.PI,
                                              'stroke': 'white', 'strokeWidth': 1,
                                              'fill': self.color}))
    
    def RS_coords_0(self, x1, y1, x2, y2):
        # hops from one edge center to the next one
        return (x1 + x2)/2, (y1 + y2)/2
    
    def RS_coords(self, x1, y1, x2, y2):
        # exponential flow along the edges
        A = 1 / (Math.exp(1 / self.game.feel) - 1)
        s = A * (Math.exp(self.tp / self.game.feel) - 1)
        return (1 - s) * x2 + s * x1, (1 - s) * y2 + s * y1

    def pulse_relative_time(self, n, tn, jn):
        if self.game.irregular:
            durations = ()
            for i in range(self.N[n] - 1):
                durations += (self.game.voicings[n][i+1] - self.game.voicings[n][i]) * self.game.T[n],
            durations += ((1 - self.game.voicings[n][self.game.N[n] - 1]) * self.game.T[n],)
            tp = ((tn - self.game.voicings[n][jn] * self.game.T[n]) % durations[jn]) / durations[jn]
        else:
            tp = (self.game.t % (self.game.T[n] / self.game.N[n]) ) * self.game.N[n] / self.game.T[n]
        return tp
    
    __pragma__ ('kwargs')
    def reset (self):
        self.x = self.game.mainCycle.Cx
        self.y = self.game.mainCycle.Cy + self.game.mainCycle.radius
        Attribute.reset (self)
    __pragma__ ('nokwargs')
    
    def move (self):
        tn, jn = self.game.pulse_index_in_cycle(self.n)
        self.tp = self.pulse_relative_time(self.n, tn, jn)

        S1 = list (self.game.S[self.n][self.game.N[self.n] - jn - 1])
        S2 = list (self.game.S[self.n][(self.game.N[self.n] - jn) % self.game.N[self.n]])
        RS =  list (self.RS_coords(S1 [0], S1 [1], S2 [0], S2 [1]))

        self.x = RS [0]
        self.y = RS [1]
        
    def commit (self):
        self.image.left = self.x
        self.image.top = self.y
    
    def draw (self):
        self.game.canvas.add (self.image)
           


class TimeFluxSpot (Attribute):
    def __init__ (self, game):
        Attribute.__init__ (self, game)
        self.radius = 0.007 * self.game.canvasWidth
        
    def install (self):
        self.image = __new__ (fabric.Circle ({'radius': self.radius,
                                              'originX': 'center', 'originY': 'center',
                                              'angle': 0, 'startAngle': 0, 'endAngle': 2 * Math.PI,
                                              'stroke': 'white', 'strokeWidth': 1,
                                              'fill': 'white'}))
        
    __pragma__ ('kwargs')
    def reset (self):
        self.x = self.game.mainCycle.Cx
        self.y = self.game.mainCycle.Cy + self.game.mainCycle.radius
        Attribute.reset (self)
    __pragma__ ('nokwargs')
    
    def move (self):
        self.x = self.game.mainCycle.radius * Math.cos (self.game.omega [0] * self.game.t + self.game.q0) + self.game.mainCycle.Cx
        self.y = -self.game.mainCycle.radius * Math.sin (self.game.omega [0] * self.game.t + self.game.q0) + self.game.mainCycle.Cy
        
    def commit (self):
        self.image.left = self.x
        self.image.top = self.y
    
    def draw (self):
        self.game.canvas.add (self.image)
         
    
class Game:
    def __init__ (self, bpm, voicings, mode, feel, graph_params, path2wav = './temp/'):
        self.serviceIndex = 1 if Math.random () > 0.5 else 0    # Index of player that has initial service
        self.pause = False                           # Start game in paused state
        self.keyCode = None
        
        # html objects defined in the calling html file are referred to as 'document'
        self.textFrame = document.getElementById ('text_frame')
        self.canvasFrame = document.getElementById ('canvas_frame')
        self.buttonsFrame = document.getElementById ('buttons_frame')
        self.memo = document.getElementById ('memo')
        
        # initialize canvas
        self.aspectRatio = 1.
        self.topMargin = 100
        self.canvas = __new__ (fabric.Canvas ('canvas', {'backgroundColor': 'black',
                                                         'originX': 'center', 'originY': 'center'}))
        self.canvas.onWindowDraw = self.draw        # Install draw callback, will be called asynch
        self.canvas.lineWidth = 2
        self.canvas.clear ()    

        # set canvas size
        self.pageWidth = window.innerWidth
        self.pageHeight = window.innerHeight
        
        self.textTop = 0

        if self.pageHeight > 1.2 * self.pageWidth:
            self.canvasHeight = self.pageHeight
            self.canvasTop = self.textTop + self.topMargin
        else:
            self.canvasHeight = 0.7 * self.pageHeight
            self.canvasTop = self.textTop + self.topMargin
        
        self.canvasWidth = self.aspectRatio * self.canvasHeight
        self.canvasLeft = 0.5 * (self.pageWidth - self.canvasWidth)
        
        
        self.WIDTH = self.canvasWidth
        self.HEIGHT = self.canvasHeight
        
        self.dt = 0.02
        self.jn = 0
        
        self.get_graphic_parameters(graph_params)


        # cycles parameters
        self.mode = mode
        self.bpm = bpm
        if type(voicings[0]) == int: 
            self.N = voicings
            self.irregular = False
        else:
            self.voicings = voicings
            self.init_N()
            self.irregular = True
        self.S = []
        
        self.initialize_cycles ()
        
        #for n in range (len((self.N)):
        self.cycle = []
        self.Polygon = [-1] * len(self.N)
        self.Sound = [-1] * len(self.N)
        
        # Vertex1
        self.enlarge = 5/4
        self.Vertex1color = 'red'
        
        # time flux spot (TFS)
        self.R2TFS_ratio = 20
        self.TFS_fill = "#EAF3FB"
        self.TFS_outline = "#A2B5C7"
        self.q0 = 1.5 * Math.PI
        
        # rhythm spot parameters (RS)
        self.R2RS_ratio = 1
        self.feel = feel # 0.5 = straight feel, 0.33 = shuffle feel 0.25 = hard swing feel; 1 = linear flow
        self.TFS_radius = 0.007 * self.canvasWidth
        # initialize RS size
        self.RS_radius = self.TFS_radius / self.R2RS_ratio
        
        
        # Construction des objets
        self.attributes = []
        self.Cycles = []
        self.RhythmSpots = []
        
        for n in range (len (self.N)):
            self.Cycles.append (Cycle (self, n))
        self.mainCycle = self.Cycles [0]
        for n in range (len (self.N)):
            self.RhythmSpots.append (Spot (self, n))
        self.TFS = TimeFluxSpot  (self)
        
        ##### TIME MANAGEMENT #####
        window.setInterval (self.update, 20)    # Install update callback, time in ms
        window.setInterval (self.draw, 20)      # Install draw callback, time in ms
        
#        self.ac = __new__ (window.AudioContext() || window.webkitAudioContext())
        self.ac = __new__ (window.AudioContext())

        self.time = + __new__ (Date) / 1000 # absolute time
        #self.time = self.ac.currentTime
        self.t0 = self.time # object start time
        self.t = self.time - self.t0 # animation relative time


        ##### AUDIO #####
        #https://www.javascripture.com/AudioContext
        beep = document.getElementById('beep')
#        beep.play()
        self.setupSample ()
        self.playSample()
 
        
        """ INTERRUPTED ATTEMPT TO LOAD SAMPLE IN AUDIOBUFFER
        self.sample = self.setupSample ()
        self.playSample ()
        """
        
        """ OBSOLETE : load sample from disk
        self.sounds = []
        for n in range (self.N):
            self.sounds.append (__new__ (Audio ('./sounds/beep_' + str (self.N[n]) + '.wav')))
        
        self.sound0 = __new__ (Audio ('./sounds/beep_' + str (self.N[0]) + '.wav'))
        self.sound0.play()
        
        self.sound1 = __new__ (Audio ('./sounds/beep_' + str (self.N[1]) + '.wav'))
        self.sound1.play()
        """
        
        #source.start()
        
        window.onresize = self.resize
        self.resize ()
        self.install ()
        # END OF OBJECT INITIALIZATION
        
    
    
    async def getFile(self, filePath):
        # https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques#dial-up_%E2%80%94_loading_a_sound_sample
        url = "https://upload.wikimedia.org/wikipedia/en/transcoded/d/dc/Strawberry_Fields_Forever_%28Beatles_song_-_sample%29.ogg/Strawberry_Fields_Forever_%28Beatles_song_-_sample%29.ogg.mp3"
        response = await fetch(filePath)
        #response = await fetch(url)
        arrayBuffer = await response.arrayBuffer()
        audioBuffer = await self.ac.decodeAudioData(arrayBuffer)
        return audioBuffer
    
    
    async def setupSample(self):
        #https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques#dial-up_%E2%80%94_loading_a_sound_sample
#        filePath = './sounds/beep_2.wav'
        filePath = 'beep_2.wav'
        self.sample = await self.getFile(filePath)   
        return None
    
    
    def playSample (self):
        #https://stackoverflow.com/questions/71199451/how-can-i-play-an-audio-file-at-specified-times-in-javascript-audiocontext
        #sampleSource = __new__ (AudioBufferSourceNode (self.ac, {'buffer': self.sample, 'playbackRate': 44100}))
        source = self.ac.createBufferSource ()
        source.buffer = self.sample
        source.connect (self.ac.destination)
        source.start (0)
        return None
    

    
    """ ATTEMPT TO LOAD SAMPLE IN AUDIOBUFFER
    async def getFile(self, filePath):
        # https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques#dial-up_%E2%80%94_loading_a_sound_sample
        response = await fetch(filePath)
        arrayBuffer = await response.arrayBuffer()
        audioBuffer = await self.ac.decodeAudioData(arrayBuffer)
        return audioBuffer
    
    
    async def setupSample(self):
        #https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques#dial-up_%E2%80%94_loading_a_sound_sample
        filePath = './sounds/beep_2.wav'
        sample = await self.getFile(self.ac, filePath)   
        return sample
    
    
    def playSample (self):
        #sampleSource = __new__ (AudioBufferSourceNode (self.ac, {'buffer': self.sample, 'playbackRate': 44100}))
        sampleSource = __new__ (AudioBufferSourceNode (self.ac))#, {'buffer': self.sample}))
        sampleSource.connect (self.ac.destination)
        sampleSource.start (0)
        return sampleSource
    """

    """ INTERRUPTED ATTEMPT TO GENERATE NOISE BUFFER
        bufferSize = self.ac.sampleRate * 1
        # Create an empty buffer
        noiseBuffer = __new__ (window.AudioBuffer({'length': bufferSize,
                                            'sampleRate': self.ac.sampleRate}))

        # Fill the buffer with noise
        data = noiseBuffer.getChannelData(0)
        for i in range (bufferSize):
            data[i] = Math.random() * 2 - 1

        # Create a buffer source for our created data
        noise = __new__ (window.AudioBufferSourceNode(self.ac, {'buffer': noiseBuffer}))
        noise.connect(self.ac.destination)
        noise.start()
        """
        
    def beep (self, n):
        tn, jn = self.pulse_index_in_cycle(n)
        if self.jn != jn:
            self.memo.innerHTML = 'SHOOOOT!!!!'
            self.playSample()
            self.jn = jn
        else: 
            self.memo.innerHTML = str(self.jn)
        return None
    

    """
    def scheduleNote(self, ac, time, dur):
        self.osc = self.ac.createOscillator()
        self.osc.connect( self.ac.destination )
        self.osc.start(time)
        self.osc.stop(time + dur)
        return None
    """

        
    def install (self):
        for attribute in self.attributes:
            attribute.install ()
        
    def mouseOrTouch (self, key, down):
        if down:
            if key == 'space':
                self.keyCode = space
            elif key == 'enter':
                self.keyCode = enter
            else:
                self.keyCode = ord (key)
        else:
            self.keyCode = None
 
    def update (self):                          # Note that update and draw are not synchronized
        oldTime = self.t
        self.time = + __new__ (Date) / 1000
#        self.time = self.ac.currentTime
        self.t = self.time - self.t0
        self.deltaT = (self.t - oldTime)
        self.update_cycle_parameters ()
        self.beep (0)
        

#        for n in range (1, len (self.N)):
#            self.move_polygon (n)
#            self.beep (n)
#        sound = list (self.sounds)
#        sound[0].play ()

        
        if self.pause:                          # If in paused state
            if self.keyCode == space:           #   If spacebar hit
                self.pause = False              #         Start playing
            elif self.keyCode == enter:         #   Else if enter hit
                self.scoreboard.reset ()        #         Reset score
        else:                                   # Else, so if in active state
            for attribute in self.attributes:   #   Compute moveed values
                attribute.move ()
            
            for attribute in self.attributes:   #   Correct values for bouncing and scoring
                attribute.interact ()
            
            for attribute in self.attributes:   #   Commit them to pyglet for display
                attribute.commit ()
            
    def scored (self, playerIndex):             # Player has scored
        self.scoreboard.increment (playerIndex) # Increment player's points
        self.serviceIndex = 1 - playerIndex     # Grant service to the unlucky player
        
        for paddle in self.paddles:             # Put paddles in rest position
            paddle.reset ()
            
        self.ball.reset ()                      # Put ball in rest position
        self.pause = True                       # Wait for next round
        
    def commit (self):
        for attribute in self.attributes:
            attribute.commit ()
        
    def draw (self):
        self.canvas.clear ()
        for attribute in self.attributes:
            attribute.draw ()
             
    def resize (self):
        self.pageWidth = window.innerWidth
        self.pageHeight = window.innerHeight
        
        self.textTop = 0

        if self.pageHeight > 1.2 * self.pageWidth:
            self.canvasHeight = self.pageHeight
            self.canvasTop = self.textTop + self.topMargin
        else:
            self.canvasHeight = 0.7 * self.pageHeight
            self.canvasTop = self.textTop + self.topMargin

        self.canvasWidth = self.aspectRatio * self.canvasHeight
        self.canvasLeft = 0.5 * (self.pageWidth - self.canvasWidth)
        
        self.buttonsTop = self.canvasTop + self.canvasHeight + 50
        self.buttonsWidth = 500
            
        self.textFrame.style.top = self.textTop;
        self.textFrame.style.left = self.canvasLeft + 0.05 * self.canvasWidth
        self.textFrame.style.width = 0.9 * self.canvasWidth
            
        self.canvasFrame.style.top = self.canvasTop
        self.canvasFrame.style.left = self.canvasLeft
        self.canvas.setDimensions ({'width': self.canvasWidth, 'height': self.canvasHeight})
        
        self.buttonsFrame.style.top = self.buttonsTop
        self.buttonsFrame.style.left = 0.5 * (self.pageWidth - self.buttonsWidth)
        self.buttonsFrame.style.width = self.canvasWidth
               
        self.WIDTH = self.canvasWidth
        self.HEIGHT = self.canvasHeight
        
        self.update_cycle_parameters ()
        for n in range (0, len (self.N)):
            self.move_polygon (n)
        
        self.install ()
        self.commit ()
        self.draw ()

    
    def initialize_cycles (self):
                # initialize cycle parameters
        self.T = []
        self.R = []
        self.C = []
        self.omega = []
        
        # initialize main cycle
        n = 0
        self.T.append(self.N[n] * 60 / self.bpm)
        self.R.append(0.28 * min(self.WIDTH, self.HEIGHT))
        self.C.append((self.WIDTH / 2, self.HEIGHT / 2))
        self.omega.append(-2*Math.PI / self.T[n])
        # initialize secondary cycles
        for n in range (1, len (self.N)):
            # polymeter
            if self.mode == 'common beat':
                # initialize cycle parameters
                self.T.append(self.N[n] * 60 / self.bpm)
                self.R.append(self.N[n] / self.N[0] * self.R[0])
                self.omega.append(2*Math.PI / self.T[n] + self.omega[0])
                self.C.append(self.instant_center(n, 0))
            # polyrhythm
            elif self.mode == 'common cycle': 
                # initialize cycle parameters
                self.T.append(self.T[0])
                self.R.append(self.R[0])
                self.omega.append(self.omega[0])
                self.C.append(self.C[0])
        return None
    
    
    def update_cycle_parameters_ (self):
        for n in range (len (self.N)):
            self.T [n] = self.N[n] * 60 / self.bpm
            if n == 0: 
                self.R [n] = 0.28 * min(self.WIDTH, self.HEIGHT)
            else:
                self.R [n] = 0.28 * min(self.WIDTH, self.HEIGHT)
            self.C [n] = (self.WIDTH / 2, self.HEIGHT / 2)
            self.omega [n] = -2*Math.PI / self.T[n]
        return None
    
    def update_cycle_parameters (self):
        n = 0
        self.T[n] = self.N[n] * 60 / self.bpm
        self.R [n] = 0.28 * min(self.WIDTH, self.HEIGHT)
        self.C [n] = (self.WIDTH / 2, self.HEIGHT / 2)
        self.omega [n] = -2*Math.PI / self.T[n]
        for n in range (1, len (self.N)):
            # polymeter
            if self.mode == 'common beat':
                # initialize cycle parameters
                self.T [n] = self.N[n] * 60 / self.bpm
                self.R [n] = self.N[n] / self.N[0] * self.R[0]
                self.omega [n] = 2*Math.PI / self.T[n] + self.omega[0]
                self.C [n] = self.instant_center(n, self.t)
            # polyrhythm
            elif self.mode == 'common cycle': 
                # initialize cycle parameters
                self.T [n] = self.T[0]
                self.R [n] = self.R[0]
                self.omega [n] = self.omega[0]
                self.C [n] = self.C[0]
        return None
    
    def instant_center(self, n, t):
        q = self.instant_angle(self.omega[0], t, self.q0)
        Cn = (self.C[0][0] + (self.R[0] - self.R[n]) * Math.cos(q),
              self.C[0][1] + (self.R[0] - self.R[n]) * Math.sin(q))
        Cn = self.convert_to_frame_coordinates (Cn[0], Cn[1])
        return Cn
    
    def instant_angle(self, omega, t, q0):
        return omega * t + q0
    
    def initialize_main_cycle (self):        
        n = 0
        # initialize cycle parameters
        self.T.append(self.N[n] * 60 / self.bpm)
        self.R.append(0.28 * min(self.WIDTH, self.HEIGHT))
        self.C.append((self.WIDTH / 2, self.HEIGHT / 2))
        self.omega.append(-2*Math.PI / self.T[n])
        
        # initialize TFS size
        self.TFS_radius = self.R[n]/self.R2TFS_ratio
        # initialize RS size
        self.RS_radius = self.R[n]/self.R2RS_ratio
        # initialize main polyon
        self.initialize_polygon(n)
        #self.initialize_sound(n)
        return None
    
    def init_N(self):
        self.N = []
        for voicing in self.voicings:
            self.N.append(len(voicing))
        return None


    ##### POLYGONS #####
    def initialize_polygon(self, n):
        S = []
        for k in range(self.N[n]):
            # calculate vertices positions
            Sk = self.calculate_vertex_k_position(n, k, self.omega[n], 0)
            S.append (Sk)
        self.S.append(S)
        return None
    
    def move_polygon(self, n):
        S = []
        t = 0
        if self.mode == 'common beat' and n != 0:
            t = self.t
        for k in range(self.N[n]):
            # calculate vertices positions
            Sk = self.calculate_vertex_k_position(n, k, self.omega[n], t)
            S.append (Sk)
        self.S[n] = list (S)
        return None    
    
    def pulse_index_in_cycle(self, n):
        N = self.N[n]
        # cycle relative time
        tn = self.t % self.T[n]
        # pulse index in cycle
        jn = 0 | Math.floor (tn * N / self.T[n])
        return tn, jn 
    
    #### SOUND ####
    def beep_ (self, n):
        tn, jn = self.pulse_index_in_cycle(n)
#        sounds = list (self.sounds)
#        sound = *self.sounds [n]
        if n == 0:
            sound = self.sound0
        elif n == 1:
            sound = self.sound1
        elif n == 2:
            sound = self.sound2
        
        if self.irregular:
            if jn > 0 :
                beep_conditions = (tn - self.voicings[n][jn] * self.T[n])  <= self.dt
            else: beep_conditions = False
        else:
                beep_conditions = self.t % (self.T[n] / self.N[n]) <= self.dt
    
        if tn <= self.dt or beep_conditions:
            sound.pause ()
            sound.currentTime = 0
            sound.play ()
# If only 8 channels in mixer
#            if n >= 8:
#                n = 7
#  If volume control
#            if jn == 0: 
#                sound.volume = self.upbeat_volume # !!! to be declared !!!
#                sound.play ()
#            else :
#                sound.play ()
#                sound.volume = self.downbeat_volume
        return None
    
    def get_graphic_parameters(self, graph_params):
        self.background = graph_params['background']
        self.CAMAIEU = graph_params['CAMAIEU']
        self.linecolor = graph_params['linecolor']
        self.R2TFS_ratio = graph_params['R2TFS_ratio']
        self.TFS_fill = graph_params['TFS_fill']
        self.TFS_outline = graph_params['TFS_outline']
        self.R2RS_ration =  graph_params['R2RS_ratio']
        # Vertex1
        self.enlarge = graph_params['enlarge']
        self.Vertex1color = graph_params['Vertex1color']
        self.MainCycleVisible = graph_params['MainCycleVisible']
        self.SecondaryCyclesVisible = graph_params['SecondaryCyclesVisible']
        return None


    def convert_to_frame_coordinates(self, x, y):
        return x, self.HEIGHT - y
    

    def convert_to_relative_coordinates(self, x, y):
        return x, self.HEIGHT - y


    def calculate_vertex_k_position(self, n, k, omega, t):
        center = self.convert_to_relative_coordinates(*self.C[n])
        if not self.irregular:
            beta = 2 * Math.PI / self.N[n]
            Sk = (center[0] + self.R[n] * Math.cos(omega * t + k * beta + self.q0),
                  center[1] + self.R[n] * Math.sin(omega * t + k * beta + self.q0))
        else:
            Sk = (center[0] + self.R[n] * Math.cos(omega * t - self.voicings[n][-k % self.N[n]] * 2 * Math.PI + self.q0),
                  center[1] + self.R[n] * Math.sin(omega * t - self.voicings[n][-k % self.N[n]] * 2 * Math.PI + self.q0))                
        Sk = self.convert_to_frame_coordinates (*Sk)
        return Sk

           
    def display_canvas_position (self):
        # for debug purposes
        text2display  = f'pageWidth = {self.pageWidth:d}\tpageHeight = {self.pageHeight:.0f}\n'
        text2display += f'canvasWidth = {self.canvasWidth:.0f}\tcanvasHeight = {self.canvasHeight:.0f}\n'
        text2display += f'canvasLeft = {self.canvasLeft:.0f}\tcanvasTop = {self.canvasTop:.0f}'
        self.memo.innerHTML = text2display
        return None
    
    
    def scaleX (self, x):
        return x * (self.canvas.width / orthoWidth)
            
    def scaleY (self, y):
        return y * (self.canvas.height / orthoHeight)   
        
    def orthoX (self, x):
        return self.scaleX (x + orthoWidth // 2)
        
    def orthoY (self, y):
        return self.scaleY (orthoHeight - fieldHeight // 2 - y)
                
    def keydown (self, event):
        self.keyCode = event.keyCode
        
    def keyup (self, event):
        self.keyCode = None 

        
def main ():
    bpm = 120
    feel = 0.25
    mode = 'common cycle'
#    mode = 'common beat'
    graph_params = gp.rythmologie
    voicings = [6 , 3]
    game = Game (bpm, voicings, mode, feel, graph_params)
    return None

if __name__ == '__main__':
    main ()
