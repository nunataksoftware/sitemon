#!/usr/bin/env python


import sys
import gtk
import appindicator

import imaplib
import re
import urllib


import pynotify
import ConfigParser

PING_FREQUENCY = 10  # seconds


class CheckSite:
    
    config = False

    def __init__(self):
        self.ind = appindicator.Indicator("new-gmail-indicator",
                                          "indicator-messages",
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("ubuntuone-client-error")

        self.menu_setup()
        self.ind.set_menu(self.menu)

        self.read_config()

        pynotify.init("summary-body")

    def read_config(self):
        self.config = ConfigParser.ConfigParser()

        self.config.read('sitemon.ini')

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.configure_item = gtk.MenuItem("Configure")
        self.configure_item.connect("activate", self.configure)
        self.configure_item.show()
        self.menu.append(self.configure_item)

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.check_sites()
        gtk.timeout_add(PING_FREQUENCY * 1000, self.check_sites)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def configure(self, widget):

        self.configure_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.configure_window.set_position(gtk.WIN_POS_CENTER)
        self.configure_window.set_title("SiteMon Configuration")

        self.notebook = gtk.Notebook()

        csections = self.config.sections()


        for site in csections:
            page = gtk.Label(self.config.get(site, 'url'))
            self.notebook.append_page(page, gtk.Label(site))    
            self.notebook.set_tab_reorderable(page, True)

        self.notebook.props.border_width = 10


        fixed = gtk.Fixed()

        
        self.button_save = gtk.Button("Save")
        #self.button_save.connect("clicked", self.destroy)

        self.button_cancel = gtk.Button("Cancel")
        #self.button_cancel.connect("clicked", self.destroy)

        fixed.put(self.button_save, 20, 100)
        fixed.put(self.button_cancel, 80, 100)
        fixed.put(self.notebook, 10, 10)

        self.configure_window.add(fixed)

        self.configure_window.show_all()

    def check_alive(self, site):
        """ Check if a site or page is alive """
        try:
            status = urllib.urlopen(site).getcode()

            if status != 200:
                return {'alive': False, 'message': site + ": Resource not ok: " + str(status)}
            else:
                return {'alive': True, 'message': False}

        except IOError:
            """ Service not found """
            return {'alive': False, 'message': site + ": Site or service not found"}

    def check_sites(self):
        """ Reads the .ini file and checks all sites in it """

        csections = self.config.sections()

        for site in csections:
            #print self.config.get(site, 'CheckAlive')

            if self.config.get(site, 'CheckAlive') == 'yes':

                print "checking " + site

                site_status = self.check_alive(self.config.get(site, 'url'))

                if site_status['alive']:
                    self.ind.set_status(appindicator.STATUS_ACTIVE)
                else:
                    self.ind.set_status(appindicator.STATUS_ATTENTION)
                    if site_status['message']:
                        n = pynotify.Notification("Error",
                                                  site_status['message'])
                        n.show()

        return True

if __name__ == "__main__":
    indicator = CheckSite()
    indicator.main()
