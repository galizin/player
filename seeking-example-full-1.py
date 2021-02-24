
#!/usr/bin/env python

import os, _thread, time
import gi
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gst, GObject, Gtk, Gdk, GLib

class GTK_Main:
      
    def __init__(self):
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("Player")
        window.set_default_size(500, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.entry = Gtk.Entry()
        self.entry.set_text("/home/userx/tlc.flac")
        vbox.pack_start(self.entry, False, False, 0)
        hbox = Gtk.HBox()
        hbox2 = Gtk.HBox()
        vbox.add(hbox2)
        vbox.add(hbox)
        ad1 = Gtk.Adjustment(value = 0, lower = 0, upper = 100, step_increment = 5, page_increment = 10, page_size = 0)
        self.h_scale = Gtk.Scale(
          orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.h_scale.set_digits(0)
        self.h_scale.set_draw_value(False)
        self.h_scale.set_hexpand(True)
        self.h_scale.set_valign(Gtk.Align.START)
        #self.h_scale.connect("value-changed", self.scale_moved)
        self.h_scale.set_sensitive(False)
        hbox2.add(self.h_scale)
        buttonbox = Gtk.HButtonBox()
        hbox.pack_start(buttonbox, False, False, 0)
        rewind_button = Gtk.Button(label="Rewind")
        rewind_button.connect("clicked", self.rewind_callback)
        buttonbox.add(rewind_button)
        self.button = Gtk.Button(label="Start")
        self.button.connect("clicked", self.start_stop)
        buttonbox.add(self.button)
        forward_button = Gtk.Button(label="Forward")
        forward_button.connect("clicked", self.forward_callback)
        buttonbox.add(forward_button)
        self.time_label = Gtk.Label()
        self.time_label.set_text("00:00 / 00:00")
        hbox.add(self.time_label)
        window.show_all()
        
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        #self.player = Gst.Pipeline.new("player")
        #source = Gst.ElementFactory.make("filesrc", "file-source")
        #demuxer = Gst.ElementFactory.make("oggdemux", "demuxer")
        #demuxer.connect("pad-added", self.demuxer_callback)
        #self.audio_decoder = Gst.ElementFactory.make("vorbisdec", "vorbis-decoder")
        #audioconv = Gst.ElementFactory.make("audioconvert", "converter")
        #audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        
        #for ele in [source, demuxer, self.audio_decoder, audioconv, audiosink]:
        #   self.player.add(ele)
        #source.link(demuxer)
        #self.audio_decoder.link(audioconv)
        #audioconv.link(audiosink)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
    def start_stop(self, w):
        if self.button.get_label() == "Start":
            filepath = self.entry.get_text().strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.button.set_label("Stop")
                #self.player.get_by_name("file-source").set_property("location", filepath)
                self.player.set_property("uri", "file://" + filepath)
                self.player.set_state(Gst.State.PLAYING)
                self.play_thread_id = _thread.start_new_thread(self.play_thread, ())
        else:
            self.play_thread_id = None
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            self.time_label.set_text("00:00 / 00:00")

    def change_label(self, newtext):
        self.time_label.set_text(newtext)

    def player_query(self, _player, type):
        if type == 'dur':
          return _player.query_duration(Gst.Format.TIME)[1]
        else:
          return _player.query_position(Gst.Format.TIME)[1]

    def play_thread(self):
        #play_thread_id = self.play_thread_id
        #Gdk.threads_enter()
        self.time_label.set_text("00:00 / 00:00")
        #print("00:00 / 00:00")
        #Gdk.threads_leave()
        #GLib.idle_add(self.change_label, "00:00 / 00:00")
        
        #while play_thread_id == self.play_thread_id:
        while 1==1:
          #try:
              time.sleep(0.2)
              dur_int = self.player_query(self.player, 'dur')
              #dur_int = self.player.query_duration(Gst.Format.TIME)[0]
              if dur_int == -1:
                  print("duration not detected")
                  continue
              #print(dur_int)
              dur_str = self.convert_ns(dur_int)
              #Gdk.threads_enter()
              self.time_label.set_text("00:00 / " + dur_str)
              #print("00:00 / " + dur_str)
              #Gdk.threads_leave()
              #GLib.idle_add(self.change_label, "00:00 / " + dur_str)
              break
          #except:
              #pass
                
        time.sleep(0.2)
        while self.play_thread_id != None:
        #while play_thread_id == self.play_thread_id:
          pos_int = self.player_query(self.player, 'pos')
          #pos_int = self.player.query_position(Gst.Format.TIME, None)[0]
          #print(pos_int)
          pos_str = self.convert_ns(pos_int)
          #if play_thread_id == self.play_thread_id:
              #Gdk.threads_enter()
          self.time_label.set_text(pos_str + " / " + dur_str)
          #print(pos_str + " / " + dur_str)
              #Gdk.threads_leave()
              #GLib.idle_add(self.change_label, pos_str + " / " + dur_str)
          time.sleep(1)
                
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.play_thread_id = None
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            self.time_label.set_text("00:00 / 00:00")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.play_thread_id = None
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            self.time_label.set_text("00:00 / 00:00")
            
    def demuxer_callback(self, demuxer, pad):
        adec_pad = self.audio_decoder.get_static_pad("sink")
        pad.link(adec_pad)
        
    def rewind_callback(self, w):
        rc, pos_int = self.player.query_position(Gst.Format.TIME)
        seek_ns = pos_int - 10 * 1000000000
        if seek_ns < 0:
            seek_ns = 0
        print('Backward: %d ns -> %d ns' % (pos_int, seek_ns))
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)
        
    def forward_callback(self, w):
        rc, pos_int = self.player.query_position(Gst.Format.TIME)
        seek_ns = pos_int + 10 * 1000000000
        print('Forward: %d ns -> %d ns' % (pos_int, seek_ns))
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)
        
    def convert_ns(self, t):
        # This method was submitted by Sam Mason.
        # It's much shorter than the original one.
        s,ns = divmod(t, 1000000000)
        m,s = divmod(s, 60)
        
        if m < 60:
            return "%02i:%02i" %(m,s)
        else:
            h,m = divmod(m, 60)
            return "%i:%02i:%02i" %(h,m,s)
            
#GObject.threads_init()
Gst.init(None)        
GTK_Main()
Gtk.main()
