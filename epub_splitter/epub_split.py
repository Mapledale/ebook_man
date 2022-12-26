#!/usr/bin/env python3
# _*_ encoding: utf-8 _*_

from distutils.dir_util import copy_tree
import fileinput
import os
import shutil
import xml.etree.ElementTree as ET
from zipfile import ZipFile


PATH_BASE = os.path.dirname(__file__)
# BOOK_FNAME = 'Tom Clancy军事系列（共9册）.epub'
# BOOK_FNAME = '解密东欧：苦难与辉煌（共4册）.epub'
# BOOK_FNAME = '大家小书：大中国古典·诗词集萃（共16册）.epub'
# BOOK_FNAME = '哈耶克大全集.epub'
BOOK_FNAME = '26部欧美人文经典.epub'
SER_TITLE = '26部欧美人文经典'  # series title
PATH_TXT = 'text'  # rel path of the folder of text files
PATH_IMG = 'images'  # rel path of the folder of image files
CONT = 'content.opf'  # content file name
TOC = 'toc.ncx'  # root TOC file name
# AUTHORS = {
#     '好诗不厌百回读': '袁行霈',
#     '闲坐说诗经': '金性尧',
#     '舒芜说诗': '舒芜',
#     '唐人绝句启蒙': '李霁野',
#     '词学十讲': '龙榆生',
#     '唐宋词欣赏': '夏承焘',
#     '唐五代词境浅说': '俞陛云',
#     '诗境浅说': '俞陛云',
#     '诗论': '朱光潜',
#     '唐诗杂论': '闻一多',
#     '中国古典诗歌讲稿': '浦江清',
#     '词曲概论': '龙榆生',
#     '唐宋词启蒙': '李霁野',
#     '北宋词境浅说': '俞陛云',
#     '南宋词境浅说': '俞陛云',
#     '唐诗纵横谈': '周勋初'
# }
AUTHORS = {
    '理想国': 'Plato',
    '查拉图斯特拉如是说': 'Friedrich Nietzsche',
    '悲剧的诞生': 'Friedrich Nietzsche',
    '论美国的民主': 'Alexis de Tocqueville',
    '论人类不平等的起源和基础': 'Jean-Jacques Rousseau',
    '菊与刀': 'Ruth Benedict',
    '国富论': 'Adam Smith',
    '富兰克林自传': 'Benjamin Franklin',
    '人性的弱点': 'Dale Carnegie',
    '论自由': 'John Stuart Mill',
    '宽容': 'Hendrik Willem van Loon',
    '思想录': 'Blaise Pascal',
    '战争论': 'Carl von Clausewitz',
    '物种起源': 'Charles Darwin',
    '审美教育书简': 'Friedrich Schiller',
    '论道德原理·论人类理智': 'David Hume',
    '道德情操论': 'Adam Smith',
    '愚人颂': 'Erasmus',
    '方法论·情志论': 'René Descartes',
    '物性论': 'Lucretius',
    '论共和国': 'Cicero',
    '自然史': 'Buffon',
    '西绪福斯神话': 'Albert Camus',
    '孤独漫步者的遐想': 'Jean-Jacques Rousseau',
    '人生的意义与价值': 'Rudolf Christoph Eucken',
    '社会契约论': 'Jean-Jacques Rousseau'
}


