import os, sys
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class urlDownloader(object):
    """ Download the webpage components base on the input url."""
    def __init__(self, imgFlg=True, linkFlg=True, scriptFlg=True):
        self.soup = None
        self.imgFlg = imgFlg
        self.linkFlg = linkFlg
        self.scriptFlg = scriptFlg
        self.linkType = ('css', 'png', 'ico', 'jpg', 'jpeg', 'mov', 'ogg', 'gif', 'xml','js')
        self.session = requests.Session()
        
    #-----------------------------------------------------------------------------
    def savePage(self, url, pagefolder='page'):
        """ Save the web page components based on the input url and dir name.
        Args:
            url ([try]): web url string.
            pagefolder (str, optional): path to save the web components.
        Returns:
            [bool]: whether the components saved the successfully.
        """
        try:
            response = self.session.get(url)
            self.soup = BeautifulSoup(response.text, features="lxml")
            if not os.path.exists(pagefolder): os.mkdir(pagefolder)
            if self.imgFlg: self._soupfindnSave(url, pagefolder, tag2find='img', inner='src')
            if self.linkFlg: self._soupfindnSave(url, pagefolder, tag2find='link', inner='href')
            if self.scriptFlg: self._soupfindnSave(url, pagefolder, tag2find='script', inner='src')
            with open(os.path.join(pagefolder, 'page.html'), 'wb') as file:
                file.write(self.soup.prettify('utf-8'))
            return True
        except Exception as e:
            print("> savePage(): Create files failed: %s." % str(e))
            return False

    #-----------------------------------------------------------------------------
    def _soupfindnSave(self, url, pagefolder, tag2find='img', inner='src'):
        """ Saves on specified pagefolder all tag2find objects. """
        pagefolder = os.path.join(pagefolder, tag2find)
        if not os.path.exists(pagefolder): os.mkdir(pagefolder)
        for res in self.soup.findAll(tag2find):   # images, css, etc..
            try:
                if not res.has_attr(inner): continue # check if inner tag (file object) exists
                # clean special chars such as '@, # ? <>'
                filename = re.sub('\W+', '.', os.path.basename(res[inner]))
                # print("> filename:", filename)
                # Added the '.html' for the html file in the href
                if tag2find == 'link' and (not any(ext in filename for ext in self.linkType)):
                    filename += '.html'
                fileurl = urljoin(url, res.get(inner))
                filepath = os.path.join(pagefolder, filename)
                # rename html ref so can move html and folder of files anywhere
                res[inner] = os.path.join(os.path.basename(pagefolder), filename)
                # create the file.
                if not os.path.isfile(filepath):
                    with open(filepath, 'wb') as file:
                        filebin = self.session.get(fileurl)
                        if len(filebin.content) > 0: # filter the empty file(imge not found)
                            file.write(filebin.content)
            except Exception as exc:
                print(exc, file=sys.stderr)

