import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys


class MyWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Scale Example", application=app)
        self.set_default_size(400, 300)
        self.set_border_width(5)

        ad1 = Gtk.Adjustment(value = 0, lower = 0, upper = 100, step_increment = 5, page_increment = 10, page_size = 0)
        self.h_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad1)
        self.h_scale.set_digits(0)
        self.h_scale.set_hexpand(True)
        self.h_scale.set_valign(Gtk.Align.START)
        self.h_scale.connect("value-changed", self.scale_moved)
        self.label = Gtk.Label()
        self.label.set_text("Move the scale handles...")
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_column_homogeneous(True)
        grid.attach(self.h_scale, 0, 0, 2, 1)
        grid.attach(self.label, 0, 1, 2, 1)

        self.add(grid)

    # any signal from the scales is signaled to the label the text of which is
    # changed
    def scale_moved(self, event):
        self.label.set_text("Horizontal scale is " + str(int(self.h_scale.get_value())) + ".")
                            #"; vertical scale is " + str(self.v_scale.get_value()) + ".")


class MyApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MyWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