class EpubBook(object):
    """ The class for e-books in epub format

    This class has attributes describing the ebook instance. Example:
    self.fname_full: <full path>\\Tom Clancy军事系列（共9册）.epub
    self.path: <full path>
    self.fname: Tom Clancy军事系列（共9册）
    self.fname_ext: .epub
    self.title: ''
    self.author: ''
    self.file_cont = 'content.opf'
    self.file_toc = 'toc.ncx'
    self.path_img: Tom Clancy军事系列（共9册）\\images
    self.files_img: ['00001.jpeg',]
    self.file_img_cover: 00029.jpeg
    self.path_txt: Tom Clancy军事系列（共9册）\\text
    self.files_txt: ['part0000.html',]
    self.file_txt_toc: part0001.html
    """
    def __init__(self, fname_full):
        self.fname_full = fname_full
        self.path, file_name = os.path.split(fname_full)
        self.fname, self.fname_ext = os.path.splitext(file_name)
        self.title = ''
        self.author = ''
        self.file_cont = CONT  # name of the content file
        self.file_toc = TOC  # name of the root TOC file
        self.path_img = os.path.join(self.fname, PATH_IMG)
        self.files_img = []
        self.file_img_cover = ''  # filename of cover img
        self.path_txt = os.path.join(self.fname, PATH_TXT)
        self.files_txt = []
        self.file_txt_toc = ''  # the toc file in the text folder
        if self.path:
            os.chdir(self.path)

    def unzip_book(self):
        fname_zip = self.fname + '.zip'
        shutil.copy2(self.fname + self.fname_ext, fname_zip)
        os.makedirs(self.fname)
        with ZipFile(fname_zip) as f:
            f.extractall(self.fname)
        os.remove(fname_zip)

    def __get_file_img_cover(self):
        """ read content file to update self.file_img_cover """
        os.chdir(self.fname)
        tree = ET.parse(self.file_cont)
        root = tree.getroot()

        # update namespace
        ns = {'dft': ''}
        if root.tag.startswith('{'):
            ns['dft'] = root.tag.split('}')[0].strip('{')

        root_manifest = root.find('dft:manifest', ns)
        root_manifest_items = root_manifest.findall('dft:item', ns)
        for item in root_manifest_items:
            id = item.get('id')
            mtype = item.get('media-type')
            if id == 'cover' and mtype == 'image/jpeg':
                self.file_img_cover = item.get('href').split('/')[1]
                break

        os.chdir(self.path)

    def get_book_info(self):
        """ update book info, including:
        self.files_img,
        self.files_txt,
        self.file_txt_toc,
        self.file_img_cover (by calling __get_file_img_cover())
        """
        self.__get_file_img_cover()

        for f in os.listdir(self.path_img):
            self.files_img.append(f)
        for f in os.listdir(self.path_txt):
            self.files_txt.append(f)

        # find the toc file in the text folder
        brk = False
        for fn in self.files_txt:
            target = os.path.join(self.path_txt, fn)
            with open(target, 'r') as f:
                fc = f.readlines()
                for line in fc:
                    if '总 目 录' in line or '总目录' in line \
                            or '目  录' in line or '目录' in line:
                        self.file_txt_toc = fn
                        brk = True
                        break
            if brk:
                break

    def write_book_info(self, fname):
        with open(fname, 'a+') as f:
            f.write()


