# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite')  

response.generic_patterns = ['*'] if request.is_local else []


def trans(**texts):
    if T.accepted_language in texts:
        return texts[T.accepted_language]
    else:
        return texts['en'] if 'en' in texts else ''

info_products = dict(
    web2py_plugins= dict(
        label='web2py-plugins',
        description=XML(trans(en="""A collection of plugins of %s, an opensource Python web framework.
Here we love to share useful code parts produced by our development with the framework.
The code parts are organized in %s, and easily available.""", 
                              ja="""オープンソースのPythonウェブ・フレームワーク %s のプラグイン集です。
ここでは、このフレームワークによる開発で生み出された有用なコード部品を共有したいと思います。
コード部品は %s に基づいて整理されいて、簡単に利用可能です。
""") % (
            A('Web2py', _href='http://www.web2py.com').xml(), 
            A(T("a web2py's plugin system"), _href='http://web2py.com/book/default/chapter/13#Plugins').xml())),
        link=URL('web2py_plugins', 'index'),
        link_label=T('See Demo'),
        image='web2py_plugins.jpg',
    ),
    akamon=dict(
        label='AKAMON',
        description=trans(ja="""新感覚CMS製品パッケージです。"""),
        link='http://aka-mon.jp/',
        link_label='紹介ページ',
        image='akamon.gif',
    ),
    ec_orange_cms=dict(
        label='EC-Orange CMS',
        description=trans(ja="""ECサイト特化型CMSです。"""),
        link='http://ec-cube.ec-orange.jp/lineup/cms/',
        link_label='紹介ページ',
        image='ec_orange_cms.gif',
    ),
    ec_orange_pos=dict(
        label='EC-Orange POS',
        description=trans(ja="""ECサイト連動型POSです。"""),
        link='http://ec-cube.ec-orange.jp/lineup/pos/',
        link_label='紹介ページ',
        image='ec_orange_pos.gif',
    ),
    excellent=dict(
        label='Excellent',
        description=trans(ja="""クラウド基盤を活用した大規模サイト構築ソリューションです。
Eコマース、SNS、CMSを中心に豊富な機能を取り揃え、
高負荷な環境下でも高信頼性、ハイパフォーマンスを可能にします。"""),
        link='http://excellent-solution.jp/',
        link_label='紹介ページ',
        image='excellent.png',
    ),
    
    cloudmap=dict(
        label='cloudmap',
        description=XML(T("""Cloudmap is a visual search engine for any contents with user evaluations.""")),
        status='under-construction',
        image='cloudmap.jpg',
    ),
)
