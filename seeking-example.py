
#!/usr/bin/env python

import os, _thread, time
import gi
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gst, GObject, Gtk, Gdk, GLib

class GTK_Main:
      
    def __init__(self):
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Player")
        self.window.set_default_size(500, -1)
        self.window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        self.window.add(vbox)
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
        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", self.on_file_clicked)
        buttonbox.add(open_button)
        self.time_label = Gtk.Label()
        self.time_label.set_text("00:00 / 00:00")
        hbox.add(self.time_label)
        self.window.show_all()
        
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="File selector", parent=self.window, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        #self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry.set_text(dialog.get_filename())
            #print("Open clicked")
            #print("File selected: " + dialog.get_filename())
        #elif response == Gtk.ResponseType.CANCEL:
            #print("Cancel clicked")

        dialog.destroy()

        
    def start_stop(self, w):
        if self.button.get_label() == "Start":
            filepath = self.entry.get_text().strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.button.set_label("Stop")
                self.player.set_property("uri", "file://" + filepath)
                self.player.set_state(Gst.State.PLAYING)
                self.play_thread_id = _thread.start_new_thread(self.play_thread, ())
        else:
            self.play_thread_id = None
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            self.time_label.set_text("00:00 / 00:00")
            self.h_scale.set_value(0)

    def change_label(self, newtext):
        self.time_label.set_text(newtext)

    def player_query(self, _player, type):
        if type == 'dur':
          return _player.query_duration(Gst.Format.TIME)[1]
        else:
          return _player.query_position(Gst.Format.TIME)[1]

    def play_thread(self):
        self.time_label.set_text("00:00 / 00:00")
        while 1==1:
              time.sleep(0.2)
              dur_int = self.player_query(self.player, 'dur')
              if dur_int == -1:
                  print("duration not detected")
                  continue
              dur_str = self.convert_ns(dur_int)
              self.time_label.set_text("00:00 / " + dur_str)
              break
                
        time.sleep(0.2)
        while self.play_thread_id != None:
          pos_int = self.player_query(self.player, 'pos')
          pos_str = self.convert_ns(pos_int)
          self.time_label.set_text(pos_str + " / " + dur_str)
          if dur_int != 0:
            self.h_scale.set_value(pos_int * 100 / dur_int)
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
        s,ns = divmod(t, 1000000000)
        m,s = divmod(s, 60)
        
        if m < 60:
            return "%02i:%02i" %(m,s)
        else:
            h,m = divmod(m, 60)
            return "%i:%02i:%02i" %(h,m,s)
            
Gst.init(None)        
GTK_Main()
Gtk.main()