class EpubBundle(EpubBook):
    """ The special type of epub book that has multiple epub books bundled

    self.subbooks is a list of subbooks, which have following keys:
    'title', 'author', 'ser_idx',
    'file_img_top', 'file_img_top_idx'
    'file_img_end', 'files_img_num'
    'file_txt_top', 'file_txt_top_idx'
    'file_txt_end', 'files_txt_num'

    A subbook example:
    {'title': '冷血悍将',
     'author': '周勋初',
     'ser_idx': '01',
     'file_img_top': '00017.jpeg',
     'file_img_top_idx': 16,
     'file_img_end': '00019.jpeg',
     'files_img_num': 3,
     'file_txt_top': 'part0186.html',
     'file_txt_top_idx': 186,
     'file_txt_end': 'part0234.html',
     'files_txt_num': 49}

     self.comm_items is a list of common items, which have following keys:
     'title', 'file_txt_top'

     A comm_items example:
     [{'file_txt_top': 'part0000.html', 'title': '版权信息'},
      {'file_txt_top': 'part0001.html', 'title': '总目录'}]
    """
    def __init__(self, fname_full, ser_title):
        super().__init__(fname_full)
        self.title = ser_title
        self.subbooks = []
        # self.comm_items = []  # common items, e.g. '版权信息', '总目录'
        self.comm_items = [{'file_txt_top': 'part0000.html', 'title': '目录'}]
        self.files_txt_comm_num = 0  # number of text files for common items
        self.files_img_cover_num = 1  # for self.file_img_cover

    def __parse_toc_ncx(self, fname='toc.ncx'):
        os.chdir(self.fname)

        tree = ET.parse(fname)
        root = tree.getroot()

        ns = {'dft': ''}
        if root.tag.startswith('{'):
            ns['dft'] = root.tag.split('}')[0].strip('{')

        root_navMap = root.find('dft:navMap', ns)
        root_navMap_navPoints = root_navMap.findall('dft:navPoint', ns)
        for navPoint in root_navMap_navPoints:
            item = {}

            navPoint_content = navPoint.find('dft:content', ns)
            src = navPoint_content.get('src')
            item['file_txt_top'] = src.split('#')[0].rsplit('/', 1)[1]

            navPoint_navLabel = navPoint.find('dft:navLabel', ns)
            navPoint_navLabel_text = navPoint_navLabel.find('dft:text', ns)
            item['title'] = navPoint_navLabel_text.text

            # if item['title'] in ['版权信息', '总目录']:
            if item['title'] in ['扉页', '目录']:
                self.comm_items.append(item)
            else:
                self.subbooks.append(item)

        os.chdir(self.path)

    def __get_subbook_img_top(self):
        for book in self.subbooks:
            target = os.path.join(self.path_txt, book['file_txt_top'])
            with open(target, 'r') as f:
                fc = f.readlines()  # file content
                for _l in fc:
                    if 'jpeg' in _l:
                        book['file_img_top'] = \
                            _l.split('src="')[1].split('"', 1)[0].\
                            rsplit('/', 1)[1]

    def __get_subbook_end(self):
        """ get subbook info for both image and text files.

        The info includes:
        'file_img_top_idx', 'file_img_end', 'files_img_num'
        'file_txt_top_idx', 'file_txt_end', 'files_txt_num'
        """
        self.subbooks[0]['file_img_top_idx'] = self.files_img.index(
            self.subbooks[0]['file_img_top'])
        self.subbooks[0]['file_txt_top_idx'] = self.files_txt.index(
            self.subbooks[0]['file_txt_top'])

        for idx in range(len(self.subbooks) - 1):
            book_curr = self.subbooks[idx]
            book_next = self.subbooks[idx + 1]

            book_next['file_img_top_idx'] = self.files_img.index(
                book_next['file_img_top'])
            book_next['file_txt_top_idx'] = self.files_txt.index(
                book_next['file_txt_top'])

            book_curr['file_img_end'] = self.files_img[
                book_next['file_img_top_idx'] - 1]
            book_curr['files_img_num'] = book_next['file_img_top_idx'] - \
                book_curr['file_img_top_idx']

            book_curr['file_txt_end'] = self.files_txt[
                book_next['file_txt_top_idx'] - 1]
            book_curr['files_txt_num'] = book_next['file_txt_top_idx'] - \
                book_curr['file_txt_top_idx']

        self.subbooks[-1]['file_img_end'] = self.files_img[-2]
        # the last img is for bundle cover
        self.subbooks[-1]['files_img_num'] = len(self.files_img) - 1 - \
            self.subbooks[-1]['file_img_top_idx']

        self.subbooks[-1]['file_txt_end'] = self.files_txt[-1]
        self.subbooks[-1]['files_txt_num'] = len(self.files_txt) - \
            self.subbooks[-1]['file_txt_top_idx']

    def __get_files_txt_comm_num(self):
        idx_top = self.files_txt.index(self.comm_items[0]['file_txt_top'])
        idx_end = self.files_txt.index(self.subbooks[0]['file_txt_top'])
        self.files_txt_comm_num = idx_end - idx_top

    def get_subbook_info(self):
        self.__parse_toc_ncx()
        self.__get_subbook_img_top()
        self.__get_subbook_end()

        self.__get_files_txt_comm_num()
        tot_img = 0
        tot_txt = 0
        for book in self.subbooks:
            book['author'] = AUTHORS[book['title']]
            idx = list(AUTHORS.keys()).index(book['title'])
            book['ser_idx'] = '{:02}'.format(idx + 1)
            tot_img += book['files_img_num']
            tot_txt += book['files_txt_num']
        assert tot_img + self.files_img_cover_num == len(self.files_img)
        assert tot_txt + self.files_txt_comm_num == len(self.files_txt)

    def __parse_and_get_ns(self, file):
        events = "start", "start-ns"
        root = None
        ns = {}
        for event, elem in ET.iterparse(file, events):
            if event == "start-ns":
                if elem[0] in ns and ns[elem[0]] != elem[1]:
                    # NOTE: It is perfectly valid to have the same prefix refer
                    # to different URI namespaces in different parts of the
                    # document. This exception serves as a reminder that this
                    # solution is not robust. Use at your own peril.
                    raise KeyError("Same prefix with different URI found.")
                # ns[elem[0]] = "{%s}" % elem[1]
                ns[elem[0]] = elem[1]
            elif event == "start":
                if root is None:
                    root = elem
        return ns

    def __create_file_txt_toc(self, path_book):
        path_work, title = os.path.split(path_book)
        fname_ori = os.path.join(self.fname, PATH_TXT, self.file_txt_toc)
        fname_new = os.path.join(path_book, PATH_TXT, self.file_txt_toc)

        tree = ET.parse(fname_ori)
        root = tree.getroot()

        ns = self.__parse_and_get_ns(fname_ori)
        ns['dft'] = ns['']

        root_body = root.find('dft:body', ns)
        root_body_ps = root_body.findall('dft:p', ns)
        for p in root_body_ps:
            p_a = p.find('dft:a', ns)
            if p_a.text != title:
                # delete attrib 'href'
                del p_a.attrib['href']

        ET.register_namespace("", ns['dft'])
        tree.write(fname_new, encoding='utf-8', xml_declaration=True)

    def __create_subbook_cont(self, path_book, author_new, ser_idx):
        path_work, title_new = os.path.split(path_book)
        path_img = os.path.join(path_book, PATH_IMG)
        path_txt = os.path.join(path_book, PATH_TXT)

        fname_ori = os.path.join(self.fname, CONT)
        fname_new = os.path.join(path_book, CONT)

        tree = ET.parse(fname_ori)
        root = tree.getroot()

        ns = self.__parse_and_get_ns(fname_ori)
        ns['dft'] = ns['']

        # the metadata part
        root_metadata = root.find('dft:metadata', ns)

        # to overwrite the text for root_metadata_title
        root_metadata_title = root_metadata.find('dc:title', ns)
        root_metadata_title.text = title_new

        # to overwrite the text for root_metadata_creator
        root_metadata_creators = root_metadata.findall('dc:creator', ns)
        key = '{%s}file-as' % ns['opf']
        for cre in root_metadata_creators:
            if cre.text == author_new:
                cre.set(key, author_new)
            else:
                root_metadata.remove(cre)

        # to add <meta name="calibre:series", <meta name="calibre:series_index"
        root_metadata_ser = ET.SubElement(root_metadata, 'meta')
        root_metadata_ser.set('name', 'calibre:series')
        root_metadata_ser.set('content', self.title)

        root_metadata_ser = ET.SubElement(root_metadata, 'meta')
        root_metadata_ser.set('name', 'calibre:series_index')
        root_metadata_ser.set('content', ser_idx)

        # the manifest part
        keep_list_img = os.listdir(path_img)
        keep_list_txt = os.listdir(path_txt)
        keep_list_id = ['titlepage']
        root_manifest = root.find('dft:manifest', ns)
        root_manifest_items = root_manifest.findall('dft:item', ns)
        for item in root_manifest_items:
            href = item.get('href')
            if href.startswith('images'):
                fn = href.split('/', 1)[1]
                if fn not in keep_list_img:
                    root_manifest.remove(item)
            elif href.startswith('text'):
                fn = href.split('/', 1)[1]
                if fn not in keep_list_txt:
                    root_manifest.remove(item)
                else:
                    keep_list_id.append(item.get('id'))
            else:
                continue

        # the spine part
        root_spine = root.find('dft:spine', ns)
        root_spine_itemrefs = root_spine.findall('dft:itemref', ns)
        for item in root_spine_itemrefs:
            if item.get('idref') not in keep_list_id:
                root_spine.remove(item)

        # the guide part
        # root_guide = root.find('dft:guide', ns)
        # root_guide_refs = root_guide.findall('dft:reference', ns)
        # for ref in root_guide_refs:
        #     if ref.get('title') not in ['Cover', '目录']:
        #         ref.set('title', title_new)

        ET.register_namespace("", ns['dft'])
        tree.write(fname_new, encoding='utf-8', xml_declaration=True)

    def __create_subbook_toc(self, path_book):
        path_work, title_new = os.path.split(path_book)
        fname_ori = os.path.join(self.fname, TOC)
        fname_new = os.path.join(path_book, TOC)

        tree = ET.parse(fname_ori)
        root = tree.getroot()

        ns = {'dft': ''}
        if root.tag.startswith('{'):
            ns['dft'] = root.tag.split('}')[0].strip('{')

        # to update root_docTitle_text with title_new
        root_docTitle = root.find('dft:docTitle', ns)
        root_docTitle_text = root_docTitle.find('dft:text', ns)
        root_docTitle_text.text = title_new

        # the navMap part
        root_navMap = root.find('dft:navMap', ns)
        root_navMap_navPoints = root_navMap.findall('dft:navPoint', ns)
        for navPoint in root_navMap_navPoints:
            # keep_list = ['版权信息', '总目录', title_new]
            # keep_list = ['扉页', '目录', title_new]
            keep_list = [title_new]

            navPoint_navLabel = navPoint.find('dft:navLabel', ns)
            navPoint_navLabel_text = navPoint_navLabel.find('dft:text', ns)

            # to remove any navPoint other than booktitle
            if navPoint_navLabel_text.text not in keep_list:
                root_navMap.remove(navPoint)

        ET.register_namespace("", ns['dft'])
        tree.write(fname_new, encoding='utf-8', xml_declaration=True)

        with fileinput.FileInput(fname_new, inplace=True) as f:
            for line in f:
                print(line.replace('    </navMap>', '  </navMap>'), end='')

    def create_subbook(self):
        path_work = 'working'
        os.mkdir(path_work)
        for book in self.subbooks:
            path_book = os.path.join(path_work, book['title'])
            path_book_img = os.path.join(path_book, PATH_IMG)
            path_book_txt = os.path.join(path_book, PATH_TXT)
            # create book folder, and sub-folders: images, text
            os.mkdir(path_book)
            while True:
                if os.path.exists(path_book):
                    os.mkdir(path_book_img)
                    os.mkdir(path_book_txt)
                    break

            # copy img files of each book, plus the bundle cover img
            src_cover = os.path.join(self.path_img, self.file_img_cover)
            dst_cover = os.path.join(path_book_img, self.file_img_cover)
            shutil.copy2(src_cover, dst_cover)

            for i in range(book['files_img_num']):
                idx = book['file_img_top_idx'] + i
                src_img = os.path.join(self.path_img, self.files_img[idx])
                dst_img = os.path.join(path_book_img, self.files_img[idx])
                shutil.copy2(src_img, dst_img)

            num_img = len(os.listdir(path_book_img))
            assert num_img == book['files_img_num'] + self.files_img_cover_num

            # copy txt files of each book, plus the commom txt files
            for i in range(book['files_txt_num']):
                idx = book['file_txt_top_idx'] + i
                src_txt = os.path.join(self.path_txt, self.files_txt[idx])
                dst_txt = os.path.join(path_book_txt, self.files_txt[idx])
                shutil.copy2(src_txt, dst_txt)

            for item in self.comm_items:
                if item['file_txt_top'] == self.file_txt_toc:
                    self.__create_file_txt_toc(path_book)
                else:
                    src_txt = os.path.join(self.path_txt, item['file_txt_top'])
                    dst_txt = os.path.join(path_book_txt, item['file_txt_top'])
                    shutil.copy2(src_txt, dst_txt)

            num_txt = len(os.listdir(path_book_txt))
            assert num_txt == book['files_txt_num'] + self.files_txt_comm_num

            # copy META-INF from bundle book to subbook
            src = os.path.join(self.fname, 'META-INF')
            dst = os.path.join(path_book, 'META-INF')
            copy_tree(src, dst)

            # copy all files from bundle book to subbook
            files = [f for f in os.listdir(self.fname) if os.path.isfile(
                os.path.join(self.fname, f))]
            for f in files:
                if f in ['toc.ncx', 'content.opf']:
                    continue
                src = os.path.join(self.fname, f)
                dst = os.path.join(path_book, f)
                shutil.copy2(src, dst)

            # modify content.opf
            self.__create_subbook_cont(
                path_book, book['author'], book['ser_idx'])

            # modify toc.ncx
            self.__create_subbook_toc(path_book)

            # create zip file, copy to epub file, remove zip file
            os.chdir(path_work)
            shutil.make_archive(book['title'], 'zip', book['title'])
            shutil.copy2('{0}.zip'.format(book['title']), '{0} - {1}.epub'.
                         format(book['author'], book['title']))
            os.remove('{0}.zip'.format(book['title']))
            os.chdir(self.path)


def main():
    my_book = EpubBundle(os.path.join(PATH_BASE, BOOK_FNAME), SER_TITLE)
    # my_book.unzip_book()
    my_book.get_book_info()
    my_book.get_subbook_info()
    my_book.create_subbook()


if __name__ == '__main__':
    main()
