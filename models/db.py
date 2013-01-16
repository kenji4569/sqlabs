# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite')

response.generic_patterns = ['*'] if request.is_local else []


def trans(**texts):
    if T.accepted_language in texts:
        return texts[T.accepted_language]
    else:
        return texts['en'] if 'en' in texts else ''

info_products = dict(
    web2py_plugins=dict(
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
    github=dict(
        label='github/scubism',
        description=trans(ja="""scubismの公式githubアカウントのページです。社内で作成したライブラリなどを公開しています。""",
                          en="""The official github account page of s-cubism."""),
        link='https://github.com/scubism',
        link_label=T('See Page'),
        image='github.png',
    ),
    github_ios=dict(
        label='github/scubism-ios',
        description=trans(ja="""ios用のユーティリティライブラリです。""",
                          en="""utility library for ios"""),
        link='https://github.com/scubism-ios',
        link_label=T('See Page'),
        image='github_ios.jpg',
    ),
    github_orangewirt=dict(
        label='github/scubism/OrangeWinRT',
        description=trans(ja="""WinRT/Windowsストアアプリ用のユーティリティライブラリです。""",
                          en="""Utility library for WinRT/Windows Store Applications"""),
        link='https://github.com/scubism/OrangeWinRT',
        link_label=T('See Page'),
        image='github_orangewirt.png',

    ),
    akamon=dict(
        label='AKAMON',
        description=trans(ja="""新感覚CMS製品パッケージです。"""),
        link='http://aka-mon.jp/',
        link_label='紹介ページ',
        image='akamon.gif',
    ),
    ec_orange=dict(
        label='ECOrange',
        description=trans(ja="""国内No.1のシェアを誇るECオープンソースソフトウェア「EC-CUBE」をベースに独自カスタマイズしたECサイト構築パッケージです。"""),
        link='http://ec-cube.ec-orange.jp',
        link_label='紹介ページ',
        image='ec_orange.gif',
    ),
    ec_orange_pos=dict(
        label='ECOrange POS',
        description=trans(ja="""ECサイト連動型POSです。"""),
        link='http://ec-cube.ec-orange.jp/lineup/pos/',
        link_label='紹介ページ',
        image='ec_orange_pos.png',
    ),
    cloudmap=dict(
        label='cloudmap',
        description=XML(T("""Cloudmap is a visual search engine for any contents with user evaluations.""")),
        status='under-construction',
        image='cloudmap.jpg',
    ),
)
